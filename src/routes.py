from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, make_response, jsonify
from flask_login import current_user, login_required
from src import db, socketio
from src.models import Ticket, User, Comment
from werkzeug.utils import secure_filename
from collections import Counter, defaultdict
from datetime import datetime
import os, csv, io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Socket.IO event handlers
@socketio.on('user_typing')
def handle_typing(data):
    """
    Handle user typing events.
    Args:
        data (dict): Contains ticket_id and username
    """
    try:
        # Broadcast to all clients except sender
        socketio.emit('user_typing', {
            'ticket_id': data['ticket_id'],
            'username': data['username']
        }, skip_sid=request.sid)
    except Exception as e:
        logger.error(f"Error handling typing event: {str(e)}")
        socketio.emit('comment_error', {
            'ticket_id': data['ticket_id'],
            'message': 'Error processing typing event'
        }, to=request.sid)

def validate_ticket_data(data):
    """
    Validate ticket form data.
    Args:
        data (dict): Form data to validate
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if not data.get('title', '').strip():
        return False, "Title is required"
    if not data.get('description', '').strip():
        return False, "Description is required"
    if not data.get('creator_id'):
        return False, "Creator is required"
    if data.get('priority') not in ['Low', 'Medium', 'High']:
        return False, "Invalid priority level"
    return True, ""

def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.
    Args:
        filename (str): The name of the file to check.
    Returns:
        bool: True if the file extension is allowed, False otherwise.
    """
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'png', 'jpg', 'jpeg', 'docx'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    Render the home page with ticket statistics and charts.
    Returns:
        Rendered template with ticket data and statistics.
    """
    try:
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
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        flash("An error occurred while loading the dashboard.", "danger")
        return redirect(url_for('main.index'))

@main_bp.route('/tickets')
@login_required
def ticket_list():
    """
    Display a list of all tickets.
    Returns:
        Rendered template with all tickets.
    """
    try:
        tickets = Ticket.query.all()
        return render_template('ticket_list.html', tickets=tickets)
    except Exception as e:
        logger.error(f"Error in ticket_list route: {str(e)}")
        flash("An error occurred while loading tickets.", "danger")
        return redirect(url_for('main.index'))

@main_bp.route('/ticket/<int:ticket_id>')
def ticket_details(ticket_id):
    """
    Display details of a specific ticket.
    Args:
        ticket_id (int): The ID of the ticket to display.
    Returns:
        Rendered template with ticket details.
    """
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
        return render_template('ticket_details.html', ticket=ticket)
    except Exception as e:
        logger.error(f"Error in ticket_details route: {str(e)}")
        flash("An error occurred while loading ticket details.", "danger")
        return redirect(url_for('main.index'))

@main_bp.route('/create_ticket', methods=['GET', 'POST'])
@login_required
def create_ticket_form():
    """
    Handle the creation of a new ticket.
    Returns:
        Rendered template for creating a ticket or redirects to ticket details on success.
    """
    try:
        users = User.query.all()

        if request.method == 'POST':
            data = {
                'title': request.form['title'],
                'description': request.form['description'],
                'creator_id': request.form['creator_id'],
                'priority': request.form.get('priority', 'Medium')
            }

            # Validate form data
            is_valid, error_message = validate_ticket_data(data)
            if not is_valid:
                flash(f"❌ {error_message}", "danger")
                return redirect(request.url)

            attachment_path = None
            file = request.files.get('attachment')

            if file and file.filename:
                if not allowed_file(file.filename):
                    flash("❌ Invalid file type. Allowed types are pdf, png, jpg, jpeg, docx.", "danger")
                    return redirect(request.url)

                filename = secure_filename(file.filename)
                upload_folder = current_app.config['LOCAL_UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                attachment_path = file_path

            ticket = Ticket(
                title=data['title'],
                description=data['description'],
                priority=data['priority'],
                creator_id=data['creator_id'],
                attachment_path=attachment_path
            )

            db.session.add(ticket)
            db.session.commit()
            logger.info(f"Ticket created successfully: {ticket.id}")

            flash("✅ Ticket created successfully!", "success")
            return redirect(url_for('main.ticket_details', ticket_id=ticket.id))

        return render_template('create_ticket.html', users=users)
    except Exception as e:
        logger.error(f"Error in create_ticket_form route: {str(e)}")
        flash("An error occurred while creating the ticket.", "danger")
        return redirect(url_for('main.index'))

@main_bp.route('/update_ticket/<int:ticket_id>', methods=['GET', 'POST'])
def update_ticket_form(ticket_id):
    """
    Handle the update of an existing ticket.
    Args:
        ticket_id (int): The ID of the ticket to update.
    Returns:
        Rendered template for updating a ticket or redirects to index on success.
    """
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
        users = User.query.all()

        if request.method == 'POST':
            if request.is_json:
                data = request.get_json()
            else:
                data = {
                    'title': request.form['title'],
                    'description': request.form['description'],
                    'status': request.form['status'],
                    'priority': request.form['priority'],
                    'creator_id': request.form['creator_id']
                }

            # Validate form data
            is_valid, error_message = validate_ticket_data(data)
            if not is_valid:
                if request.is_json:
                    return jsonify({'error': error_message}), 400
                flash(f"❌ {error_message}", "danger")
                return redirect(request.url)

            ticket.title = data['title']
            ticket.description = data['description']
            ticket.status = data['status']
            ticket.priority = data['priority']
            ticket.creator_id = data['creator_id']
            
            db.session.commit()
            logger.info(f"Ticket updated successfully: {ticket.id}")

            if request.is_json:
                return jsonify({'message': 'Ticket updated successfully!'})
            flash("Ticket updated successfully!", "success")
            return redirect(url_for('main.ticket_list'))

        return render_template('update_ticket.html', ticket=ticket, users=users)
    except Exception as e:
        logger.error(f"Error in update_ticket_form route: {str(e)}")
        if request.is_json:
            return jsonify({'error': 'An error occurred while updating the ticket.'}), 500
        flash("An error occurred while updating the ticket.", "danger")
        return redirect(url_for('main.index'))

@main_bp.route('/delete_ticket/<int:ticket_id>', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    """
    Handle the deletion of a ticket.
    Args:
        ticket_id (int): The ID of the ticket to delete.
    Returns:
        Redirects to the ticket list on success.
    """
    try:
        ticket = Ticket.query.get_or_404(ticket_id)

        # Optional: Only allow Admins or the creator to delete
        if current_user.role != 'Admin' and ticket.creator_id != current_user.id:
            flash("You don't have permission to delete this ticket.")
            return redirect(url_for('main.index'))

        # Delete comments before ticket
        Comment.query.filter_by(ticket_id=ticket.id).delete()
        db.session.delete(ticket)
        db.session.commit()
        logger.info(f"Ticket deleted successfully: {ticket_id}")

        flash("Ticket deleted successfully.")
        return redirect(url_for('main.ticket_list'))
    except Exception as e:
        logger.error(f"Error in delete_ticket route: {str(e)}")
        flash("An error occurred while deleting the ticket.", "danger")
        return redirect(url_for('main.index'))

@main_bp.route('/tickets/<int:ticket_id>/comments', methods=['POST'])
@login_required
def post_comment(ticket_id):
    """
    Handle the posting of a comment on a ticket.
    Args:
        ticket_id (int): The ID of the ticket to comment on.
    Returns:
        JSON response with success/error message.
    """
    try:
        ticket = Ticket.query.get_or_404(ticket_id)

        content = request.form.get('content')
        if not content:
            return jsonify({'error': 'Comment cannot be empty!'}), 400

        attachment_path = None
        file = request.files.get('attachment')

        if file and file.filename:
            if not allowed_file(file.filename):
                return jsonify({'error': 'Invalid attachment type. Allowed types are pdf, png, jpg, jpeg, docx.'}), 400

            filename = secure_filename(file.filename)
            upload_folder = current_app.config['LOCAL_UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            attachment_path = file_path

        comment = Comment(
            content=content,
            user_id=current_user.id,
            ticket_id=ticket.id,
            attachment_path=attachment_path
        )

        db.session.add(comment)
        db.session.commit()
        logger.info(f"Comment posted successfully on ticket: {ticket_id}")

        # Prepare comment data for emission
        comment_data = {
            'ticket_id': ticket.id,
            'comment_id': comment.id,
            'username': current_user.username,
            'content': content,
            'timestamp': comment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'attachment': filename if attachment_path else None,
            'ticket_title': ticket.title,
            'assignee_id': ticket.creator_id,
            'assignee_username': ticket.creator.username if ticket.creator else None,
            'commenter_id': current_user.id
        }

        # Emit the comment to all connected clients
        socketio.emit('comment_added', comment_data, namespace='/')

        return jsonify({'message': 'Comment posted successfully!'})
    except Exception as e:
        logger.error(f"Error in post_comment route: {str(e)}")
        socketio.emit('comment_error', {
            'ticket_id': ticket_id,
            'message': 'Error posting comment'
        }, namespace='/')
        return jsonify({'error': 'An error occurred while posting the comment.'}), 500

@main_bp.route('/export_tickets')
@login_required
def export_tickets():
    """
    Export all tickets to a CSV file.
    Returns:
        CSV file containing ticket data.
    """
    try:
        tickets = Ticket.query.all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Title', 'Description', 'Status', 'Priority', 'Created At', 'Updated At', 'Creator'])
        for ticket in tickets:
            writer.writerow([
                ticket.id,
                ticket.title,
                ticket.description,
                ticket.status,
                ticket.priority,
                ticket.created_at,
                ticket.updated_at,
                ticket.creator.username
            ])
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=tickets.csv'
        response.headers['Content-type'] = 'text/csv'
        logger.info("Tickets exported successfully")
        return response
    except Exception as e:
        logger.error(f"Error in export_tickets route: {str(e)}")
        flash("An error occurred while exporting tickets.", "danger")
        return redirect(url_for('main.index'))
