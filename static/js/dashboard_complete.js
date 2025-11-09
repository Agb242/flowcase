// Flowcase Complete Dashboard JavaScript
// Combines original features with modern design

// Global variables
let droplets = [];
let instances = [];
let currentView = 'dashboard';
let currentDropletId = null;

// Initialize (Using Original Flowcase Functions)
window.onload = function() {
    UpdateAll();  // Original Flowcase function
    
    // Auto-refresh every 30 seconds (Original)
    setInterval(UpdateAll, 30000);
    
    // Animate body (Original)
    setTimeout(() => {
        document.body.classList.add('active');
    }, 100);
};

// Original Flowcase Functions
function UpdateAll() {
    console.log("Updating all... Time: " + new Date().toLocaleTimeString());
    GetDroplets();
    GetInstances();
}

// Get Droplets (Original Flowcase)
function GetDroplets() {
    var url = "/api/droplets";
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            var json = JSON.parse(xhr.responseText);
            if (json["success"] == true) {
                droplets = json["droplets"] || [];
                UpdateDroplets(json);
            } else {
                if (json["error"] != null) {
                    CreateNotification(json["error"], "error");
                } else {
                    CreateNotification("An error occurred while retrieving the droplets.", "error");
                }
            }
        }
    };
    xhr.send();
    console.log("Retrieving droplets...");
}

