import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration with default settings"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_EMAIL = "admin@tktsys.com"
    DEFAULT_ADMIN_PASSWORD = "admin"

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'app_demo.db')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Dictionary to select configuration dynamically
config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig
}
