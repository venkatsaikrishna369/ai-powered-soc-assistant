// Network Security Dashboard JavaScript
// Use the current origin so dashboard works whether served via backend or static server
const API_BASE = window.location.origin + '/api';
let charts = {};
let autoRefresh = true;
let refreshInterval = 10000; // 10 seconds
let chartInitialized = false;

// DISABLE ALL Chart.js animations globally
Chart.defaults.animation = false;
Chart.defaults.transitions = {
    active: {
        animation: {
            duration: 0
        }
    },
    resize: {
        animation: {
            duration: 0
        }
    }
};
Chart.defaults.responsive = false;
Chart.defaults.maintainAspectRatio = false;

console.log('API_BASE ->', API_BASE);

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Dashboard initializing...');
    
    // Apply immediate CSS fixes
    applyChartCSSFixes();
    
    // Test API connection
    testApiConnection();
    
    // Load dashboard data
    loadDashboard();
    
    // Set up auto-refresh for everything EXCEPT charts
    if (autoRefresh) {
        setInterval(() => {
            refreshDashboardWithoutChartJump();
        }, refreshInterval);
    }
    
    // Set up event listeners
    setupEventListeners();
    
    // Simulate initial threats
    setTimeout(() => {
        simulateInitialThreats();
    }, 2000);
});

// Apply CSS fixes for charts
function applyChartCSSFixes() {
    // Force all chart containers to be exact size
    setTimeout(() => {
        const containers = document.querySelectorAll('.chart-container');
        containers.forEach(container => {
            container.style.width = '100%';
            container.style.height = '250px';
            container.style.position = 'relative';
        });
        
        const canvases = document.querySelectorAll('canvas');
        canvases.forEach(canvas => {
            canvas.style.width = '100%';
            canvas.style.height = '250px';
            canvas.style.position = 'absolute';
            canvas.style.left = '0';
            canvas.style.top = '0';
        });
    }, 100);
}

// Refresh dashboard WITHOUT touching charts
async function refreshDashboardWithoutChartJump() {
    console.log('🔄 Refreshing dashboard (static mode)...');
    
    // Update timestamp
    updateTimestamp();
    
    // Load stats, alerts, intel, logs WITHOUT touching charts
    await Promise.all([
        loadStats(),
        loadRecentAlerts(),
        loadThreatIntelligence(),
        loadRealTimeLogs()
    ]);
    
    console.log('✅ Dashboard refreshed (charts static)');
}

// Test API connection
async function testApiConnection() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        if (response.ok) {
            const data = await response.json();
            console.log('✅ API Connected:', data);
            return true;
        }
    } catch (error) {
        console.error('❌ API Connection failed:', error);
        showError('API Connection failed - using demo data');
        return false;
    }
}