// Update Droplets Display (Modified for new design)
function UpdateDroplets(json) {
    var mainDiv = document.getElementById('droplets-grid');
    if (!mainDiv) return;
    
    mainDiv.innerHTML = "";
    
    json["droplets"].forEach(droplet => {
        mainDiv.innerHTML += `
        <div class="droplet-card" onclick="OpenDropletModal('${droplet.id}', '${droplet.display_name}', '${droplet.description ? droplet.description : ""}')">
            <img src="${droplet.image_path ? droplet.image_path : '/static/img/droplet_default.jpg'}" 
                 alt="${droplet.display_name}" 
                 class="droplet-image">
            <div class="droplet-content">
                <div class="droplet-name">${droplet.display_name}</div>
                <div class="droplet-description">${droplet.description || 'Docker container'}</div>
            </div>
        </div> 
        `;
    });
    
    if (json["droplets"].length == 0) {
        mainDiv.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: #64748b;">
            <i class="fas fa-box-open" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
            <h2>No droplets available.</h2>
            {% if userInfo.permissions.perm_admin_panel && userInfo.permissions.perm_edit_droplets && userInfo.permissions.perm_view_registry %}
                <p>Would you like to add some from the registry?</p>
                <button class="btn" onclick="OpenAdminPanel(); AdminChangeTab('registry');">View Registry</button>
            {% endif %}
        </div>
        `;
    }
    
    // Update stats
    document.getElementById('stat-droplets').textContent = json["droplets"].length;
}

// Get Instances (Original Flowcase)
function GetInstances() {
    var url = "/api/instances";
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            var json = JSON.parse(xhr.responseText);
            if (json["success"] == true) {
                instances = json["instances"] || [];
                UpdateInstances(json);
            } else {
                if (json["error"] != null) {
                    CreateNotification(json["error"], "error");
                } else {
                    CreateNotification("An error occurred while retrieving the instances.", "error");
                }
            }
        }
    };
    xhr.send();
    console.log("Retrieving instances...");
}

// Update Instances Display (Original + New)
function UpdateInstances(json) {
    // Update bottom bar (Original style)
    var instancesBar = document.getElementById('instances-bar');
    instancesBar.innerHTML = "";
    
    if (json["instances"].length == 0) {
        instancesBar.classList.remove('active');
        document.querySelector('.main-content').style.marginBottom = "0";
    } else {
        instancesBar.classList.add('active');
        document.querySelector('.main-content').style.marginBottom = "140px";
        
        json["instances"].forEach(instance => {
            instancesBar.innerHTML += `
            <div class="droplet-instance" data-id="${instance.id}">
                <div class="droplet-instance-popup" data-id="${instance.id}">
                    <p class="droplet-instance-popup-title">${instance.droplet.display_name}</p>
                    <img src="/desktop/${instance.id}/vnc/api/get_screenshot?width=256" alt="" 
                         class="droplet-instance-popup-screenshot"
                         onerror="this.src='/static/img/droplet_default.jpg'">
                    <div class="droplet-instance-popup-buttons">
                        <p class="droplet-instance-popup-connect" onclick="window.location.href='/droplet/${instance.id}'">Connect</p>
                        <p class="droplet-instance-popup-destroy" onclick="RequestDestroyInstance('${instance.id}')">Destroy</p>
                    </div>
                </div>
                <img src="${instance.droplet.image_path ? instance.droplet.image_path : '/static/img/droplet_default.jpg'}"
                     alt="${instance.droplet.display_name}" 
                     class="droplet-instance-image droplet-image" 
                     onclick="ToggleInstancePopup('${instance.id}')">
            </div>
            `;
        });
    }
    
    // Also update table
    UpdateInstancesTable(json);
    
    // Update stats
    document.getElementById('stat-instances').textContent = 
        json["instances"].filter(i => i.container_status === 'running').length;
}

// Toggle Instance Popup (Original)
function ToggleInstancePopup(instanceID) {
    var popups = document.querySelectorAll('.droplet-instance-popup');
    popups.forEach(popup => {
        if (popup.dataset.id != instanceID) {
            popup.classList.remove('active');
        }
    });
    
    var popup = document.querySelector('.droplet-instance-popup[data-id="' + instanceID + '"]');
    popup.classList.toggle('active');
}

// View Switching
function switchView(view) {
    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target?.closest('.nav-item')?.classList.add('active');
    
    // Hide all views
    document.querySelectorAll('[id^="view-"]').forEach(v => {
        v.style.display = 'none';
    });
    
    // Show requested view
    const viewElement = document.getElementById(`view-${view}`);
    if (viewElement) {
        viewElement.style.display = 'block';
    }
    
    // Update page title
    const titles = {
        'dashboard': 'Dashboard',
        'droplets': 'Available Droplets',
        'instances': 'My Instances',
        'profile': 'Profile',
        'settings': 'Settings'
    };
    document.getElementById('page-title').textContent = titles[view] || 'Dashboard';
    
    currentView = view;
    
    // Load data for view
    if (view === 'droplets') {
        renderDropletsView();
    } else if (view === 'instances') {
        renderInstancesView();
    }
}

// Load Droplets
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

// Render Droplets in Dashboard
function renderDroplets() {
    const container = document.getElementById('droplets-grid');
    if (!container) return;
    
    if (droplets.length === 0) {
        container.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: #64748b;">
                <i class="fas fa-box-open" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                <p>No droplets available</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = droplets.map(droplet => `
        <div class="droplet-card" onclick="openLaunchModal('${droplet.id}')">
            <img src="${droplet.image_path || '/static/img/droplet_default.jpg'}" 
                 alt="${droplet.display_name}" 
                 class="droplet-image">
            <div class="droplet-content">
                <div class="droplet-name">${droplet.display_name}</div>
                <div class="droplet-description">${droplet.description || 'Docker container'}</div>
            </div>
        </div>
    `).join('');
}

// Render Droplets View (full page)
function renderDropletsView() {
    const container = document.getElementById('view-droplets');
    if (!container) return;
    
    const html = `
        <div class="section">
            <div class="section-header">
                <h2 class="section-title">Browse Available Droplets</h2>
                <div>
                    <input type="text" placeholder="Search droplets..." class="search-input" onkeyup="filterDroplets(this.value)">
                </div>
            </div>
            <div class="droplets-grid" id="droplets-view-grid">
                ${droplets.map(droplet => `
                    <div class="droplet-card" onclick="openLaunchModal('${droplet.id}')">
                        <img src="${droplet.image_path || '/static/img/droplet_default.jpg'}" 
                             alt="${droplet.display_name}" 
                             class="droplet-image">
                        <div class="droplet-content">
                            <div class="droplet-name">${droplet.display_name}</div>
                            <div class="droplet-description">${droplet.description || 'Docker container'}</div>
                            <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem; font-size: 0.75rem; color: #64748b;">
                                <span><i class="fas fa-microchip"></i> ${droplet.container_cores || 2} cores</span>
                                <span><i class="fas fa-memory"></i> ${(droplet.container_memory / 1024).toFixed(1)} GB</span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

// Load Instances
function loadInstances() {
    fetch('/api/instances')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                instances = data.instances || [];
                renderInstances();
                renderInstancesBar();
                updateStats();
            }
        })
        .catch(error => {
            console.error('Error loading instances:', error);
        });
}

// Render Instances Bar (bottom)
function renderInstancesBar() {
    const bar = document.getElementById('instances-bar');
    if (!bar) return;
    
    if (instances.length === 0) {
        bar.classList.remove('active');
        return;
    }
    
    bar.classList.add('active');
    bar.innerHTML = instances.map(instance => `
        <div class="instance-card" data-id="${instance.id}">
            <div class="instance-popup" id="popup-${instance.id}">
                <div class="instance-popup-title">${instance.droplet?.display_name || 'Unknown'}</div>
                <img src="/desktop/${instance.id}/vnc/api/get_screenshot?width=256" 
                     class="instance-popup-screenshot" 
                     onerror="this.src='/static/img/droplet_default.jpg'">
                <div class="instance-popup-actions">
                    <div class="popup-btn popup-btn-connect" onclick="window.location.href='/droplet/${instance.id}'">
                        <i class="fas fa-terminal"></i> Connect
                    </div>
                    <div class="popup-btn popup-btn-destroy" onclick="deleteInstance('${instance.id}')">
                        <i class="fas fa-trash"></i> Destroy
                    </div>
                </div>
            </div>
            <img src="${instance.droplet?.image_path || '/static/img/droplet_default.jpg'}"
                 alt="${instance.droplet?.display_name}"
                 class="instance-image"
                 onclick="toggleInstancePopup('${instance.id}')">
        </div>
    `).join('');
}

// Render Instances in Dashboard
function renderInstances() {
    const container = document.getElementById('instances-list');
    if (!container) return;
    
    if (instances.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #64748b;">
                <i class="fas fa-server" style="font-size: 2rem; margin-bottom: 0.5rem; opacity: 0.5;"></i>
                <p>No active instances</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${instances.map(instance => {
                    const status = instance.container_status || 'stopped';
                    return `
                        <tr>
                            <td style="font-weight: 500; color: white;">${instance.droplet?.display_name || 'Unknown'}</td>
                            <td>${instance.droplet?.droplet_type || 'unknown'}</td>
                            <td>
                                <span class="status-badge status-${status}">
                                    <i class="fas fa-circle"></i> ${status}
                                </span>
                            </td>
                            <td>${formatDate(instance.created_at)}</td>
                            <td>
                                <div style="display: flex; gap: 0.5rem;">
                                    ${status === 'running' ? `
                                        <button class="btn-small" onclick="window.location.href='/droplet/${instance.id}'">
                                            <i class="fas fa-terminal"></i> Connect
                                        </button>
                                        <button class="btn-small btn-secondary" onclick="stopInstance('${instance.id}')">
                                            <i class="fas fa-stop"></i> Stop
                                        </button>
                                    ` : `
                                        <button class="btn-small" onclick="startInstance('${instance.id}')">
                                            <i class="fas fa-play"></i> Start
                                        </button>
                                    `}
                                    <button class="btn-small btn-danger" onclick="deleteInstance('${instance.id}')">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    `;
}

// Render Instances View (full page)
function renderInstancesView() {
    const container = document.getElementById('view-instances');
    if (!container) return;
    
    container.innerHTML = `
        <div class="section">
            <div class="section-header">
                <h2 class="section-title">My Instances</h2>
            </div>
            ${instances.length === 0 ? `
                <div style="text-align: center; padding: 3rem; color: #64748b;">
                    <i class="fas fa-server" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                    <p>No instances running</p>
                    <button class="btn" onclick="switchView('droplets')" style="margin-top: 1rem;">
                        <i class="fas fa-box"></i> Browse Droplets
                    </button>
                </div>
            ` : `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Status</th>
                            <th>Created</th>
                            <th>Uptime</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${instances.map(instance => {
                            const status = instance.container_status || 'stopped';
                            return `
                                <tr>
                                    <td style="font-weight: 500; color: white;">
                                        <i class="fas fa-cube" style="color: #06b6d4; margin-right: 0.5rem;"></i>
                                        ${instance.droplet?.display_name || 'Unknown'}
                                    </td>
                                    <td>
                                        <span class="type-badge type-${instance.droplet?.droplet_type}">
                                            ${instance.droplet?.droplet_type || 'unknown'}
                                        </span>
                                    </td>
                                    <td>
                                        <span class="status-badge status-${status}">
                                            <i class="fas ${status === 'running' ? 'fa-circle' : 'fa-circle'}"></i>
                                            ${status}
                                        </span>
                                    </td>
                                    <td>${formatDate(instance.created_at)}</td>
                                    <td>${calculateUptime(instance.created_at, status)}</td>
                                    <td>
                                        <div style="display: flex; gap: 0.5rem;">
                                            ${status === 'running' ? `
                                                <button class="btn-small" onclick="window.location.href='/droplet/${instance.id}'">
                                                    <i class="fas fa-terminal"></i> Connect
                                                </button>
                                                <button class="btn-small btn-secondary" onclick="stopInstance('${instance.id}')">
                                                    <i class="fas fa-stop"></i> Stop
                                                </button>
                                            ` : `
                                                <button class="btn-small" onclick="startInstance('${instance.id}')">
                                                    <i class="fas fa-play"></i> Start
                                                </button>
                                            `}
                                            <button class="btn-small btn-danger" onclick="deleteInstance('${instance.id}')">
                                                <i class="fas fa-trash"></i> Delete
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            `}
        </div>
    `;
}

// Load Stats
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

// Update Stats
function updateStats() {
    document.getElementById('stat-droplets').textContent = droplets.length;
    document.getElementById('stat-instances').textContent = instances.filter(i => i.container_status === 'running').length;
}

// Open Launch Modal
function openLaunchModal(dropletId) {
    const droplet = droplets.find(d => d.id === dropletId);
    if (!droplet) return;
    
    currentDropletId = dropletId;
    
    document.getElementById('modal-droplet-name').textContent = droplet.display_name;
    document.getElementById('modal-droplet-desc').textContent = droplet.description || 'Docker container';
    document.getElementById('launch-droplet-id').value = dropletId;
    
    // Show/hide resolution selector based on type
    const resolutionGroup = document.getElementById('resolution-group');
    if (droplet.droplet_type === 'vnc' || droplet.droplet_type === 'rdp') {
        resolutionGroup.style.display = 'block';
    } else {
        resolutionGroup.style.display = 'none';
    }
    
    document.getElementById('launch-modal').classList.add('active');
}

// Close Launch Modal
function closeLaunchModal() {
    document.getElementById('launch-modal').classList.remove('active');
    currentDropletId = null;
}

// Launch Instance
function launchInstance() {
    if (!currentDropletId) return;
    
    const resolution = document.getElementById('launch-resolution').value;
    const btn = document.getElementById('launch-btn');
    const originalText = btn.innerHTML;
    
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Launching...';
    
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
            
            if (data.instance_id) {
                window.location.href = `/droplet/${data.instance_id}`;
            }
        } else {
            showNotification('Failed to launch: ' + (data.error || 'Unknown error'), 'error');
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Failed to launch instance', 'error');
        btn.disabled = false;
        btn.innerHTML = originalText;
    });
}

// Instance Actions
function startInstance(instanceId) {
    fetch(`/api/instances/${instanceId}/start`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Instance started', 'success');
                loadInstances();
            }
        });
}

