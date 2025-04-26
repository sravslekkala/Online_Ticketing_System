from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from src import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    """
    User model representing a user in the system.
    Attributes:
        id (int): Primary key.
        username (str): Unique username.
        email (str): Unique email address.
        password (str): Hashed password.
        role (str): User role (Admin, Member, Developer).
        tickets (relationship): Tickets created by the user.
        comments (relationship): Comments made by the user.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(1024), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="Member")
    __table_args__ = (
    db.CheckConstraint(
        "role IN ('Admin', 'Member', 'Developer')",
        name='check_user_role'
        ),
    )
    tickets = db.relationship('Ticket', backref='creator', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

class Ticket(db.Model):
    """
    Ticket model representing a support ticket.
    Attributes:
        id (int): Primary key.
        title (str): Ticket title.
        description (str): Ticket description.
        status (str): Current status of the ticket.
        priority (str): Priority level of the ticket.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        creator_id (int): Foreign key to the user who created the ticket.
        attachment_path (str): Path to any attached file.
        comments (relationship): Comments associated with the ticket.
    """
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Open')
    priority = db.Column(db.String(20), default='Medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    attachment_path = db.Column(db.String(255))
    
    comments = db.relationship('Comment', backref='ticket', cascade='all, delete', passive_deletes=True)

class Comment(db.Model):
    """
    Comment model representing a comment on a ticket.
    Attributes:
        id (int): Primary key.
        content (str): Comment content.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        user_id (int): Foreign key to the user who made the comment.
        ticket_id (int): Foreign key to the ticket the comment is on.
        attachment_path (str): Path to any attached file.
        user (relationship): User who made the comment.
    """
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id', ondelete='CASCADE'), nullable=False)

    attachment_path = db.Column(db.String(255))

    user = db.relationship('User', backref='user_comments', overlaps="author,comments")



