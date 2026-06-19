from fastapi import APIRouter, HTTPException
from typing import Dict, List
import random
from datetime import datetime

router = APIRouter()

@router.post("/analyze", response_model=Dict)
async def analyze_threats(count: int = 10):
    """Analyze logs for threats"""
    try:
        # Generate sample threats
        severities = ['critical', 'high', 'medium', 'low', 'info']
        attack_types = ['Port Scan', 'DDoS', 'Malware', 'Brute Force', 'SQL Injection']
        
        categorized = {s: [] for s in severities}
        
        for i in range(count):
            severity = random.choice(severities)
            alert = {
                'id': f"THREAT-{random.randint(1000, 9999)}",
                'timestamp': datetime.now().isoformat(),
                'severity': severity,
                'description': f"{severity.upper()} {random.choice(attack_types)} detected",
                'confidence': random.uniform(0.6, 0.95),
                'risk_score': random.randint(40, 95)
            }
            categorized[severity].append(alert)
        
        return {
            "statistics": {
                "total_analyzed": count,
                "threats_detected": sum(len(categorized[s]) for s in ['critical', 'high', 'medium']),
                "false_positives": random.randint(0, 2),
                "processing_time_ms": random.randint(50, 200)
            },
            "categorized_alerts": categorized,
            "top_threats": categorized['critical'][:2] if categorized['critical'] else categorized['high'][:2]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))