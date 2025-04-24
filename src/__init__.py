from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from config import config_dict
from flask_login import LoginManager

# Initialize SQLAlchemy
db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins='*')

def create_app(config_name='development'):
    """App factory function to create and configure the Flask app."""
    app = Flask(__name__)

    # Load configuration dynamically based on the environment
    config_class = config_dict.get(config_name, config_dict['development'])
    app.config.from_object(config_class)

    # Initialize database with the app
    db.init_app(app)
    socketio.init_app(app)
    
    # Set up Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # This is where Flask redirects unauthenticated users
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import models so they are registered with SQLAlchemy
    with app.app_context():
        from . import models
        db.create_all()  # Ensure database tables are created

    # Register Blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)  # General routes

    from .tickets import ticket_bp
    app.register_blueprint(ticket_bp, url_prefix='/api')  # Ticket API routes

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .admin import admin_bp
    app.register_blueprint(admin_bp)


    return app
