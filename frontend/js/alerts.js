// Alerts page functionality
const API_BASE = '/api';
document.addEventListener('DOMContentLoaded', function() {
    loadAllAlerts();
    setupAlertFilters();
});

async function loadAllAlerts(severity = null) {
    try {
        let url = '/api/alerts/';
        if (severity) {
            url += `?severity=${severity}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        displayAlerts(data.alerts);
        updateAlertCount(data.count);
        
    } catch (error) {
        console.error('Alerts load error:', error);
        showToast('Failed to load alerts', 'danger');
    }
}

function displayAlerts(alerts) {
    const container = document.getElementById('alertsContainer');
    if (!container) return;
    
    if (!alerts || alerts.length === 0) {
        container.innerHTML = `
            <div class="col-12">
                <div class="glass-card p-5 text-center">
                    <i class="bi bi-check-circle-fill text-success fs-1 mb-3"></i>
                    <h4>No Alerts Found</h4>
                    <p class="text-muted">No security alerts detected in the system.</p>
                </div>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    alerts.forEach(alert => {
        const time = new Date(alert.timestamp).toLocaleString();
        const severityClass = `severity-${alert.severity}`;
        const mitreBadges = (alert.mitre_techniques || []).map(tech => 
            `<span class="badge mitre-badge me-1">${tech}</span>`
        ).join('');
        
        html += `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="glass-card p-3 alert-card" onclick="showAlertDetails('${alert.id}')">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="severity-badge ${severityClass}">${alert.severity.toUpperCase()}</span>
                        <small class="text-muted">${time}</small>
                    </div>
                    <h6 class="mb-2">${alert.description}</h6>
                    <div class="mb-2">
                        <small class="text-muted">Source:</small>
                        <code class="ms-2">${alert.source_ip}</code>
                    </div>
                    <div class="mb-2">
                        <small class="text-muted">Destination:</small>
                        <code class="ms-2">${alert.destination_ip}</code>
                    </div>
                    <div class="mb-2">
                        ${mitreBadges}
                    </div>
                    <div class="d-flex justify-content-between align-items-center mt-3">
                        <span class="text-warning">Risk: ${alert.risk_score}/100</span>
                        <button class="btn btn-sm btn-outline-primary" onclick="event.stopPropagation(); assignAlert('${alert.id}')">
                            <i class="bi bi-person-plus"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function updateAlertCount(count) {
    const countElement = document.getElementById('totalAlertCount');
    if (countElement) {
        countElement.textContent = count;
    }
}

function setupAlertFilters() {
    const filterButtons = document.querySelectorAll('.alert-filter');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const severity = this.getAttribute('data-severity');
            loadAllAlerts(severity === 'all' ? null : severity);
            
            // Update active state
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

function assignAlert(alertId) {
    fetch(`/api/alerts/${alertId}/assign`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ assignee: 'Me' })
    })
    .then(response => response.json())
    .then(data => {
        showToast('Alert assigned successfully', 'success');
        loadAllAlerts();
    })
    .catch(error => {
        console.error('Assign error:', error);
        showToast('Failed to assign alert', 'danger');
    });
}

function clearAllAlerts() {
    if (confirm('Are you sure you want to clear all alerts?')) {
        fetch('/api/alerts/clear', {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            showToast('All alerts cleared', 'info');
            loadAllAlerts();
        })
        .catch(error => {
            console.error('Clear error:', error);
            showToast('Failed to clear alerts', 'danger');
        });
    }
}

// Export functions for HTML
window.loadAllAlerts = loadAllAlerts;
window.assignAlert = assignAlert;
window.clearAllAlerts = clearAllAlerts;