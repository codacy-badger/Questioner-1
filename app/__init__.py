"""Initializing the app."""
from flask import Flask
from app.api.v1.views.api_views import v1_u, v1_m, v1_q
from instance.config import app_config


def create_app(config='development'):
    app = Flask(__name__)
    app.register_blueprint(v1_u, url_prefix='/api/v1')
    app.register_blueprint(v1_m, url_prefix='/api/v1')
    app.register_blueprint(v1_q, url_prefix='/api/v1')
    app.config.from_object(app_config[config])
    app.config.from_pyfile('../instance/config.py')

    return app
