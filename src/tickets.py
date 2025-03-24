from flask import Blueprint, request, jsonify, redirect, url_for, flash
from .models import Ticket, db

# Create a blueprint for ticket-related routes
ticket_bp = Blueprint('ticket', __name__)

@ticket_bp.route('/tickets', methods=['POST'])
def create_ticket():
    """API to create a new ticket"""
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 415

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

@ticket_bp.route('/api/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """Retrieve a single ticket"""
    ticket = Ticket.query.get(ticket_id)

    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    return jsonify({
        'id': ticket.id,
        'title': ticket.title,
        'description': ticket.description,
        'status': ticket.status,
        'priority': ticket.priority,
        'creator_id': ticket.creator_id,
        'created_at': ticket.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': ticket.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 200


@ticket_bp.route('/tickets/<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    """API to update a ticket"""
    print(f"Received PUT request for ticket ID: {ticket_id}")

    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        print("Ticket not found!")  # Debugging output
        return jsonify({'error': f'Ticket with ID {ticket_id} not found'}), 404

    data = request.get_json()
    print(f"Received Data: {data}")  # Debugging output

    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    if 'title' in data:
        ticket.title = data['title']
    if 'description' in data:
        ticket.description = data['description']
    if 'status' in data:
        ticket.status = data['status']
    if 'priority' in data:
        ticket.priority = data['priority']

    db.session.commit()
    print(f"Updated Ticket: {ticket}")  # Debugging output

    return jsonify({'message': 'Ticket updated successfully'}), 200


@ticket_bp.route('/api/tickets/<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    """API to delete a ticket"""
    ticket = Ticket.query.get(ticket_id)

    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    db.session.delete(ticket)
    db.session.commit()

    return jsonify({'message': 'Ticket deleted successfully'}), 200
