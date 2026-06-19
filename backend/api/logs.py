from fastapi import APIRouter, HTTPException
from typing import Dict, List
import random
from datetime import datetime

router = APIRouter()

@router.get("/sample", response_model=Dict)
async def get_sample_logs(count: int = 10):
    """Get sample logs"""
    try:
        protocols = ['TCP', 'UDP', 'HTTP', 'HTTPS', 'SSH', 'DNS']
        actions = ['ALLOW', 'BLOCK']
        
        logs = []
        for i in range(min(count, 50)):
            logs.append({
                'timestamp': datetime.now().isoformat(),
                'source_ip': f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                'destination_ip': f"10.0.{random.randint(1, 255)}.{random.randint(1, 100)}",
                'protocol': random.choice(protocols),
                'source_port': random.randint(1024, 65535),
                'destination_port': random.choice([80, 443, 22, 53, 3389]),
                'action': random.choice(actions),
                'bytes_sent': random.randint(64, 2048),
                'bytes_received': random.randint(64, 1024)
            })
        
        return {
            "count": len(logs),
            "logs": logs[:5],  # Return first 5
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))