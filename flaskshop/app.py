# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import sys
from dotenv import load_dotenv

from flask import Flask, current_app, render_template, request
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError

from flaskshop import commands
from flaskshop.extensions import (
    babel,
    bcrypt,
    bootstrap,
    csrf_protect,
    db,
    debug_toolbar,
    get_locale,
    login_manager,
    migrate,
)
from flaskshop.plugin import manager, spec
from flaskshop.plugin.models import PluginRegistry
from flaskshop.settings import Config
from flaskshop.utils import jinja_global_varibles, log_slow_queries


def create_app(config_object=Config):
    # author: Wassim Alkhalil
    # Load environment variables from .env file
    load_dotenv()
    
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)
    app.pluggy = manager.FlaskshopPluginManager("flaskshop")
    register_extensions(app)
    load_plugins(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)
    jinja_global_varibles(app)
    log_slow_queries(app)

    return app


# csrf_protect = CSRFProtect()


def register_extensions(app):
    bcrypt.init_app(app)
    db.init_app(app)
    csrf_protect.init_app(app)
    login_manager.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    babel.init_app(app, locale_selector=get_locale)


def register_blueprints(app):
    app.pluggy.hook.flaskshop_load_blueprints(app=app)


def register_errorhandlers(app):
    """Register error handlers."""

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    # CSRF protection script added by Swarup
    # @app.errorhandler(CSRFError)
    # def handle_csrf(e):
    #     current_app.logger.warning(
    #         "CSRF blocked: path=%s remote=%s", request.path, request.remote_addr
    #     )
    #     return ("CSRF token missing or invalid", 400)
    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template(f"errors/{error_code}.html"), error_code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {"db": db}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)
    app.cli.add_command(commands.clean)
    app.cli.add_command(commands.urls)
    app.cli.add_command(commands.createdb)
    app.cli.add_command(commands.seed)
    app.cli.add_command(commands.flushrdb)
    app.cli.add_command(commands.reindex)
    # Migration and db cleaning to quickly test features
    # @author: Nebil Müren - cas3322
    app.cli.add_command(commands.dropdb)
    app.cli.add_command(commands.db_migrate)
    app.cli.add_command(commands.db_upgrade)
    app.cli.add_command(commands.db_downgrade)


def load_plugins(app):
    app.pluggy.add_hookspecs(spec)

    for name, module in sys.modules.items():
        if name.startswith("flaskshop"):
            app.pluggy.register(module)

    app.pluggy.load_setuptools_entrypoints("flaskshop_plugins")
    try:
        with app.app_context():
            for name in app.pluggy.external_plugins:
                plugin, _ = PluginRegistry.get_or_create(name=name)
                if not plugin.enabled:
                    app.pluggy.set_blocked(plugin.name)
    except Exception as e:
        # when db migrate raise exception
        app.logger.error(e)
