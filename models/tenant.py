import uuid
from sqlalchemy.sql import func
from __init__ import db

class Tenant(db.Model):
    """Represents a tenant (organization) in a multi‑tenant setup."""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(80), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, server_default=func.now())

    # Relationships
    users = db.relationship('User', backref='tenant', lazy=True)
    droplets = db.relationship('Droplet', backref='tenant', lazy=True)
    workshop_templates = db.relationship('WorkshopTemplate', backref='tenant', lazy=True)
    workshops = db.relationship('Workshop', backref='tenant', lazy=True)
    user_workshops = db.relationship('UserWorkshop', backref='tenant', lazy=True)