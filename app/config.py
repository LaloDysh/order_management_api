import os
from datetime import timedelta

JWT_ACCESS_TOKEN_EXPIRES = os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', '86400')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_change_this_in_production')
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'postgresql://postgres:postgres@db:5432/order_management')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt_dev_key_change_this_in_production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(JWT_ACCESS_TOKEN_EXPIRES))