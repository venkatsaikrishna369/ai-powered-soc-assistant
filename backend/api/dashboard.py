from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any
import random
from datetime import datetime, timedelta
import json

router = APIRouter()

# In-memory data storage
alerts_db = []
last_alert_id = 1000

# Generate sample alerts
def generate_sample_alerts(count: int = 5) -> List[Dict]:
    global last_alert_id
    alerts = []
    
    severities = ['critical', 'high', 'medium', 'low', 'info']
    protocols = ['TCP', 'UDP', 'HTTP', 'HTTPS', 'SSH', 'DNS']
    attack_types = ['Port Scan', 'DDoS', 'Malware', 'Brute Force', 'SQL Injection', 'XSS']
    mitre_techniques = ['T1046', 'T1043', 'T1190', 'T1566', 'T1059', 'T1203']
    
    for i in range(count):
        last_alert_id += 1
        severity = random.choice(severities)
        
        alert = {
            "id": f"ALERT-{last_alert_id}",
            "timestamp": datetime.now().isoformat(),
            "source_ip": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "destination_ip": f"10.0.{random.randint(1, 255)}.{random.randint(1, 100)}",
            "protocol": random.choice(protocols),
            "source_port": random.randint(1024, 65535),
            "destination_port": random.choice([80, 443, 22, 53, 3389]),
            "threat_type": "Malicious" if severity in ['critical', 'high', 'medium'] else "Normal",
            "confidence": random.uniform(0.6, 0.95) if severity in ['critical', 'high'] else random.uniform(0.3, 0.6),
            "severity": severity,
            "risk_score": random.randint(40, 95) if severity in ['critical', 'high'] else random.randint(20, 60),
            "description": f"{severity.upper()} {random.choice(attack_types)} detected from source",
            "attack_category": random.choice(attack_types),
            "mitre_techniques": random.sample(mitre_techniques, random.randint(1, 3)),
            "status": "new",
            "assigned_to": None,
            "llm_analysis": f"AI Analysis: This appears to be a {severity} severity {random.choice(attack_types)} attack.",
            "recommended_actions": [
                "Block source IP in firewall",
                "Review authentication logs",
                "Update security policies"
            ],
            "risk_level": severity
        }
        alerts.append(alert)
        alerts_db.append(alert)
    
    return alerts

# Initialize with some sample data
generate_sample_alerts(10)

@router.get("/stats", response_model=Dict)
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Calculate statistics
        total = len(alerts_db)
        critical = sum(1 for a in alerts_db if a['severity'] == 'critical')
        high = sum(1 for a in alerts_db if a['severity'] == 'high')
        medium = sum(1 for a in alerts_db if a['severity'] == 'medium')
        low = sum(1 for a in alerts_db if a['severity'] == 'low')
        info = sum(1 for a in alerts_db if a['severity'] == 'info')
        
        risk_scores = [a['risk_score'] for a in alerts_db]
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        # Count MITRE techniques
        mitre_count = sum(len(a['mitre_techniques']) for a in alerts_db)
        
        # Find most common MITRE technique
        technique_counter = {}
        for alert in alerts_db:
            for tech in alert['mitre_techniques']:
                technique_counter[tech] = technique_counter.get(tech, 0) + 1
        
        top_technique = max(technique_counter.items(), key=lambda x: x[1], default=('T1046', 0))[0]
        
        return {
            "total_alerts": total,
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
            "info": info,
            "avg_risk_score": round(avg_risk),
            "active_threats": critical + high,
            "response_time": random.randint(5, 15),
            "mitre_count": mitre_count,
            "top_technique": top_technique,
            "alert_trend": round(random.uniform(-5.0, 15.0), 1),
            "critical_response": critical,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts", response_model=Dict)
async def get_chart_data():
    """Get data for dashboard charts"""
    try:
        # Generate timeline data (last 24 hours)
        labels = []
        data = []
        
        now = datetime.now()
        for i in range(24, -1, -1):
            hour = (now - timedelta(hours=i)).strftime("%H:00")
            labels.append(hour)
            
            # More activity during business hours
            base = 10 if 9 <= (now.hour - i) % 24 <= 17 else 4
            data.append(base + random.randint(0, 8))
        
        # Attack types data
        attack_types = ['Port Scan', 'DDoS', 'Malware', 'Brute Force', 'SQL Injection', 'XSS']
        attack_data = [random.randint(20, 50) for _ in range(6)]
        
        # Country data
        countries = ['USA', 'China', 'Russia', 'Germany', 'Netherlands', 'Brazil', 'India']
        country_data = [random.randint(10, 40) for _ in range(7)]
        
        return {
            "threat_timeline": {
                "labels": labels,
                "data": data
            },
            "attack_types": {
                "labels": attack_types,
                "data": attack_data
            },
            "top_countries": {
                "labels": countries,
                "data": country_data
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent-alerts", response_model=Dict)
async def get_recent_alerts(limit: int = Query(10, ge=1, le=100)):
    """Get recent alerts for dashboard"""
    try:
        recent = alerts_db[-limit:] if alerts_db else []
        
        # Format for frontend
        formatted = []
        for alert in recent:
            formatted.append({
                'id': alert.get('id', ''),
                'time': alert.get('timestamp', ''),
                'severity': alert.get('severity', 'info'),
                'source_ip': alert.get('source_ip', ''),
                'destination_ip': alert.get('destination_ip', ''),
                'description': alert.get('description', ''),
                'mitre_techniques': alert.get('mitre_techniques', []),
                'risk_score': alert.get('risk_score', 0),
                'status': alert.get('status', 'new')
            })
        
        # Count new alerts
        new_count = sum(1 for a in recent if a.get('status') == 'new')
        
        return {
            "alerts": formatted,
            "new_alerts_count": new_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/threat-intelligence", response_model=Dict)
async def get_threat_intelligence():
    """Get AI threat intelligence"""
    try:
        return {
            "root_cause": "Increased scanning activity from suspicious IP ranges. Multiple port scanning attempts detected targeting exposed services.",
            "mitre_mapping": ["T1046", "T1043", "T1190", "T1566", "T1059"],
            "recommended_actions": [
                "Block suspicious IP ranges in firewall",
                "Implement rate limiting on authentication endpoints",
                "Review and update security group rules",
                "Enable multi-factor authentication for critical systems"
            ],
            "top_threats": ["Port Scanning", "Credential Stuffing", "Malware Distribution", "DDoS Attacks"],
            "risk_level": "high"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate-threats", response_model=Dict)
async def simulate_threats(count: int = Query(3, ge=1, le=20)):
    """Simulate new threats"""
    try:
        new_alerts = generate_sample_alerts(count)
        
        return {
            "message": f"Simulated {count} threats",
            "generated": len(new_alerts),
            "alerts": new_alerts[:3],  # Return first 3 for preview
            "stats": await get_dashboard_stats()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/stream", response_model=Dict)
async def stream_logs():
    """Stream real-time logs"""
    try:
        protocols = ['TCP', 'UDP', 'HTTP', 'HTTPS', 'SSH', 'DNS']
        actions = ['ALLOW', 'BLOCK']
        
        logs = []
        for i in range(8):
            logs.append({
                'timestamp': (datetime.now() - timedelta(seconds=i*5)).strftime("%H:%M:%S"),
                'source': f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                'dest': f"10.0.{random.randint(1, 255)}.1",
                'protocol': random.choice(protocols),
                'action': random.choice(actions),
                'bytes': random.randint(64, 2048)
            })
        
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))