import os
from src import create_app, db, socketio

# Choose the environment (default to development)
config_name = os.getenv('FLASK_ENV', 'development')

# Initialize the Flask app
app = create_app(config_name)

# Define the database file path based on the config
db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace("sqlite:///", "")

# Ensure the database is created only if it doesn't already exist
with app.app_context():
    if not os.path.exists(db_path):
        print("Initializing the database...")
        db.create_all()
        print("Database initialized successfully.")
    else:
        print("Database already exists. Skipping initialization.")

# Run the Flask application
if __name__ == '__main__':
    socketio.run(app, debug=True)
