// Flowcase Dashboard - Integrated JavaScript

// Global variables
let droplets = [];
let instances = [];
let currentDropletId = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadDroplets();
    loadInstances();
    loadStats();
    
    // Auto-refresh instances every 30 seconds
    setInterval(loadInstances, 30000);
});

// Load droplets from API
function loadDroplets() {
    fetch('/api/droplets')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                droplets = data.droplets || [];
                renderDroplets();
                updateStats();
            }
        })
        .catch(error => {
            console.error('Error loading droplets:', error);
            showNotification('Failed to load droplets', 'error');
        });
}

// Render droplets grid
function renderDroplets() {
    const grid = document.getElementById('droplets-grid');
    
    if (droplets.length === 0) {
        grid.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <i class="fas fa-box-open"></i>
                <p>No droplets available</p>
                <p style="font-size: 0.875rem;">Contact your administrator to add droplets</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = droplets.map(droplet => {
        const icon = getDropletIcon(droplet.droplet_type);
        const cores = droplet.container_cores || 2;
        const memory = (droplet.container_memory / 1024).toFixed(1);
        const storage = droplet.container_storage || 10;
        
        return `
            <div class="droplet-card" onclick="openLaunchModal('${droplet.id}')">
                <span class="droplet-type-badge type-${droplet.droplet_type}">
                    ${droplet.droplet_type.toUpperCase()}
                </span>
                <div class="droplet-icon">
                    <i class="${icon}"></i>
                </div>
                <div class="droplet-name">${droplet.display_name}</div>
                <div class="droplet-description">${droplet.description || 'Docker container'}</div>
                <div class="droplet-specs">
                    <div class="droplet-spec">
                        <i class="fas fa-microchip"></i>
                        ${cores} cores
                    </div>
                    <div class="droplet-spec">
                        <i class="fas fa-memory"></i>
                        ${memory} GB
                    </div>
                    <div class="droplet-spec">
                        <i class="fas fa-hdd"></i>
                        ${storage} GB
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Load instances from API
function loadInstances() {
    fetch('/api/instances')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                instances = data.instances || [];
                renderInstances();
                updateStats();
            }
        })
        .catch(error => {
            console.error('Error loading instances:', error);
        });
}

// Render instances table
function renderInstances() {
    const tbody = document.getElementById('instances-tbody');
    
    if (instances.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">
                    <i class="fas fa-server"></i>
                    <p>No active instances</p>
                    <p style="font-size: 0.875rem;">Launch a droplet to get started</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = instances.map(instance => {
        const status = instance.container_status || 'stopped';
        const statusClass = `status-${status}`;
        const statusIcon = status === 'running' ? 'fa-circle' : 
                          status === 'starting' ? 'fa-spinner fa-spin' : 'fa-circle';
        const dropletName = instance.droplet?.display_name || 'Unknown';
        const dropletType = instance.droplet?.droplet_type || 'unknown';
        const createdAt = formatDate(instance.created_at);
        
        let actions = '';
        if (status === 'running') {
            actions = `
                <a href="/droplet/${instance.id}" class="action-btn">
                    <i class="fas fa-terminal"></i>
                    Connect
                </a>
                <button class="action-btn" onclick="stopInstance('${instance.id}')">
                    <i class="fas fa-stop"></i>
                    Stop
                </button>
            `;
        } else if (status === 'stopped') {
            actions = `
                <button class="action-btn" onclick="startInstance('${instance.id}')">
                    <i class="fas fa-play"></i>
                    Start
                </button>
            `;
        }
        
        actions += `
            <button class="action-btn danger" onclick="deleteInstance('${instance.id}')">
                <i class="fas fa-trash"></i>
                Delete
            </button>
        `;
        
        return `
            <tr>
                <td class="instance-name">${dropletName}</td>
                <td>${dropletType}</td>
                <td>
                    <span class="instance-status ${statusClass}">
                        <i class="fas ${statusIcon}"></i>
                        ${status.charAt(0).toUpperCase() + status.slice(1)}
                    </span>
                </td>
                <td>${createdAt}</td>
                <td>
                    <div class="instance-actions">
                        ${actions}
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

// Load stats
function loadStats() {
    fetch('/api/droplets/stats')
        .then(response => response.json())
        .then(data => {
            if (data) {
                document.getElementById('stat-cpu').textContent = `${data.cpu_usage || 0}%`;
                document.getElementById('stat-memory').textContent = `${data.memory_usage || 0}%`;
            }
        })
        .catch(error => {
            console.error('Error loading stats:', error);
        });
}

// Update stats
function updateStats() {
    document.getElementById('stat-droplets').textContent = droplets.length;
    document.getElementById('stat-instances').textContent = instances.filter(i => i.container_status === 'running').length;
}

// Open launch modal
function openLaunchModal(dropletId) {
    const droplet = droplets.find(d => d.id === dropletId);
    if (!droplet) return;
    
    currentDropletId = dropletId;
    
    document.getElementById('launch-droplet-id').value = dropletId;
    document.getElementById('launch-droplet-info').innerHTML = `
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div class="droplet-icon" style="width: 48px; height: 48px; font-size: 1.5rem;">
                <i class="${getDropletIcon(droplet.droplet_type)}"></i>
            </div>
            <div>
                <div style="font-weight: 600; color: white;">${droplet.display_name}</div>
                <div style="font-size: 0.875rem; color: #94a3b8;">${droplet.description || 'Docker container'}</div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">
                    ${droplet.container_cores || 2} cores • 
                    ${(droplet.container_memory / 1024).toFixed(1)} GB RAM • 
                    ${droplet.container_storage || 10} GB Storage
                </div>
            </div>
        </div>
    `;
    
    // Show/hide resolution based on droplet type
    const resolutionGroup = document.getElementById('resolution-group');
    if (droplet.droplet_type === 'vnc' || droplet.droplet_type === 'rdp') {
        resolutionGroup.style.display = 'block';
    } else {
        resolutionGroup.style.display = 'none';
    }
    
    document.getElementById('launch-modal').classList.add('active');
}

// Close launch modal
function closeLaunchModal() {
    document.getElementById('launch-modal').classList.remove('active');
    currentDropletId = null;
}

// Launch instance
function launchInstance() {
    if (!currentDropletId) return;
    
    const droplet = droplets.find(d => d.id === currentDropletId);
    if (!droplet) return;
    
    const resolution = document.getElementById('launch-resolution').value;
    const btn = document.querySelector('#launch-modal .btn:last-child');
    const originalText = btn.innerHTML;
    
    // Show loading state
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Launching...';
    
    // Call API to launch instance
    fetch('/api/instance/request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            droplet_id: currentDropletId,
            resolution: resolution
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success || data.instance_id) {
            closeLaunchModal();
            showNotification('Instance launched successfully!', 'success');
            
            // Reload instances after a short delay
            setTimeout(() => {
                loadInstances();
                
                // If we have an instance_id, redirect to viewer
                if (data.instance_id) {
                    window.location.href = `/droplet/${data.instance_id}`;
                }
            }, 1000);
        } else {
            showNotification('Failed to launch instance: ' + (data.error || 'Unknown error'), 'error');
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    })
    .catch(error => {
        console.error('Error launching instance:', error);
        showNotification('Failed to launch instance', 'error');
        btn.disabled = false;
        btn.innerHTML = originalText;
    });
}

// Start instance
function startInstance(instanceId) {
    fetch(`/api/instances/${instanceId}/start`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Instance started successfully', 'success');
            loadInstances();
        } else {
            showNotification('Failed to start instance', 'error');
        }
    })
    .catch(error => {
        console.error('Error starting instance:', error);
        showNotification('Failed to start instance', 'error');
    });
}

// Stop instance
function stopInstance(instanceId) {
    fetch(`/api/instances/${instanceId}/stop`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Instance stopped successfully', 'success');
            loadInstances();
        } else {
            showNotification('Failed to stop instance', 'error');
        }
    })
    .catch(error => {
        console.error('Error stopping instance:', error);
        showNotification('Failed to stop instance', 'error');
    });
}

