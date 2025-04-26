from flask import Flask, send_from_directory, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_login import LoginManager
from config import config_dict
import os

db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")

def create_app(config_name='development'):
    app = Flask(__name__)
    config_class = config_dict.get(config_name, config_dict['development'])
    app.config.from_object(config_class)

    db.init_app(app)
    socketio.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        from . import models
        db.create_all()

    from .routes import main_bp
    app.register_blueprint(main_bp)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        upload_folder = os.path.join(os.getcwd(), current_app.config['LOCAL_UPLOAD_FOLDER'])
        print(f"Serving from folder: {upload_folder}")
        print(f"Requested filename: {filename}")
        return send_from_directory(upload_folder, filename)

    return app
