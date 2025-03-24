from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Ticket, User, db
from .tickets import create_ticket as create_ticket_api, update_ticket as update_ticket_api

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    tickets = Ticket.query.all()
    return render_template('index.html', tickets=tickets)

@main_bp.route('/ticket/<int:ticket_id>')
def ticket_details(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    return render_template('ticket_details.html', ticket=ticket)

@main_bp.route('/create_ticket', methods=['GET', 'POST'])
def create_ticket_form():
    users = User.query.all()  # Fetch users for dropdown

    if request.method == 'POST':
        data = {
            "title": request.form['title'],
            "description": request.form['description'],
            "creator_id": request.form['creator_id']
        }

        response = create_ticket_api()
        if isinstance(response, tuple):  # Handle Flask response
            response_data, status_code = response
            if status_code == 201:
                flash("Ticket created successfully!", "success")
                return redirect(url_for('main.index'))
            else:
                flash(response_data.get("error", "Failed to create ticket!"), "danger")

    return render_template('create_ticket.html', users=users)

@main_bp.route('/update_ticket/<int:ticket_id>', methods=['GET', 'PUT'])
def update_ticket_form(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    users = User.query.all()

    if request.method == 'POST':
        data = {
            "title": request.form['title'],
            "description": request.form['description'],
            "status": request.form['status'],
            "priority": request.form['priority'],
            "creator_id": request.form['creator_id']
        }

        response = update_ticket_api(ticket_id)
        if isinstance(response, tuple):
            response_data, status_code = response
            if status_code == 200:
                flash("Ticket updated successfully!", "success")
                return redirect(url_for('main.index'))
            else:
                flash(response_data.get("error", "Failed to update ticket!"), "danger")

    return render_template('update_ticket.html', ticket=ticket, users=users)