// Delete instance
function deleteInstance(instanceId) {
    if (!confirm('Are you sure you want to delete this instance?')) return;
    
    fetch(`/api/instance/${instanceId}/destroy`, {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Instance deleted successfully', 'success');
            loadInstances();
        } else {
            showNotification('Failed to delete instance', 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting instance:', error);
        showNotification('Failed to delete instance', 'error');
    });
}

// Refresh droplets
function refreshDroplets() {
    loadDroplets();
    showNotification('Droplets refreshed', 'info');
}

// Refresh instances
function refreshInstances() {
    loadInstances();
    showNotification('Instances refreshed', 'info');
}

// Get droplet icon based on type
function getDropletIcon(type) {
    const icons = {
        'vnc': 'fas fa-desktop',
        'rdp': 'fab fa-windows',
        'ssh': 'fas fa-terminal',
        'http': 'fas fa-globe',
        'default': 'fas fa-cube'
    };
    return icons[type] || icons.default;
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    // Less than 1 minute
    if (diff < 60000) return 'Just now';
    
    // Less than 1 hour
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    }
    
    // Less than 1 day
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    }
    
    // More than 1 day
    const days = Math.floor(diff / 86400000);
    if (days < 7) {
        return `${days} day${days > 1 ? 's' : ''} ago`;
    }
    
    // Format as date
    return date.toLocaleDateString();
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 
                       type === 'error' ? 'fa-exclamation-circle' : 
                       'fa-info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Open admin panel (if exists)
function openAdminPanel() {
    // TODO: Implement admin panel
    alert('Admin panel not yet implemented in integrated dashboard');
}
