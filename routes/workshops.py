import uuid
import json
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy.sql import func
from __init__ import db
from models.workshop import WorkshopTemplate, Workshop, UserWorkshop
from models.droplet import Droplet, DropletInstance
from models.user import User
from models.tenant import Tenant
from utils.permissions import Permissions
from utils.schemas import WorkshopTemplateCreateSchema, WorkshopCreateSchema, UserWorkshopCreateSchema
from marshmallow import ValidationError

workshop_bp = Blueprint('workshops', __name__)

# Workshop Templates API
@workshop_bp.route('/api/workshops/templates', methods=['GET'])
@login_required
def api_workshop_templates_list():
    """Get all public workshop templates"""
    if not current_user.has_permission(Permissions.VIEW_WORKSHOPS):
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    templates = WorkshopTemplate.query.filter(
        WorkshopTemplate.is_public == True,
        WorkshopTemplate.is_active == True
    ).all()
    
    templates_data = []
    for template in templates:
        templates_data.append({
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "category": template.category,
            "thumbnail": template.thumbnail,
            "estimated_duration": template.estimated_duration,
            "difficulty_level": template.difficulty_level,
            "created_by": template.created_by,
            "created_at": template.created_at.isoformat() if template.created_at else None
        })
    
    return jsonify({
        "success": True,
        "templates": templates_data
    })

@workshop_bp.route('/api/workshops/templates', methods=['POST'])
@login_required
def api_workshop_templates_create():
    """Create a new workshop template (Admin only)"""
    if not current_user.has_permission(Permissions.MANAGE_TEMPLATES):
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    schema = WorkshopTemplateCreateSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"success": False, "error": err.messages}), 400
    
    template = WorkshopTemplate(
        name=data['name'],
        description=data.get('description'),
        category=data['category'],
        thumbnail=data.get('thumbnail'),
        config_schema=data.get('config_schema'),
        template_droplets=data.get('template_droplets'),
        estimated_duration=data.get('estimated_duration'),
        difficulty_level=data.get('difficulty_level'),
        is_public=data.get('is_public', True),
        created_by=current_user.id,
        tenant_id=current_user.tenant_id
    )
    
    try:
        template.set_config_schema(json.loads(data.get('config_schema', '{}')))
        template.set_template_droplets(json.loads(data.get('template_droplets', '[]')))
    except json.JSONDecodeError:
        return jsonify({"success": False, "error": "Invalid JSON in config_schema or template_droplets"}), 400
    
    db.session.add(template)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "template_id": template.id
    })

@workshop_bp.route('/api/workshops/templates/<template_id>', methods=['GET'])
@login_required
def api_workshop_template_details(template_id):
    """Get details of a specific workshop template"""
    if not current_user.has_permission(Permissions.VIEW_WORKSHOPS):
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    template = WorkshopTemplate.query.filter_by(id=template_id).first()
    if not template:
        return jsonify({"success": False, "error": "Template not found"}), 404
    
    if not template.is_public and template.created_by != current_user.id:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    return jsonify({
        "success": True,
        "template": template.to_dict()
    })

# Workshops API
@workshop_bp.route('/api/workshops', methods=['GET'])
@login_required
def api_workshops_list():
    """Get all workshops (admin and personal)"""
    if not current_user.has_permission(Permissions.VIEW_WORKSHOPS):
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    # Get workshops created by user or public workshops
    workshops = Workshop.query.filter(
        (Workshop.created_by == current_user.id) | 
        (Workshop.is_public == True)
    ).all()
    
    workshops_data = []
    for workshop in workshops:
        workshops_data.append(workshop.to_dict())
    
    return jsonify({
        "success": True,
        "workshops": workshops_data
    })

@workshop_bp.route('/api/workshops', methods=['POST'])
@login_required
def api_workshops_create():
    """Create a new workshop from a template"""
    if not current_user.has_permission(Permissions.CREATE_WORKSHOPS):
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    schema = WorkshopCreateSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"success": False, "error": err.messages}), 400
    
    # Check if template exists if provided
    template = None
    if data.get('template_id'):
        template = WorkshopTemplate.query.filter_by(id=data['template_id']).first()
        if not template:
            return jsonify({"success": False, "error": "Template not found"}), 404
    
    workshop = Workshop(
        name=data['name'],
        description=data.get('description'),
        template_id=data.get('template_id'),
        is_public=data.get('is_public', False),
        created_by=current_user.id,
        tenant_id=current_user.tenant_id
    )
    
    db.session.add(workshop)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "workshop_id": workshop.id
    })

