import uuid
import json
from sqlalchemy.sql import func
from __init__ import db

class Droplet(db.Model):
	"""Droplet model with enhanced persistence support"""
	id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
	tenant_id = db.Column(db.String(36), db.ForeignKey('tenant.id'), nullable=True)
	display_name = db.Column(db.String(80), nullable=False)
	description = db.Column(db.String(255), nullable=True)
	image_path = db.Column(db.String(255), nullable=True)
	droplet_type = db.Column(db.String(80), nullable=False)
	
	# Docker Configuration
	container_docker_image = db.Column(db.String(255), nullable=True)
	container_docker_registry = db.Column(db.String(255), nullable=True)
	container_cores = db.Column(db.Integer, nullable=True, default=2)
	container_memory = db.Column(db.Integer, nullable=True, default=2048)  # MB
	container_storage = db.Column(db.Integer, nullable=True, default=10)  # GB
	
	# Persistence Configuration
	container_persistent_profile_path = db.Column(db.String(255), nullable=True)
	persistent_volumes = db.Column(db.Text, nullable=True)  # JSON: [{"host": "/path", "container": "/path"}]
	persistent_enabled = db.Column(db.Boolean, default=False)
	volume_size_limit = db.Column(db.Integer, nullable=True)  # MB
	
	# Network Configuration
	server_ip = db.Column(db.String(255), nullable=True)
	server_port = db.Column(db.Integer, nullable=True)
	server_username = db.Column(db.String(255), nullable=True)
	server_password = db.Column(db.String(255), nullable=True)
	exposed_ports = db.Column(db.Text, nullable=True)  # JSON: [8080, 3000]
	
	# Environment & Labels
	environment_vars = db.Column(db.Text, nullable=True)  # JSON: {"KEY": "value"}
	docker_labels = db.Column(db.Text, nullable=True)  # JSON: {"label": "value"}
	
	# Metadata
	created_at = db.Column(db.DateTime, server_default=func.now())
	updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
	is_active = db.Column(db.Boolean, default=True)
	
	def get_persistent_volumes(self):
		"""Parse and return persistent volumes as list"""
		if self.persistent_volumes:
			try:
				return json.loads(self.persistent_volumes)
			except:
				return []
		return []
	
	def set_persistent_volumes(self, volumes_list):
		"""Set persistent volumes from list"""
		self.persistent_volumes = json.dumps(volumes_list)
	
	def get_environment_vars(self):
		"""Parse and return environment variables as dict"""
		if self.environment_vars:
			try:
				return json.loads(self.environment_vars)
			except:
				return {}
		return {}
	
	def set_environment_vars(self, env_dict):
		"""Set environment variables from dict"""
		self.environment_vars = json.dumps(env_dict)
	
	def get_exposed_ports(self):
		"""Parse and return exposed ports as list"""
		if self.exposed_ports:
			try:
				return json.loads(self.exposed_ports)
			except:
				return []
		return []
	
	def to_dict(self):
		"""Convert droplet to dictionary"""
		return {
			'id': self.id,
			'tenant_id': self.tenant_id,
			'display_name': self.display_name,
			'description': self.description,
			'image_path': self.image_path,
			'droplet_type': self.droplet_type,
			'container_docker_image': self.container_docker_image,
			'persistent_enabled': self.persistent_enabled,
			'persistent_volumes': self.get_persistent_volumes(),
			'environment_vars': self.get_environment_vars(),
			'exposed_ports': self.get_exposed_ports(),
			'is_active': self.is_active,
			'created_at': self.created_at.isoformat() if self.created_at else None,
			'updated_at': self.updated_at.isoformat() if self.updated_at else None
		}

class DropletInstance(db.Model):
	"""Running instance of a droplet with container metadata"""
	id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
	droplet_id = db.Column(db.String(36), db.ForeignKey('droplet.id'), nullable=False)
	user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
	
	# Container Information
	container_id = db.Column(db.String(255), nullable=True)  # Docker container ID
	container_name = db.Column(db.String(255), nullable=True)
	container_status = db.Column(db.String(50), default='created')  # created, running, stopped, error
	
	# Volume Information
	volume_ids = db.Column(db.Text, nullable=True)  # JSON: ["volume_id_1", "volume_id_2"]
	volume_path = db.Column(db.String(255), nullable=True)  # Host path for persistent data
	
	# Network Information
	assigned_port = db.Column(db.Integer, nullable=True)
	access_url = db.Column(db.String(255), nullable=True)
	
	# Timestamps
	created_at = db.Column(db.DateTime, server_default=func.now())
	updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
	last_accessed = db.Column(db.DateTime, nullable=True)
	stopped_at = db.Column(db.DateTime, nullable=True)
	
	def get_volume_ids(self):
		"""Parse and return volume IDs as list"""
		if self.volume_ids:
			try:
				return json.loads(self.volume_ids)
			except:
				return []
		return []
	
	def set_volume_ids(self, volume_list):
		"""Set volume IDs from list"""
		self.volume_ids = json.dumps(volume_list)
	
	def to_dict(self):
		"""Convert instance to dictionary"""
		return {
			'id': self.id,
			'droplet_id': self.droplet_id,
			'user_id': self.user_id,
			'container_id': self.container_id,
			'container_name': self.container_name,
			'container_status': self.container_status,
			'volume_ids': self.get_volume_ids(),
			'access_url': self.access_url,
			'created_at': self.created_at.isoformat() if self.created_at else None,
			'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None
		} 