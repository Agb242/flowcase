#!/usr/bin/env python3
"""
Create test droplets for Flowcase/Nalabo
"""

from __init__ import db, create_app
from models.droplet import Droplet

def create_test_droplets():
    """Create sample droplets for testing"""
    
    droplets = [
        {
            "id": "ubuntu-desktop-vnc",
            "display_name": "Ubuntu Desktop",
            "description": "Ubuntu 22.04 with XFCE desktop environment",
            "droplet_type": "vnc",
            "is_active": True,
            "container_docker_image": "ubuntu:22.04",
            "container_docker_registry": "docker.io",
            "container_cores": 2,
            "container_memory": 2048,
            "container_storage": 10,
            "container_persistent_profile_path": "/flowcase/profiles/{user_id}/ubuntu-desktop",
            "server_ip": "localhost",
            "server_port": 5901,
            "server_username": "flowcase",
            "server_password": "password"
        },
        {
            "id": "vscode-server",
            "display_name": "VS Code Server",
            "description": "Web-based VS Code development environment",
            "droplet_type": "http",
            "is_active": True,
            "container_docker_image": "codercom/code-server:latest",
            "container_docker_registry": "docker.io",
            "container_cores": 2,
            "container_memory": 4096,
            "container_storage": 20,
            "container_persistent_profile_path": "/flowcase/profiles/{user_id}/vscode",
            "server_ip": "localhost",
            "server_port": 8080,
            "server_username": "",
            "server_password": ""
        },
        {
            "id": "jupyter-notebook",
            "display_name": "Jupyter Notebook",
            "description": "Interactive Python notebook environment",
            "droplet_type": "http",
            "is_active": True,
            "container_docker_image": "jupyter/base-notebook:latest",
            "container_docker_registry": "docker.io",
            "container_cores": 2,
            "container_memory": 2048,
            "container_storage": 10,
            "container_persistent_profile_path": "/flowcase/profiles/{user_id}/jupyter",
            "server_ip": "localhost",
            "server_port": 8888,
            "server_username": "",
            "server_password": ""
        },
        {
            "id": "ubuntu-ssh",
            "display_name": "Ubuntu SSH Server",
            "description": "Ubuntu 22.04 with SSH access",
            "droplet_type": "ssh",
            "is_active": True,
            "container_docker_image": "ubuntu:22.04",
            "container_docker_registry": "docker.io",
            "container_cores": 1,
            "container_memory": 1024,
            "container_storage": 5,
            "container_persistent_profile_path": "",
            "server_ip": "localhost",
            "server_port": 22,
            "server_username": "root",
            "server_password": "password"
        },
        {
            "id": "nginx-webserver",
            "display_name": "Nginx Web Server",
            "description": "Nginx web server for hosting static websites",
            "droplet_type": "http",
            "is_active": True,
            "container_docker_image": "nginx:alpine",
            "container_docker_registry": "docker.io",
            "container_cores": 1,
            "container_memory": 512,
            "container_storage": 5,
            "container_persistent_profile_path": "/flowcase/profiles/{user_id}/nginx",
            "server_ip": "localhost",
            "server_port": 80,
            "server_username": "",
            "server_password": ""
        }
    ]
    
    # Create each droplet
    for droplet_data in droplets:
        # Check if droplet already exists
        existing = Droplet.query.filter_by(id=droplet_data['id']).first()
        if not existing:
            droplet = Droplet(**droplet_data)
            db.session.add(droplet)
            print(f"✅ Created droplet: {droplet_data['display_name']}")
        else:
            print(f"⚠️  Droplet already exists: {droplet_data['display_name']}")
    
    # Commit changes
    db.session.commit()
    print("\n✅ Test droplets created successfully!")
    print("📝 Available droplet types:")
    print("   - VNC: Ubuntu Desktop")
    print("   - SSH: Ubuntu Server")
    print("   - HTTP: VS Code, Jupyter, Nginx")

if __name__ == "__main__":
    # Create app context
    app = create_app()
    
    with app.app_context():
        print("🚀 Creating test droplets for Flowcase/Nalabo...")
        create_test_droplets()
