from flask import Blueprint, jsonify

# Create a blueprint for general routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Basic welcome route"""
    return jsonify({"message": "Welcome to the Online Ticketing System!"}), 200