// Load all dashboard data (initial load only)
async function loadDashboard() {
    try {
        console.log('🔄 Loading dashboard data...');
        
        // Update timestamp
        updateTimestamp();
        
        // Load all data including charts (only on initial load)
        await Promise.all([
            loadStats(),
            loadCharts(),
            loadRecentAlerts(),
            loadThreatIntelligence(),
            loadRealTimeLogs()
        ]);
        
        console.log('✅ Dashboard data loaded');
        
    } catch (error) {
        console.error('❌ Dashboard load error:', error);
        showError('Failed to load dashboard data');
    }
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/dashboard/stats`);
        if (response.ok) {
            const data = await response.json();
            console.debug('Stats response:', data);
            // Update stat cards
            document.getElementById('totalAlerts').textContent = data.total_alerts || 0;
            document.getElementById('criticalAlerts').textContent = data.critical || 0;
            document.getElementById('avgRiskScore').textContent = data.avg_risk_score || 0;
            document.getElementById('mitreCount').textContent = data.mitre_count || 0;
            document.getElementById('activeThreats').textContent = data.active_threats || 0;
            document.getElementById('responseTime').textContent = `${data.response_time || 0}m`;
            document.getElementById('alertTrend').textContent = `${data.alert_trend || 0}%`;
            document.getElementById('topTechnique').textContent = data.top_technique || 'T1046';
            document.getElementById('criticalResponse').textContent = data.critical_response || 0;
            
            console.log('✅ Stats loaded');
        } else {
            console.warn('Stats endpoint returned', response.status, await response.text());
        }
    } catch (error) {
        console.error('❌ Stats error:', error);
    }
}

// Load charts data - ONLY ON INITIAL LOAD
async function loadCharts() {
    if (chartInitialized) return;
    
    try {
        const response = await fetch(`${API_BASE}/dashboard/charts`);
        if (response.ok) {
            const data = await response.json();
            
            // Create charts only once
            if (!chartInitialized) {
                setTimeout(() => {
                    createTimelineChart(data.threat_timeline);
                    createAttackTypesChart(data.attack_types);
                    createGeoChart(data.top_countries);
                    chartInitialized = true;
                }, 500); // Give more time for DOM to settle
            }
            
            console.log('✅ Charts loaded (initial only)');
        }
    } catch (error) {
        console.error('❌ Charts error:', error);
    }
}

// Create timeline chart - UPDATED TO FILL FULL WIDTH
function createTimelineChart(chartData) {
    const canvas = document.getElementById('threatTimelineChart');
    if (!canvas) return;
    
    console.log('📈 Creating timeline chart...');
    
    // Get container
    const container = canvas.parentElement;
    
    // Set container dimensions
    container.style.width = '100%';
    container.style.height = '250px';
    
    // Set canvas dimensions to match container
    canvas.width = container.clientWidth;
    canvas.height = 250;
    
    // Apply inline styles
    canvas.style.width = '100%';
    canvas.style.height = '250px';
    
    // Prepare data
    const labels = chartData.labels || [];
    const dataPoints = chartData.data || [];
    
    // Calculate FIXED y-axis range
    const maxValue = Math.max(...dataPoints, 1);
    const yAxisMax = Math.max(20, Math.ceil(maxValue * 1.2));
    
    // Clear any previous chart
    if (charts.timeline) {
        try {
            charts.timeline.destroy();
        } catch(e) {
            // Ignore
        }
    }
    
    // Create chart with MANUAL width control
    charts.timeline = new Chart(canvas.getContext('2d'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Threats',
                data: dataPoints,
                borderColor: '#4361ee',
                backgroundColor: 'rgba(67, 97, 238, 0.1)',
                borderWidth: 3,
                tension: 0.3,
                fill: true,
                pointBackgroundColor: '#4361ee',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 4
            }]
        },
        options: {
            // CRITICAL: Disable ALL responsive behavior
            responsive: false,
            maintainAspectRatio: false,
            
            // CRITICAL: Disable ALL animations
            animation: {
                duration: 0
            },
            
            // CRITICAL: Disable ALL transitions
            transitions: {
                active: {
                    animation: {
                        duration: 0
                    }
                },
                resize: {
                    animation: {
                        duration: 0
                    }
                }
            },
            
            plugins: {
                legend: { 
                    display: false 
                },
                tooltip: {
                    enabled: true,
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#94a3b8',
                    bodyColor: '#e2e8f0',
                    borderColor: '#4361ee',
                    borderWidth: 1,
                    cornerRadius: 6,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `Threats: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'category',
                    offset: false, // This removes extra padding
                    bounds: 'ticks',
                    grid: { 
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false,
                        drawTicks: true
                    },
                    ticks: { 
                        color: '#94a3b8',
                        maxTicksLimit: 8, // Show fewer labels
                        autoSkip: true,
                        maxRotation: 0,
                        minRotation: 0,
                        padding: 0,
                        align: 'center',
                        callback: function(value, index, values) {
                            // Show every 3rd label for better spacing
                            return index % 3 === 0 ? this.getLabelForValue(value) : '';
                        }
                    },
                    afterFit: function(scale) {
                        scale.width = canvas.width; // Force full width
                    }
                },
                y: {
                    beginAtZero: true,
                    min: 0,
                    max: yAxisMax,
                    offset: false, // This removes extra padding
                    bounds: 'ticks',
                    grid: { 
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: { 
                        color: '#94a3b8',
                        stepSize: Math.max(5, Math.floor(yAxisMax / 4)),
                        padding: 5,
                        callback: function(value) {
                            return value;
                        }
                    },
                    afterFit: function(scale) {
                        scale.width = 40; // Fixed width for y-axis
                    }
                }
            },
            elements: {
                line: {
                    tension: 0.3
                },
                point: {
                    radius: 4,
                    hoverRadius: 4
                }
            },
            layout: {
                padding: {
                    left: 0,
                    right: 0,
                    top: 10,
                    bottom: 5
                }
            }
        }
    });
    
    console.log('✅ Timeline chart created');
}