@workshop_bp.route('/api/workshops/<workshop_id>/start', methods=['POST'])
@login_required
def api_workshop_start(workshop_id):
    """Start a workshop"""
    if not current_user.has_permission(Permissions.CREATE_WORKSHOPS):
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    workshop = Workshop.query.filter_by(id=workshop_id).first()
    if not workshop:
        return jsonify({"success": False, "error": "Workshop not found"}), 404
    
    if workshop.created_by != current_user.id and not workshop.is_public:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    # Check if user already has an instance of this workshop
    existing_user_workshop = UserWorkshop.query.filter_by(
        user_id=current_user.id,
        workshop_id=workshop_id
    ).first()
    
    if existing_user_workshop and existing_user_workshop.status != 'stopped':
        return jsonify({"success": False, "error": "Workshop instance already running"}), 400
    
    # Create user workshop instance
    user_workshop = UserWorkshop(
        user_id=current_user.id,
        workshop_id=workshop_id,
        template_id=workshop.template_id,
        status='creating',
        tenant_id=current_user.tenant_id
    )
    
    db.session.add(user_workshop)
    db.session.commit()
    
    # TODO: Implement actual workshop instance creation logic
    # This would involve creating DropletInstance objects for each droplet in the template
    user_workshop.status = 'ready'
    db.session.commit()
    
    return jsonify({
        "success": True,
        "user_workshop_id": user_workshop.id
    })

@workshop_bp.route('/api/workshops/<workshop_id>/stop', methods=['POST'])
@login_required
def api_workshop_stop(workshop_id):
    """Stop a workshop"""
    if not current_user.has_permission(Permissions.EDIT_WORKSHOPS):
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    user_workshop = UserWorkshop.query.filter_by(
        user_id=current_user.id,
        workshop_id=workshop_id
    ).first()
    
    if not user_workshop:
        return jsonify({"success": False, "error": "Workshop instance not found"}), 404
    
    # TODO: Implement actual cleanup logic for DropletInstances
    user_workshop.status = 'stopped'
    db.session.commit()
    
    return jsonify({
        "success": True
    })

@workshop_bp.route('/api/workshops/<workshop_id>', methods=['DELETE'])
@login_required
def api_workshop_delete(workshop_id):
    """Delete a workshop"""
    if not current_user.has_permission(Permissions.EDIT_WORKSHOPS):
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    workshop = Workshop.query.filter_by(id=workshop_id).first()
    if not workshop:
        return jsonify({"success": False, "error": "Workshop not found"}), 404
    
    if workshop.created_by != current_user.id:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    # Delete associated user workshops
    UserWorkshop.query.filter_by(workshop_id=workshop_id).delete()
    db.session.delete(workshop)
    db.session.commit()
    
    return jsonify({
        "success": True
    })

# User Workshop Instances API
@workshop_bp.route('/api/user-workshops', methods=['GET'])
@login_required
def api_user_workshops_list():
    """Get all user workshop instances"""
    if not current_user.has_permission(Permissions.VIEW_WORKSHOP_INSTANCES):
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    user_workshops = UserWorkshop.query.filter_by(user_id=current_user.id).all()
    
    user_workshops_data = []
    for user_workshop in user_workshops:
        data = user_workshop.to_dict()
        # Add workshop info
        if user_workshop.workshop:
            data['workshop_name'] = user_workshop.workshop.name
            data['workshop_description'] = user_workshop.workshop.description
        # Add template info
        if user_workshop.template:
            data['template_name'] = user_workshop.template.name
            data['template_category'] = user_workshop.template.category
        user_workshops_data.append(data)
    
    return jsonify({
        "success": True,
        "user_workshops": user_workshops_data
    })

