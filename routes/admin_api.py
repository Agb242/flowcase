"""
Admin API Routes
Provides API endpoints for the admin panel
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from functools import wraps
from models.user import User
from models.droplet import Droplet, DropletInstance
from models.tenant import Tenant
from models.workshop import Workshop
from models.log import Log
from services.droplet_manager import droplet_manager
from __init__ import db
from utils.logger import log

admin_api_bp = Blueprint('admin_api', __name__, url_prefix='/api/admin')

def admin_required(f):
    """Decorator to require admin permissions"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        if not current_user.has_permission('perm_admin_panel'):
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_api_bp.route('/stats', methods=['GET'])
@login_required
@admin_required
def get_stats():
    """Get dashboard statistics"""
    try:
        stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_droplets': Droplet.query.count(),
            'active_droplets': DropletInstance.query.filter_by(container_status='running').count(),
            'workshops': Workshop.query.count(),
            'tenants': Tenant.query.count(),
            'total_instances': DropletInstance.query.count()
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        log('ERROR', f'Failed to get stats: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def list_users():
    """List all users with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        query = User.query
        
        if search:
            query = query.filter(
                db.or_(
                    User.username.like(f'%{search}%'),
                    User.email.like(f'%{search}%')
                )
            )
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        users_data = []
        for user in pagination.items:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'tenant_id': user.tenant_id
            })
        
        return jsonify({
            'success': True,
            'users': users_data,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
        
    except Exception as e:
        log('ERROR', f'Failed to list users: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api_bp.route('/users/<user_id>', methods=['GET'])
@login_required
@admin_required
def get_user(user_id):
    """Get detailed user information"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Get user's droplet instances
        instances = DropletInstance.query.filter_by(user_id=user_id).all()
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'tenant_id': user.tenant_id,
            'instance_count': len(instances),
            'instances': [inst.to_dict() for inst in instances]
        }
        
        return jsonify({
            'success': True,
            'user': user_data
        })
        
    except Exception as e:
        log('ERROR', f'Failed to get user: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api_bp.route('/droplets', methods=['GET'])
@login_required
@admin_required
def list_droplets():
    """List all droplets"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        pagination = Droplet.query.paginate(page=page, per_page=per_page, error_out=False)
        
        droplets_data = [droplet.to_dict() for droplet in pagination.items]
        
        return jsonify({
            'success': True,
            'droplets': droplets_data,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
        
    except Exception as e:
        log('ERROR', f'Failed to list droplets: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api_bp.route('/instances', methods=['GET'])
@login_required
@admin_required
def list_instances():
    """List all droplet instances"""
    try:
        status_filter = request.args.get('status', None)
        
        query = DropletInstance.query
        if status_filter:
            query = query.filter_by(container_status=status_filter)
        
        instances = query.order_by(DropletInstance.created_at.desc()).limit(100).all()
        
        instances_data = []
        for instance in instances:
            inst_dict = instance.to_dict()
            
            # Add user info
            user = User.query.get(instance.user_id)
            if user:
                inst_dict['username'] = user.username
            
            # Add droplet info
            droplet = Droplet.query.get(instance.droplet_id)
            if droplet:
                inst_dict['droplet_name'] = droplet.display_name
            
            instances_data.append(inst_dict)
        
        return jsonify({
            'success': True,
            'instances': instances_data
        })
        
    except Exception as e:
        log('ERROR', f'Failed to list instances: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api_bp.route('/instances/<instance_id>/stop', methods=['POST'])
@login_required
@admin_required
def stop_instance(instance_id):
    """Stop a running instance"""
    try:
        droplet_manager.stop_instance(instance_id)
        log('INFO', f'Admin {current_user.username} stopped instance {instance_id}')
        
        return jsonify({
            'success': True,
            'message': 'Instance stopped successfully'
        })
        
    except Exception as e:
        log('ERROR', f'Failed to stop instance: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api_bp.route('/instances/<instance_id>/restart', methods=['POST'])
@login_required
@admin_required
def restart_instance(instance_id):
    """Restart an instance"""
    try:
        droplet_manager.restart_instance(instance_id)
        log('INFO', f'Admin {current_user.username} restarted instance {instance_id}')
        
        return jsonify({
            'success': True,
            'message': 'Instance restarted successfully'
        })
        
    except Exception as e:
        log('ERROR', f'Failed to restart instance: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api_bp.route('/instances/<instance_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_instance(instance_id):
    """Delete an instance"""
    try:
        remove_volumes = request.json.get('remove_volumes', False)
        droplet_manager.delete_instance(instance_id, remove_volumes=remove_volumes)
        log('INFO', f'Admin {current_user.username} deleted instance {instance_id}')
        
        return jsonify({
            'success': True,
            'message': 'Instance deleted successfully'
        })
        
    except Exception as e:
        log('ERROR', f'Failed to delete instance: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api_bp.route('/instances/<instance_id>/stats', methods=['GET'])
@login_required
@admin_required
def get_instance_stats(instance_id):
    """Get instance resource usage statistics"""
    try:
        stats = droplet_manager.get_instance_stats(instance_id)
        
        if stats is None:
            return jsonify({'success': False, 'error': 'Failed to get stats'}), 500
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        log('ERROR', f'Failed to get instance stats: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api_bp.route('/volumes', methods=['GET'])
@login_required
@admin_required
def list_volumes():
    """List all persistent volumes"""
    try:
        droplet_id = request.args.get('droplet_id', None)
        volumes = droplet_manager.list_volumes(droplet_id=droplet_id)
        
        return jsonify({
            'success': True,
            'volumes': volumes
        })
        
    except Exception as e:
        log('ERROR', f'Failed to list volumes: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api_bp.route('/cleanup', methods=['POST'])
@login_required
@admin_required
def cleanup_orphaned():
    """Cleanup orphaned containers and volumes"""
    try:
        cleaned = droplet_manager.cleanup_orphaned_containers()
        log('INFO', f'Admin {current_user.username} cleaned up {cleaned} orphaned containers')
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {cleaned} orphaned containers'
        })
        
    except Exception as e:
        log('ERROR', f'Failed to cleanup: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api_bp.route('/tenants', methods=['GET'])
@login_required
@admin_required
def list_tenants():
    """List all tenants"""
    try:
        tenants = Tenant.query.all()
        
        tenants_data = []
        for tenant in tenants:
            user_count = User.query.filter_by(tenant_id=tenant.id).count()
            tenants_data.append({
                'id': tenant.id,
                'name': tenant.name,
                'description': tenant.description,
                'user_count': user_count,
                'created_at': tenant.created_at.isoformat() if tenant.created_at else None
            })
        
        return jsonify({
            'success': True,
            'tenants': tenants_data
        })
        
    except Exception as e:
        log('ERROR', f'Failed to list tenants: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api_bp.route('/workshops', methods=['GET'])
@login_required
@admin_required
def list_workshops():
    """List all workshops"""
    try:
        workshops = Workshop.query.all()
        
        workshops_data = []
        for workshop in workshops:
            workshops_data.append({
                'id': workshop.id,
                'name': workshop.name,
                'description': workshop.description,
                'created_at': workshop.created_at.isoformat() if workshop.created_at else None
            })
        
        return jsonify({
            'success': True,
            'workshops': workshops_data
        })
        
    except Exception as e:
        log('ERROR', f'Failed to list workshops: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api_bp.route('/logs', methods=['GET'])
@login_required
@admin_required
def get_logs():
    """Get system logs with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        level = request.args.get('level', None)
        
        query = Log.query
        
        if level:
            query = query.filter_by(level=level)
        
        pagination = query.order_by(Log.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        logs_data = []
        for log in pagination.items:
            logs_data.append({
                'id': log.id,
                'level': log.level,
                'message': log.message,
                'created_at': log.created_at.isoformat() if log.created_at else None
            })
        
        return jsonify({
            'success': True,
            'logs': logs_data,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
        
    except Exception as e:
        log('ERROR', f'Failed to get logs: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_api_bp.route('/system/health', methods=['GET'])
@login_required
@admin_required
def system_health():
    """Get system health status"""
    try:
        # Check database
        db_healthy = True
        try:
            db.session.execute('SELECT 1')
        except:
            db_healthy = False
        
        # Check Docker
        docker_healthy = True
        docker_version = None
        try:
            docker_client = droplet_manager.docker_client
            docker_version = docker_client.version()['Version']
        except:
            docker_healthy = False
        
        health_data = {
            'database': {
                'status': 'healthy' if db_healthy else 'unhealthy',
                'responsive': db_healthy
            },
            'docker': {
                'status': 'healthy' if docker_healthy else 'unhealthy',
                'version': docker_version,
                'responsive': docker_healthy
            },
            'overall': 'healthy' if (db_healthy and docker_healthy) else 'degraded'
        }
        
        return jsonify({
            'success': True,
            'health': health_data
        })
        
    except Exception as e:
        log('ERROR', f'Failed to check system health: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500
