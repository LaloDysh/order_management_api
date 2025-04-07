# app/config.py
import os
from datetime import timedelta

JWT_ACCESS_TOKEN_EXPIRES = os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', '86400')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_change_this_in_production')
    
    # Database URI without connection pooling parameters
    DB_URI = os.environ.get('DATABASE_URI', 'postgresql://postgres:postgres@db:5432/order_management')
    
    # Keep the base URI clean without pooling parameters
    SQLALCHEMY_DATABASE_URI = DB_URI
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # All connection pooling parameters go here
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 1800
    }
    
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt_dev_key_change_this_in_production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(JWT_ACCESS_TOKEN_EXPIRES))