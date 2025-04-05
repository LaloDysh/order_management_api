from flask import Blueprint
from app.api.users import users_bp
from app.api.orders import orders_bp
from app.api.reports import reports_bp
from app.api.auth import auth_bp


def register_blueprints(app):
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')