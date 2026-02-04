# -*- coding: utf-8 -*-
"""Test configs."""
from flaskshop.app import create_app
from flaskshop.settings import Config, ProdConfig


def test_production_config():
    """Production config."""
    app = create_app(ProdConfig)
    assert app.config["ENV"] == "prod"# nosec
    assert app.config["FLASK_DEBUG"] is False# nosec
    assert app.config["DEBUG_TB_ENABLED"] is False# nosec


def test_dev_config():
    """Development config."""
    app = create_app(Config)
    assert app.config["ENV"] == "dev"# nosec
    # assert app.config["FLASK_DEBUG"] is True