// Create attack types chart
function createAttackTypesChart(chartData) {
    const canvas = document.getElementById('attackTypeChart');
    if (!canvas) return;
    
    // Get container
    const container = canvas.parentElement;
    container.style.width = '100%';
    container.style.height = '250px';
    
    // Set canvas dimensions
    canvas.width = container.clientWidth;
    canvas.height = 250;
    
    const colors = ['#f72585', '#4361ee', '#4cc9f0', '#f8961e', '#7209b7', '#06d6a0'];
    
    if (charts.attackTypes) {
        charts.attackTypes.destroy();
    }
    
    charts.attackTypes = new Chart(canvas.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: chartData.labels || [],
            datasets: [{
                data: chartData.data || [],
                backgroundColor: colors,
                borderColor: colors.map(c => `${c}80`),
                borderWidth: 1
            }]
        },
        options: {
            responsive: false,
            maintainAspectRatio: false,
            animation: {
                duration: 0
            },
            plugins: {
                legend: {
                    position: 'right',
                    labels: { 
                        color: '#94a3b8',
                        padding: 15,
                        font: {
                            size: 11
                        }
                    }
                }
            },
            layout: {
                padding: {
                    left: 0,
                    right: 0,
                    top: 0,
                    bottom: 0
                }
            },
            cutout: '65%'
        }
    });
}

