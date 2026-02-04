# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""

import logging
from logging.handlers import RotatingFileHandler
from urllib.parse import urlencode

from flask import current_app, flash, request
from flask_babel import gettext
from flask_sqlalchemy.record_queries import get_recorded_queries
from flask_wtf.csrf import generate_csrf

from flaskshop.checkout.models import Cart
from flaskshop.constant import SiteDefaultSettings
from flaskshop.dashboard.models import Setting
from flaskshop.plugin.utils import template_hook
from flaskshop.public.models import MenuItem


# Add time util to prevent repetition
# @author: Nebil Müren - cas3322
def format_duration_seconds(seconds):
    if seconds is None:
        return None

    total_seconds = int(seconds)
    days = total_seconds // 86400
    remaining_after_days = total_seconds % 86400
    hours = remaining_after_days // 3600
    remaining_after_hours = remaining_after_days % 3600
    minutes = remaining_after_hours // 60

    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

    if not parts:
        return "< 1 minute"

    return " ".join(parts)


def flash_errors(form, category="warning"):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text} - {error}", category)


def log_slow_queries(app):
    formatter = logging.Formatter(
        "[%(asctime)s]{%(pathname)s:%(lineno)d}\n%(levelname)s - %(message)s"
    )
    handler = RotatingFileHandler(
        "slow_queries.log", maxBytes=10_000_000, backupCount=10
    )
    handler.setLevel(logging.WARN)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    @app.after_request
    def after_request(response):
        for query in get_recorded_queries():
            if query.duration >= app.config["DATABASE_QUERY_TIMEOUT"]:
                app.logger.warn(
                    f"Context: {query.location}\n"
                    f"SLOW QUERY: {query.statement}\n"
                    f"Parameters: {query.parameters}\n"
                    f"Duration: {query.duration}"
                )
        return response


def jinja_global_varibles(app):
    """Register global varibles for jinja2"""

    @app.context_processor
    def inject_cart():
        current_user_cart = Cart.get_current_user_cart()
        return dict(current_user_cart=current_user_cart)

    @app.context_processor
    def inject_menus():
        top_menu = (
            MenuItem.query.filter(MenuItem.position == 1)
            .filter(MenuItem.parent_id == 0)
            .order_by(MenuItem.order)
            .all()
        )
        bottom_menu = (
            MenuItem.query.filter(MenuItem.position == 2)
            .filter(MenuItem.parent_id == 0)
            .order_by(MenuItem.order)
            .all()
        )
        return dict(top_menu=top_menu, bottom_menu=bottom_menu)

    @app.context_processor
    def inject_site_setting():
        settings = {}
        for key, value in SiteDefaultSettings.items():
            obj = Setting.query.filter_by(key=key).first()
            if not obj:
                obj = Setting.create(key=key, **value)
            settings[key] = obj
        return dict(settings=settings)

    def get_sort_by_url(field, descending=False):
        request_get = request.args.copy()
        if descending:
            request_get["sort_by"] = "-" + field
        else:
            request_get["sort_by"] = field
        return f"{request.path}?{urlencode(request_get)}"

    app.add_template_global(current_app, "current_app")
    # author: Wassim Alkhalil
    app.add_template_global(gettext, "gettext")
    app.add_template_global(get_sort_by_url, "get_sort_by_url")
    app.add_template_global(template_hook, "run_hook")
    app.add_template_global(generate_csrf, "csrf_token")
    app.add_template_filter(format_duration_seconds, "format_duration")
