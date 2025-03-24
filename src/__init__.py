from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from config import config_dict

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app(config_name='development'):
    """App factory function to create and configure the Flask app."""
    app = Flask(__name__)

    # Load configuration dynamically based on the environment
    config_class = config_dict.get(config_name, config_dict['development'])
    app.config.from_object(config_class)

    # Initialize database with the app
    db.init_app(app)

    # Import models so they are registered with SQLAlchemy
    with app.app_context():
        from . import models
        db.create_all()  # Ensure database tables are created

    # Register Blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)  # General routes

    from .tickets import ticket_bp
    app.register_blueprint(ticket_bp, url_prefix='/api')  # Ticket API routes

    return app