function stopInstance(instanceId) {
    fetch(`/api/instances/${instanceId}/stop`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Instance stopped', 'success');
                loadInstances();
            }
        });
}

function deleteInstance(instanceId) {
    if (!confirm('Are you sure you want to delete this instance?')) return;
    
    fetch(`/api/instance/${instanceId}/destroy`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Instance deleted', 'success');
                loadInstances();
            }
        });
}

// Toggle Instance Popup
function toggleInstancePopup(instanceId) {
    // Close all other popups
    document.querySelectorAll('.instance-popup').forEach(popup => {
        popup.classList.remove('active');
    });
    
    // Toggle this popup
    const popup = document.getElementById(`popup-${instanceId}`);
    if (popup) {
        popup.classList.toggle('active');
    }
}

// User Dropdown
function toggleUserDropdown() {
    document.getElementById('user-dropdown').classList.toggle('active');
}

// Refresh Data
function refreshData() {
    showNotification('Refreshing...', 'info');
    loadDroplets();
    loadInstances();
    loadStats();
}

// Admin Panel
function openAdminPanel(tab) {
    const panel = document.getElementById('admin-panel');
    if (!panel) return;
    
    panel.classList.add('active');
    
    // Switch to tab
    if (tab) {
        adminChangeTab(tab);
    }
}

