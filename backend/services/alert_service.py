from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
from collections import defaultdict

class AlertService:
    def __init__(self):
        self.alerts = []
        self.alert_counters = {
            'total': 0,
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
        self.mitre_counter = defaultdict(int)
        self.last_update = datetime.now()
    
    def add_alert(self, alert: Dict):
        """Add a new alert"""
        self.alerts.append(alert)
        self.alert_counters['total'] += 1
        
        # Update severity counter
        severity = alert.get('severity', 'info')
        if severity in self.alert_counters:
            self.alert_counters[severity] += 1
        
        # Update MITRE counter
        for technique in alert.get('mitre_techniques', []):
            self.mitre_counter[technique] += 1
        
        self.last_update = datetime.now()
    
    def get_recent_alerts(self, limit: int = 20) -> List[Dict]:
        """Get recent alerts"""
        # Return latest alerts
        return sorted(
            self.alerts[-limit:],
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )
    
    def get_alerts_by_severity(self, severity: str) -> List[Dict]:
        """Get alerts by severity"""
        return [
            alert for alert in self.alerts
            if alert.get('severity') == severity
        ]
    
    def get_alert(self, alert_id: str) -> Dict:
        """Get specific alert"""
        for alert in self.alerts:
            if alert.get('id') == alert_id:
                return alert
        return {}
    
    def get_stats(self) -> Dict:
        """Get alert statistics"""
        # Calculate recent alerts (last hour)
        hour_ago = datetime.now() - timedelta(hours=1)
        recent_count = sum(1 for a in self.alerts 
                          if datetime.fromisoformat(a.get('timestamp', '2000-01-01')) > hour_ago)
        
        # Calculate average risk score
        risk_scores = [a.get('risk_score', 0) for a in self.alerts if a.get('risk_score')]
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        return {
            'total': self.alert_counters['total'],
            'critical': self.alert_counters['critical'],
            'high': self.alert_counters['high'],
            'medium': self.alert_counters['medium'],
            'low': self.alert_counters['low'],
            'info': self.alert_counters['info'],
            'active_threats': self.alert_counters['critical'] + self.alert_counters['high'],
            'recent_alerts': recent_count,
            'avg_risk_score': int(avg_risk),
            'mitre_count': sum(len(a.get('mitre_techniques', [])) for a in self.alerts),
            'top_mitre': max(self.mitre_counter.items(), key=lambda x: x[1], default=('T1046', 0))[0],
            'last_updated': self.last_update.isoformat()
        }
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()
        for key in self.alert_counters:
            self.alert_counters[key] = 0
        self.mitre_counter.clear()
        self.last_update = datetime.now()

# Global instance
alert_service = AlertService()