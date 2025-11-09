import uuid
import json
from sqlalchemy.sql import func
from __init__ import db

class WorkshopTemplate(db.Model):
    """Template for creating workshops with predefined configurations."""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenant.id'), nullable=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)  # DevOps, Sécurité, Cloud, Dev, DataScience
    thumbnail = db.Column(db.String(255), nullable=True)
    config_schema = db.Column(db.Text, nullable=True)  # JSON schema for configuration
    template_droplets = db.Column(db.Text, nullable=True)  # JSON: list of required droplets
    estimated_duration = db.Column(db.Integer, nullable=True)  # in minutes
    difficulty_level = db.Column(db.String(20), nullable=True)  # beginner, intermediate, advanced
    is_public = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = db.relationship('User')
    workshops = db.relationship('UserWorkshop', backref='template', lazy=True)
    
    def get_config_schema(self):
        """Parse and return config schema as dict"""
        if self.config_schema:
            try:
                return json.loads(self.config_schema)
            except:
                return {}
        return {}
    
    def set_config_schema(self, schema_dict):
        """Set config schema from dict"""
        self.config_schema = json.dumps(schema_dict)
    
    def get_template_droplets(self):
        """Parse and return template droplets as list"""
        if self.template_droplets:
            try:
                return json.loads(self.template_droplets)
            except:
                return []
        return []
    
    def set_template_droplets(self, droplets_list):
        """Set template droplets from list"""
        self.template_droplets = json.dumps(droplets_list)
    
    def to_dict(self):
        """Convert template to dictionary"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'thumbnail': self.thumbnail,
            'config_schema': self.get_config_schema(),
            'template_droplets': self.get_template_droplets(),
            'estimated_duration': self.estimated_duration,
            'difficulty_level': self.difficulty_level,
            'is_public': self.is_public,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Workshop(db.Model):
    """Workshop instance that can be instantiated from a template."""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenant.id'), nullable=True)
    template_id = db.Column(db.String(36), db.ForeignKey('workshop_template.id'), nullable=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='draft')  # draft, active, paused, completed, archived
    is_public = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    template = db.relationship('WorkshopTemplate')
    creator = db.relationship('User')
    user_workshops = db.relationship('UserWorkshop', backref='workshop', lazy=True)
    
    def to_dict(self):
        """Convert workshop to dictionary"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'template_id': self.template_id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'is_public': self.is_public,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserWorkshop(db.Model):
    """Individual user workshop instances."""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenant.id'), nullable=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    workshop_id = db.Column(db.String(36), db.ForeignKey('workshop.id'), nullable=False)
    template_id = db.Column(db.String(36), db.ForeignKey('workshop_template.id'), nullable=True)
    
    # Custom configuration
    custom_config = db.Column(db.Text, nullable=True)  # JSON configuration
    instance_ids = db.Column(db.Text, nullable=True)  # JSON: list of DropletInstance IDs
    
    # State and metadata
    status = db.Column(db.String(20), default='creating')  # creating, ready, running, stopped, error
    progress = db.Column(db.Integer, default=0)  # percentage 0-100
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    last_accessed = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = db.relationship('User')
    
    def get_custom_config(self):
        """Parse and return custom config as dict"""
        if self.custom_config:
            try:
                return json.loads(self.custom_config)
            except:
                return {}
        return {}
    
    def set_custom_config(self, config_dict):
        """Set custom config from dict"""
        self.custom_config = json.dumps(config_dict)
    
    def get_instance_ids(self):
        """Parse and return instance IDs as list"""
        if self.instance_ids:
            try:
                return json.loads(self.instance_ids)
            except:
                return []
        return []
    
    def set_instance_ids(self, instance_list):
        """Set instance IDs from list"""
        self.instance_ids = json.dumps(instance_list)
    
    def to_dict(self):
        """Convert user workshop to dictionary"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'user_id': self.user_id,
            'workshop_id': self.workshop_id,
            'template_id': self.template_id,
            'custom_config': self.get_custom_config(),
            'instance_ids': self.get_instance_ids(),
            'status': self.status,
            'progress': self.progress,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }