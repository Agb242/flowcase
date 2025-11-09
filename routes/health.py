from flask import Blueprint, jsonify
from flask_login import login_required
import utils.docker
from utils.docker import is_docker_available, get_docker_version
from __init__ import db

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint returning status of core components."""
    # Check DB connectivity
    try:
        db.session.execute('SELECT 1')
        db_status = True
    except Exception:
        db_status = False

    # Docker status
    docker_status = is_docker_available()
    docker_version = get_docker_version() if docker_status else None

    # Docker Compose health: check if main nginx container is running
    nginx_running = False
    if docker_status:
        try:
            container = utils.docker.docker_client.containers.get("flowcase-nginx")
            nginx_running = container.status == "running"
        except Exception:
            nginx_running = False
    # Docker logging health: retrieve log driver and options for the web container
    docker_logging = {}
    if docker_status:
        try:
            web_container = utils.docker.docker_client.containers.get("flowcase-web")
            log_cfg = web_container.attrs.get('HostConfig', {}).get('LogConfig', {})
            docker_logging = {
                "driver": log_cfg.get('Type'),
                "options": log_cfg.get('Config')
            }
        except Exception:
            docker_logging = {"driver": None, "options": None}
    # Docker web container health: check if main web container is running
    web_running = False
    if docker_status:
        try:
            web_container = utils.docker.docker_client.containers.get("flowcase-web")
            web_running = web_container.status == "running"
        except Exception:
            web_running = False
    # Docker images status: check required images presence
    images_status = utils.docker.get_images_status() if docker_status else {}

    return jsonify({
        "status": "ok",
        "components": {
            "database": db_status,
            "docker": {
                "available": docker_status,
                "version": docker_version,
                "nginx_running": nginx_running,
                "logging": docker_logging,
                "web_running": web_running,
                "images": images_status
            }
        }
    })