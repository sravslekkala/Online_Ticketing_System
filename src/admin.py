from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from src.models import User, db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/settings', methods=['GET'])
@login_required
def admin_panel():
    """
    Display the admin panel with user management options.
    Returns:
        Rendered template for the admin panel or redirects to index if not authorized.
    """
    if current_user.role != 'Admin':
        flash("Access denied.")
        return redirect(url_for('main.index'))

    users = User.query.all()
    return render_template('admin_panel.html', users=users)

@admin_bp.route('/admin/users/<int:user_id>/update_role', methods=['POST'])
@login_required
def update_user_role(user_id):
    """
    Update the role of a user.
    Args:
        user_id (int): The ID of the user to update.
    Returns:
        Redirects to the admin panel on success or index if not authorized.
    """
    if current_user.role != 'Admin':
        flash("Access denied.")
        return redirect(url_for('main.index'))

    new_role = request.form.get('role')
    user = User.query.get(user_id)

    if user:
        user.role = new_role
        db.session.commit()
        flash(f"{user.username}'s role updated to {new_role}.")
    else:
        flash("User not found.")

    return redirect(url_for('admin.admin_panel'))