@workshop_bp.route('/api/user-workshops', methods=['POST'])
@login_required
def api_user_workshops_create():
    """Create a new user workshop instance"""
    if not current_user.has_permission(Permissions.CREATE_WORKSHOPS):
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    schema = UserWorkshopCreateSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"success": False, "error": err.messages}), 400
    
    # Check if workshop exists
    workshop = Workshop.query.filter_by(id=data['workshop_id']).first()
    if not workshop:
        return jsonify({"success": False, "error": "Workshop not found"}), 404
    
    # Check if user already has an active instance
    existing_user_workshop = UserWorkshop.query.filter_by(
        user_id=current_user.id,
        workshop_id=data['workshop_id']
    ).filter(UserWorkshop.status != 'stopped').first()
    
    if existing_user_workshop:
        return jsonify({"success": False, "error": "Active workshop instance already exists"}), 400
    
    user_workshop = UserWorkshop(
        user_id=current_user.id,
        workshop_id=data['workshop_id'],
        template_id=data.get('template_id'),
        custom_config=data.get('custom_config'),
        status='creating',
        tenant_id=current_user.tenant_id
    )
    
    # Set custom config if provided
    if data.get('custom_config'):
        try:
            user_workshop.set_custom_config(json.loads(data['custom_config']))
        except json.JSONDecodeError:
            return jsonify({"success": False, "error": "Invalid JSON in custom_config"}), 400
    
    db.session.add(user_workshop)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "user_workshop_id": user_workshop.id
    })

@workshop_bp.route('/api/user-workshops/<user_workshop_id>', methods=['GET'])
@login_required
def api_user_workshop_details(user_workshop_id):
    """Get details of a specific user workshop instance"""
    if not current_user.has_permission(Permissions.VIEW_WORKSHOP_INSTANCES):
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    user_workshop = UserWorkshop.query.filter_by(
        id=user_workshop_id,
        user_id=current_user.id
    ).first()
    
    if not user_workshop:
        return jsonify({"success": False, "error": "User workshop not found"}), 404
    
    return jsonify({
        "success": True,
        "user_workshop": user_workshop.to_dict()
    })

@workshop_bp.route('/api/user-workshops/<user_workshop_id>/start', methods=['POST'])
@login_required
def api_user_workshop_start(user_workshop_id):
    """Start a user workshop instance"""
    if not current_user.has_permission(Permissions.CREATE_WORKSHOPS):
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    user_workshop = UserWorkshop.query.filter_by(
        id=user_workshop_id,
        user_id=current_user.id
    ).first()
    
    if not user_workshop:
        return jsonify({"success": False, "error": "User workshop not found"}), 404
    
    if user_workshop.status != 'stopped':
        return jsonify({"success": False, "error": "Workshop instance is already running"}), 400
    
    # TODO: Implement actual workshop instance creation logic
    # This would involve creating DropletInstance objects based on the template
    user_workshop.status = 'ready'
    user_workshop.start_time = func.now()
    db.session.commit()
    
    return jsonify({
        "success": True
    })

@workshop_bp.route('/api/user-workshops/<user_workshop_id>/stop', methods=['POST'])
@login_required
def api_user_workshop_stop(user_workshop_id):
    """Stop a user workshop instance"""
    if not current_user.has_permission(Permissions.EDIT_WORKSHOPS):
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    user_workshop = UserWorkshop.query.filter_by(
        id=user_workshop_id,
        user_id=current_user.id
    ).first()
    
    if not user_workshop:
        return jsonify({"success": False, "error": "User workshop not found"}), 404
    
    # TODO: Implement actual cleanup logic for associated DropletInstances
    user_workshop.status = 'stopped'
    user_workshop.end_time = func.now()
    db.session.commit()
    
    return jsonify({
        "success": True
    })

@workshop_bp.route('/api/user-workshops/<user_workshop_id>', methods=['DELETE'])
@login_required
def api_user_workshop_delete(user_workshop_id):
    """Delete a user workshop instance"""
    if not current_user.has_permission(Permissions.EDIT_WORKSHOPS):
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    user_workshop = UserWorkshop.query.filter_by(
        id=user_workshop_id,
        user_id=current_user.id
    ).first()
    
    if not user_workshop:
        return jsonify({"success": False, "error": "User workshop not found"}), 404
    
    # TODO: Implement actual cleanup logic for associated DropletInstances
    db.session.delete(user_workshop)
    db.session.commit()
    
    return jsonify({
        "success": True
    })