// Create geo chart
function createGeoChart(chartData) {
    const container = document.getElementById('geoChart');
    if (!container) return;
    
    // Clear container and set dimensions
    container.innerHTML = '';
    container.style.width = '100%';
    container.style.height = '250px';
    container.style.position = 'relative';
    
    // Create canvas
    const canvas = document.createElement('canvas');
    canvas.id = 'geoChartCanvas';
    canvas.style.width = '100%';
    canvas.style.height = '250px';
    container.appendChild(canvas);
    
    // Set canvas dimensions
    canvas.width = container.clientWidth;
    canvas.height = 250;
    
    if (charts.geo) {
        charts.geo.destroy();
    }
    
    charts.geo = new Chart(canvas.getContext('2d'), {
        type: 'bar',
        data: {
            labels: chartData.labels || [],
            datasets: [{
                label: 'Attacks',
                data: chartData.data || [],
                backgroundColor: 'rgba(67, 97, 238, 0.7)',
                borderColor: '#4361ee',
                borderWidth: 1,
                borderRadius: 4,
                barPercentage: 0.8,
                categoryPercentage: 0.9
            }]
        },
        options: {
            responsive: false,
            maintainAspectRatio: false,
            animation: {
                duration: 0
            },
            plugins: { 
                legend: { 
                    display: false 
                } 
            },
            scales: {
                x: {
                    grid: { 
                        display: false,
                        drawBorder: false
                    },
                    ticks: { 
                        color: '#94a3b8',
                        font: {
                            size: 11
                        },
                        maxRotation: 0,
                        minRotation: 0
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: { 
                        color: 'rgba(255, 255, 255, 0.1)',
                        drawBorder: false
                    },
                    ticks: { 
                        color: '#94a3b8',
                        precision: 0,
                        font: {
                            size: 11
                        },
                        padding: 5
                    }
                }
            },
            layout: {
                padding: {
                    left: 0,
                    right: 0,
                    top: 10,
                    bottom: 0
                }
            }
        }
    });
}

// Load recent alerts
async function loadRecentAlerts() {
    try {
        const response = await fetch(`${API_BASE}/dashboard/recent-alerts?limit=10`);
        if (response.ok) {
            const data = await response.json();
            
            updateAlertFeed(data.alerts || []);
            document.getElementById('newAlertsCount').textContent = `${data.new_alerts_count || 0} NEW`;
            
            console.log('✅ Alerts loaded');
        }
    } catch (error) {
        console.error('❌ Alerts error:', error);
    }
}

// Update alert feed
function updateAlertFeed(alerts) {
    const feed = document.getElementById('alertFeed');
    if (!feed) return;
    
    if (!alerts || alerts.length === 0) {
        feed.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="bi bi-check-circle-fill fs-1 mb-2"></i>
                <p class="mb-0">No alerts detected</p>
                <small>All systems operational</small>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    alerts.forEach(alert => {
        const time = new Date(alert.time || Date.now()).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        const severity = alert.severity || 'info';
        const severityClass = `severity-${severity}`;
        
        const mitreBadges = (alert.mitre_techniques || []).slice(0, 2).map(tech => 
            `<span class="badge mitre-badge me-1">${tech}</span>`
        ).join('');
        
        html += `
            <div class="alert-row p-3 border-bottom border-secondary" 
                 onclick="showAlertDetails('${alert.id}')"
                 style="cursor: pointer;">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="severity-badge ${severityClass}">
                        ${severity.toUpperCase()}
                    </span>
                    <small class="text-muted">${time}</small>
                </div>
                <div class="mb-2">
                    <div class="d-flex align-items-center mb-1">
                        <i class="bi bi-pc me-2"></i>
                        <code class="small">${alert.source_ip || 'Unknown'}</code>
                        <i class="bi bi-arrow-right mx-2"></i>
                        <code class="small">${alert.destination_ip || 'Unknown'}</code>
                    </div>
                    <p class="small mb-1">${alert.description || 'No description'}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <div>${mitreBadges}</div>
                        <div class="risk-meter">
                            <div class="risk-fill ${severityClass}" 
                                 style="width: ${alert.risk_score || 50}%"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    feed.innerHTML = html;
}

// Load threat intelligence
async function loadThreatIntelligence() {
    try {
        const response = await fetch(`${API_BASE}/dashboard/threat-intelligence`);
        if (response.ok) {
            const data = await response.json();
            
            // Update sections
            document.getElementById('rootCause').textContent = data.root_cause || 'Analysis in progress...';
            
            // Update MITRE mapping
            const mitreContainer = document.getElementById('mitreMapping');
            if (mitreContainer) {
                mitreContainer.innerHTML = (data.mitre_mapping || []).map(tech => 
                    `<span class="badge mitre-badge me-1 mb-1">${tech}</span>`
                ).join('');
            }
            
            // Update recommended actions
            const actionsContainer = document.getElementById('recommendedActions');
            if (actionsContainer) {
                actionsContainer.innerHTML = (data.recommended_actions || []).map(action => 
                    `<li>${action}</li>`
                ).join('');
            }
            
            console.log('✅ Threat intelligence loaded');
        }
    } catch (error) {
        console.error('❌ Threat intel error:', error);
    }
}

// Load real-time logs
async function loadRealTimeLogs() {
    try {
        const response = await fetch(`${API_BASE}/dashboard/logs/stream`);
        if (response.ok) {
            const data = await response.json();
            
            const container = document.getElementById('logMonitor');
            if (!container) return;
            
            let html = '';
            (data.logs || []).forEach(log => {
                const actionClass = log.action === 'ALLOW' ? 'text-success' : 'text-danger';
                html += `
                    <div class="log-entry">
                        <span class="text-muted">[${log.timestamp}]</span>
                        <span class="text-info"> ${log.source}</span>
                        <span class="text-muted"> → </span>
                        <span class="text-warning">${log.dest}</span>
                        <span class="text-muted"> (${log.protocol})</span>
                        <span class="${actionClass}"> ${log.action}</span>
                        <span class="text-muted"> ${log.bytes} bytes</span>
                    </div>
                `;
            });
            
            container.innerHTML = html;
            container.scrollTop = container.scrollHeight;
            
            console.log('✅ Logs loaded');
        }
    } catch (error) {
        console.error('❌ Logs error:', error);
    }
}

// Show alert details
async function showAlertDetails(alertId) {
    try {
        const response = await fetch(`${API_BASE}/alerts/${alertId}`);
        if (response.ok) {
            const alert = await response.json();
            
            const modalTitle = document.getElementById('alertModalTitle');
            const modalContent = document.getElementById('alertDetailContent');
            
            modalTitle.textContent = `Alert ${alert.id}`;
            
            const mitreBadges = (alert.mitre_techniques || []).map(tech => 
                `<span class="badge mitre-badge me-1">${tech}</span>`
            ).join('');
            
            modalContent.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6>Alert Information</h6>
                        <table class="table table-dark table-sm">
                            <tr><th>Alert ID:</th><td>${alert.id}</td></tr>
                            <tr><th>Severity:</th><td><span class="badge severity-${alert.severity}">${alert.severity.toUpperCase()}</span></td></tr>
                            <tr><th>Timestamp:</th><td>${new Date(alert.timestamp).toLocaleString()}</td></tr>
                            <tr><th>Risk Score:</th><td>${alert.risk_score || 0}/100</td></tr>
                            <tr><th>Confidence:</th><td>${((alert.confidence || 0) * 100).toFixed(1)}%</td></tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h6>Network Details</h6>
                        <table class="table table-dark table-sm">
                            <tr><th>Source IP:</th><td><code>${alert.source_ip}</code></td></tr>
                            <tr><th>Destination IP:</th><td><code>${alert.destination_ip}</code></td></tr>
                            <tr><th>Protocol:</th><td>${alert.protocol}</td></tr>
                            <tr><th>Ports:</th><td>${alert.source_port} → ${alert.destination_port}</td></tr>
                        </table>
                    </div>
                </div>
                
                <div class="mt-3">
                    <h6>MITRE ATT&CK Mapping</h6>
                    <div class="d-flex flex-wrap gap-2 mb-3">
                        ${mitreBadges}
                    </div>
                    
                    <h6>AI Analysis</h6>
                    <div class="alert alert-dark">
                        ${alert.llm_analysis || alert.description}
                    </div>
                    
                    <h6>Recommended Actions</h6>
                    <ul>
                        ${(alert.recommended_actions || []).map(action => `<li>${action}</li>`).join('')}
                    </ul>
                </div>
            `;
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('alertDetailModal'));
            modal.show();
        }
    } catch (error) {
        console.error('❌ Alert details error:', error);
        showError('Failed to load alert details');
    }
}

// Simulate initial threats
async function simulateInitialThreats() {
    try {
        const response = await fetch(`${API_BASE}/dashboard/simulate-threats?count=5`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Initial threats simulated:', data.message);
            showToast('Initial threats simulated', 'info');
            
            // Refresh dashboard but not charts
            refreshDashboardWithoutChartJump();
        }
    } catch (error) {
        console.error('❌ Simulation error:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Alert search
    const searchInput = document.getElementById('alertSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            filterAlerts(e.target.value);
        });
    }
}

// Filter alerts in the feed
function filterAlerts(searchTerm) {
    const alerts = document.querySelectorAll('.alert-row');
    const term = searchTerm.toLowerCase();
    
    alerts.forEach(alert => {
        const text = alert.textContent.toLowerCase();
        alert.style.display = text.includes(term) ? 'block' : 'none';
    });
}

// Update timestamp
function updateTimestamp() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('lastUpdateTime').textContent = timeStr;
}

