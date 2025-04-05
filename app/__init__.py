from flask import Flask
from app.config import Config
from app.extensions import db, jwt, migrate
from app.api import register_blueprints


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    register_blueprints(app)

    @app.route('/health')
    def health_check():
        return {'status': 'ok'}

    return app