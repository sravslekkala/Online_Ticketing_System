import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Base configuration class with common settings.
    """
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'local')
    LOCAL_UPLOAD_FOLDER = os.getenv('LOCAL_UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'docx'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB file upload limit

    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_EMAIL = "admin@tktsys.com"
    DEFAULT_ADMIN_PASSWORD = "admin"

class DevelopmentConfig(Config):
    """
    Development environment configuration.
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'app_demo.db')

class TestingConfig(Config):
    """
    Testing environment configuration.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """
    Production environment configuration.
    """
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