function closeAdminPanel() {
    const panel = document.getElementById('admin-panel');
    if (panel) {
        panel.classList.remove('active');
    }
}

function adminChangeTab(tab) {
    // Update active nav
    document.querySelectorAll('.admin-nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.tab === tab) {
            item.classList.add('active');
        }
    });
    
    // Load content
    const content = document.getElementById('admin-content');
    if (!content) return;
    
    content.innerHTML = '<div style="padding: 2rem;"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';
    
    // Load admin data based on tab
    switch(tab) {
        case 'system':
            loadAdminSystem();
            break;
        case 'users':
            loadAdminUsers();
            break;
        case 'groups':
            loadAdminGroups();
            break;
        case 'droplets':
            loadAdminDroplets();
            break;
        case 'images':
            loadAdminImages();
            break;
        case 'registry':
            loadAdminRegistry();
            break;
        case 'logs':
            loadAdminLogs();
            break;
    }
}

// Admin Functions (simplified)
function loadAdminSystem() {
    // Load system info
    const content = document.getElementById('admin-content');
    content.innerHTML = `
        <h2>System Information</h2>
        <div class="stats-grid" style="margin-top: 2rem;">
            <div class="stat-card">
                <div class="stat-label">CPU Usage</div>
                <div class="stat-value">45%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Memory Usage</div>
                <div class="stat-value">2.4 GB</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Disk Usage</div>
                <div class="stat-value">65%</div>
            </div>
        </div>
    `;
}

// Utilities
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)} min ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`;
    return date.toLocaleDateString();
}

function calculateUptime(createdAt, status) {
    if (status !== 'running') return '-';
    const created = new Date(createdAt);
    const now = new Date();
    const diff = now - created;
    
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    
    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
}

// Notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type} show`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 
                       type === 'error' ? 'fa-exclamation-circle' : 
                       'fa-info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Mobile sidebar toggle
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('active');
}