// Show error message
function showError(message) {
    console.error('❌ Error:', message);
}

// Show toast notification
function showToast(message, type = 'info') {
    console.log(`📢 ${type.toUpperCase()}: ${message}`);
}

// Simulate threats (for drill button)
async function triggerDrill() {
    try {
        const response = await fetch(`${API_BASE}/dashboard/simulate-threats?count=3`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const data = await response.json();
            showToast('Incident drill initiated - 3 threats simulated', 'warning');
            refreshDashboardWithoutChartJump();
        }
    } catch (error) {
        console.error('❌ Drill error:', error);
        showToast('Drill failed', 'danger');
    }
}

// Export functions for HTML onclick handlers
window.refreshDashboard = function() {
    console.log('🔄 Manual refresh');
    
    // Force refresh everything including charts
    chartInitialized = false;
    loadDashboard();
    showToast('Dashboard refreshed', 'info');
};

window.refreshThreatIntel = function() {
    loadThreatIntelligence();
    showToast('Threat intelligence updated', 'info');
};

window.setTimeline = function(range) {
    showToast(`Timeline set to ${range}`, 'info');
    // You can implement actual timeline range changes here
};

window.triggerDrill = triggerDrill;
window.assignToMe = function() {
    showToast('Alert assigned to you', 'success');
};

window.markAsFalsePositive = function() {
    showToast('Alert marked as false positive', 'info');
};

window.showAlertDetails = showAlertDetails;

// Force charts to resize on window resize
window.addEventListener('resize', function() {
    if (charts.timeline) {
        setTimeout(() => {
            charts.timeline.resize();
        }, 100);
    }
});