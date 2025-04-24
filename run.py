import os
from src import create_app, db, socketio

# Choose the environment (default to development)
config_name = os.getenv('FLASK_ENV', 'development')

# Initialize the Flask app
app = create_app(config_name)
admin_username = app.config['DEFAULT_ADMIN_USERNAME']
admin_email = app.config['DEFAULT_ADMIN_EMAIL']
admin_password = app.config['DEFAULT_ADMIN_PASSWORD']

# Define the database file path based on the config
db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace("sqlite:///", "")

# Ensure the database is created only if it doesn't already exist
with app.app_context():
    if not os.path.exists(db_path):
        print("Initializing the database...")
        db.create_all()
        print("Database initialized successfully.")

        from src.models import User
        from werkzeug.security import generate_password_hash

        if not User.query.filter_by(username="admin").first():
            admin_user = User(
                username=admin_username,
                email=admin_email,
                password=generate_password_hash(admin_password),
                role="Admin"
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Admin user created: username=admin, password=admin")
        else:
            print("ℹ️ Admin user already exists.")
    else:
        print("Database already exists. Skipping initialization.")

# Run the Flask application
if __name__ == '__main__':
    socketio.run(app, debug=True)
