"""
Droplet Manager Service
Handles droplet lifecycle with Docker volume persistence
"""

import docker
import os
import json
from datetime import datetime
from pathlib import Path
from models.droplet import Droplet, DropletInstance
from __init__ import db
from utils.logger import log

class DropletManager:
    """Manages droplet instances with persistent storage"""
    
    def __init__(self):
        """Initialize Docker client and volume path"""
        self.docker_client = docker.from_env()
        self.base_volume_path = os.getenv('DROPLET_VOLUME_PATH', '/flowcase/volumes')
        Path(self.base_volume_path).mkdir(parents=True, exist_ok=True)
    
    def create_persistent_volume(self, droplet_id, user_id):
        """Create a Docker volume for persistent storage"""
        try:
            volume_name = f"nalabo_droplet_{droplet_id}_{user_id}"
            
            # Check if volume already exists
            try:
                existing_volume = self.docker_client.volumes.get(volume_name)
                log('INFO', f'Using existing volume: {volume_name}')
                return existing_volume
            except docker.errors.NotFound:
                pass
            
            # Create new volume
            volume = self.docker_client.volumes.create(
                name=volume_name,
                driver='local',
                labels={
                    'nalabo.droplet_id': droplet_id,
                    'nalabo.user_id': user_id,
                    'nalabo.created_at': datetime.utcnow().isoformat()
                }
            )
            
            log('INFO', f'Created persistent volume: {volume_name}')
            return volume
            
        except Exception as e:
            log('ERROR', f'Failed to create volume: {str(e)}')
            raise
    
    def create_instance(self, droplet, user, persist_data=True):
        """
        Create and start a droplet instance with optional persistence
        
        Args:
            droplet: Droplet model instance
            user: User model instance
            persist_data: Enable persistent storage (default: True)
        
        Returns:
            DropletInstance object
        """
        try:
            # Create droplet instance record
            instance = DropletInstance(
                droplet_id=droplet.id,
                user_id=user.id,
                container_status='creating'
            )
            db.session.add(instance)
            db.session.commit()
            
            # Prepare container configuration
            container_name = f"nalabo_{droplet.display_name}_{user.username}_{instance.id[:8]}"
            
            # Setup volumes
            volumes = {}
            volume_ids = []
            
            if persist_data and droplet.persistent_enabled:
                # Create persistent volume
                volume = self.create_persistent_volume(droplet.id, user.id)
                volume_ids.append(volume.name)
                
                # Add volume mount
                mount_point = droplet.container_persistent_profile_path or '/data'
                volumes[volume.name] = {'bind': mount_point, 'mode': 'rw'}
                
                # Add any additional configured volumes
                for vol_config in droplet.get_persistent_volumes():
                    host_path = vol_config.get('host')
                    container_path = vol_config.get('container')
                    if host_path and container_path:
                        volumes[host_path] = {'bind': container_path, 'mode': 'rw'}
            
            # Setup environment variables
            environment = droplet.get_environment_vars()
            environment.update({
                'NALABO_USER': user.username,
                'NALABO_USER_ID': user.id,
                'NALABO_DROPLET_ID': droplet.id,
                'NALABO_INSTANCE_ID': instance.id
            })
            
            # Setup port mapping
            ports = {}
            exposed_ports = droplet.get_exposed_ports()
            if exposed_ports:
                for port in exposed_ports:
                    ports[f'{port}/tcp'] = None  # Random host port
            
            # Resource limits
            mem_limit = f"{droplet.container_memory}m" if droplet.container_memory else "2g"
            cpu_quota = droplet.container_cores * 100000 if droplet.container_cores else None
            
            # Create and start container
            container = self.docker_client.containers.run(
                image=droplet.container_docker_image,
                name=container_name,
                detach=True,
                volumes=volumes,
                environment=environment,
                ports=ports,
                mem_limit=mem_limit,
                cpu_quota=cpu_quota,
                labels={
                    'nalabo.droplet_id': droplet.id,
                    'nalabo.user_id': user.id,
                    'nalabo.instance_id': instance.id,
                    'nalabo.managed': 'true'
                },
                restart_policy={'Name': 'unless-stopped'}
            )
            
            # Update instance with container info
            instance.container_id = container.id
            instance.container_name = container_name
            instance.container_status = 'running'
            instance.set_volume_ids(volume_ids)
            
            # Get assigned port if any
            container.reload()
            if container.ports:
                for port_info in container.ports.values():
                    if port_info:
                        instance.assigned_port = port_info[0]['HostPort']
                        instance.access_url = f"http://localhost:{instance.assigned_port}"
                        break
            
            db.session.commit()
            
            log('INFO', f'Created droplet instance: {instance.id} for user {user.username}')
            return instance
            
        except Exception as e:
            instance.container_status = 'error'
            db.session.commit()
            log('ERROR', f'Failed to create droplet instance: {str(e)}')
            raise
    
    def stop_instance(self, instance_id):
        """Stop a running droplet instance"""
        try:
            instance = DropletInstance.query.get(instance_id)
            if not instance:
                raise ValueError(f'Instance {instance_id} not found')
            
            if instance.container_id:
                try:
                    container = self.docker_client.containers.get(instance.container_id)
                    container.stop(timeout=10)
                    log('INFO', f'Stopped container: {instance.container_id}')
                except docker.errors.NotFound:
                    log('WARNING', f'Container {instance.container_id} not found')
            
            instance.container_status = 'stopped'
            instance.stopped_at = datetime.utcnow()
            db.session.commit()
            
            return True
            
        except Exception as e:
            log('ERROR', f'Failed to stop instance: {str(e)}')
            raise
    
    def delete_instance(self, instance_id, remove_volumes=False):
        """
        Delete a droplet instance
        
        Args:
            instance_id: Instance ID to delete
            remove_volumes: If True, also remove persistent volumes
        """
        try:
            instance = DropletInstance.query.get(instance_id)
            if not instance:
                raise ValueError(f'Instance {instance_id} not found')
            
            # Stop and remove container
            if instance.container_id:
                try:
                    container = self.docker_client.containers.get(instance.container_id)
                    container.stop(timeout=5)
                    container.remove()
                    log('INFO', f'Removed container: {instance.container_id}')
                except docker.errors.NotFound:
                    log('WARNING', f'Container {instance.container_id} not found')
            
            # Remove volumes if requested
            if remove_volumes:
                for volume_id in instance.get_volume_ids():
                    try:
                        volume = self.docker_client.volumes.get(volume_id)
                        volume.remove()
                        log('INFO', f'Removed volume: {volume_id}')
                    except docker.errors.NotFound:
                        log('WARNING', f'Volume {volume_id} not found')
            
            # Remove instance record
            db.session.delete(instance)
            db.session.commit()
            
            log('INFO', f'Deleted droplet instance: {instance_id}')
            return True
            
        except Exception as e:
            log('ERROR', f'Failed to delete instance: {str(e)}')
            raise
    
    def restart_instance(self, instance_id):
        """Restart a droplet instance"""
        try:
            instance = DropletInstance.query.get(instance_id)
            if not instance or not instance.container_id:
                raise ValueError(f'Invalid instance: {instance_id}')
            
            container = self.docker_client.containers.get(instance.container_id)
            container.restart(timeout=10)
            
            instance.container_status = 'running'
            instance.updated_at = datetime.utcnow()
            db.session.commit()
            
            log('INFO', f'Restarted instance: {instance_id}')
            return True
            
        except Exception as e:
            log('ERROR', f'Failed to restart instance: {str(e)}')
            raise
    
    def get_instance_stats(self, instance_id):
        """Get resource usage statistics for an instance"""
        try:
            instance = DropletInstance.query.get(instance_id)
            if not instance or not instance.container_id:
                return None
            
            container = self.docker_client.containers.get(instance.container_id)
            stats = container.stats(stream=False)
            
            # Calculate CPU percentage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0.0
            
            # Calculate memory usage
            memory_usage = stats['memory_stats'].get('usage', 0)
            memory_limit = stats['memory_stats'].get('limit', 0)
            memory_percent = (memory_usage / memory_limit) * 100.0 if memory_limit > 0 else 0.0
            
            return {
                'cpu_percent': round(cpu_percent, 2),
                'memory_usage_mb': round(memory_usage / (1024 * 1024), 2),
                'memory_limit_mb': round(memory_limit / (1024 * 1024), 2),
                'memory_percent': round(memory_percent, 2),
                'network_rx_bytes': stats['networks'].get('eth0', {}).get('rx_bytes', 0),
                'network_tx_bytes': stats['networks'].get('eth0', {}).get('tx_bytes', 0)
            }
            
        except Exception as e:
            log('ERROR', f'Failed to get instance stats: {str(e)}')
            return None
    
    def cleanup_orphaned_containers(self):
        """Remove containers that are no longer tracked in database"""
        try:
            # Get all Nalabo-managed containers
            containers = self.docker_client.containers.list(
                all=True,
                filters={'label': 'nalabo.managed=true'}
            )
            
            cleaned = 0
            for container in containers:
                instance_id = container.labels.get('nalabo.instance_id')
                if instance_id:
                    # Check if instance exists in database
                    instance = DropletInstance.query.get(instance_id)
                    if not instance:
                        container.remove(force=True)
                        log('INFO', f'Removed orphaned container: {container.id}')
                        cleaned += 1
            
            return cleaned
            
        except Exception as e:
            log('ERROR', f'Failed to cleanup orphaned containers: {str(e)}')
            return 0
    
    def list_volumes(self, droplet_id=None):
        """List all volumes, optionally filtered by droplet"""
        try:
            filters = {'label': 'nalabo.managed=true'}
            if droplet_id:
                filters['label'] = f'nalabo.droplet_id={droplet_id}'
            
            volumes = self.docker_client.volumes.list(filters=filters)
            
            volume_info = []
            for vol in volumes:
                volume_info.append({
                    'name': vol.name,
                    'driver': vol.attrs.get('Driver'),
                    'mountpoint': vol.attrs.get('Mountpoint'),
                    'labels': vol.attrs.get('Labels', {}),
                    'size': self._get_volume_size(vol)
                })
            
            return volume_info
            
        except Exception as e:
            log('ERROR', f'Failed to list volumes: {str(e)}')
            return []
    
    def _get_volume_size(self, volume):
        """Estimate volume size (requires root access)"""
        try:
            # This is a placeholder - actual implementation would require
            # more complex volume size calculation
            return "Unknown"
        except:
            return "Unknown"

# Global instance (lazy loaded)
_droplet_manager_instance = None

class _DropletManagerProxy:
    """Proxy to lazy load DropletManager"""
    def __getattr__(self, name):
        global _droplet_manager_instance
        if _droplet_manager_instance is None:
            _droplet_manager_instance = DropletManager()
        return getattr(_droplet_manager_instance, name)

# Global proxy instance
droplet_manager = _DropletManagerProxy()
