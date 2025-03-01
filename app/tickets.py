from flask import Blueprint, request, jsonify
from .models import Ticket, db

# Create a blueprint for ticket-related routes
ticket_bp = Blueprint('ticket', __name__)

@ticket_bp.route('/tickets', methods=['POST'])
def create_ticket():
    """Create a new ticket"""
    data = request.get_json()
    if not data or 'title' not in data or 'description' not in data or 'creator_id' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    new_ticket = Ticket(
        title=data['title'],
        description=data['description'],
        creator_id=data['creator_id']
    )

    db.session.add(new_ticket)
    db.session.commit()

    return jsonify({
        'message': 'Ticket created successfully',
        'ticket': {
            'id': new_ticket.id,
            'title': new_ticket.title,
            'description': new_ticket.description,
            'status': new_ticket.status
        }
    }), 201


@ticket_bp.route('/tickets', methods=['GET'])
def get_all_tickets():
    """Retrieve all tickets"""
    tickets = Ticket.query.all()

    ticket_list = [{
        'id': ticket.id,
        'title': ticket.title,
        'description': ticket.description,
        'status': ticket.status,
        'priority': ticket.priority,
        'creator_id': ticket.creator_id,
        'created_at': ticket.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': ticket.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    } for ticket in tickets]

    return jsonify(ticket_list), 200
