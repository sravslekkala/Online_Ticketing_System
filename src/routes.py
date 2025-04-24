from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.models import Ticket, User, db
from src.tickets import create_ticket as create_ticket_api, update_ticket as update_ticket_api
from flask_login import current_user, login_required
from collections import Counter, defaultdict
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    tickets = Ticket.query.all()

    # --- 1. Chart data ---
    status_counts = Counter(t.status for t in tickets)
    priority_counts = Counter(t.priority for t in tickets)

    # --- 2. Monthly trends ---
    monthly_counts = defaultdict(int)
    for t in tickets:
        if t.created_at:
            month = t.created_at.strftime('%Y-%m')
            monthly_counts[month] += 1

    sorted_months = sorted(monthly_counts.keys())

    # --- 3. Top contributors ---
    assignee_counts = Counter(t.creator.username for t in tickets)

    # --- 4. Avg resolution time (Closed only) ---
    durations = [
        (t.updated_at - t.created_at).days
        for t in tickets if t.status == 'Closed' and t.updated_at
    ]
    avg_days = round(sum(durations) / len(durations), 2) if durations else 0

    return render_template(
        'index.html',
        tickets=tickets,
        status_counts=status_counts,
        priority_counts=priority_counts,
        monthly_labels=sorted_months,
        monthly_data=[monthly_counts[m] for m in sorted_months],
        assignee_labels=list(assignee_counts.keys()),
        assignee_data=list(assignee_counts.values()),
        avg_days=avg_days
    )

@main_bp.route('/tickets')
@login_required
def ticket_list():
    tickets = Ticket.query.all()
    return render_template('ticket_list.html', tickets=tickets)

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

@main_bp.route('/delete_ticket/<int:ticket_id>', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    # Optional: Only allow Admins or the creator to delete
    if current_user.role != 'Admin' and ticket.creator_id != current_user.id:
        flash("You don't have permission to delete this ticket.")
        return redirect(url_for('main.index'))

    # Delete comments before ticket
    Comment.query.filter_by(ticket_id=ticket.id).delete()
    db.session.delete(ticket)
    db.session.commit()

    flash("Ticket deleted successfully.")
    return redirect(url_for('main.index'))
