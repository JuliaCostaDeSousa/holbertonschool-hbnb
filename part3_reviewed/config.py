import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True
    JWT_SECRET_KEY = os.getenv('SECRET_KEY', 'dev-jwt-secret')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=5)

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
