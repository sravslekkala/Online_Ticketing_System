from setuptools import setup, find_packages

setup(
    name="online-ticketing-system",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask>=3.1.0",
        "flask-sqlalchemy>=3.1.1",
        "flask-socketio>=5.5.1",
        "eventlet>=0.39.1",
        "flask-login>=0.6.3",
        "flask-migrate>=4.1.0",
        "psycopg2-binary>=2.9.10",
        "python-dotenv>=1.0.0",
        "werkzeug>=3.0.1",
        "gunicorn>=20.1.0",
    ],
) 