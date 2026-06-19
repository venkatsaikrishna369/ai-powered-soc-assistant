from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

router = APIRouter()

# Share the same alerts database
from backend.api.dashboard import alerts_db

@router.get("/", response_model=Dict)
async def get_alerts(
    severity: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000)
):
    """Get alerts with optional filtering"""
    try:
        filtered = alerts_db
        
        if severity:
            filtered = [a for a in alerts_db if a.get('severity') == severity]
        
        # Apply limit
        result = filtered[-limit:] if filtered else []
        
        return {
            "count": len(result),
            "alerts": result,
            "filter": severity if severity else "all",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{alert_id}", response_model=Dict)
async def get_alert_by_id(alert_id: str):
    """Get specific alert by ID"""
    try:
        for alert in alerts_db:
            if alert.get('id') == alert_id:
                return alert
        
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{alert_id}/assign", response_model=Dict)
async def assign_alert(alert_id: str, assignee: str = "SOC Analyst"):
    """Assign alert to someone"""
    try:
        for alert in alerts_db:
            if alert.get('id') == alert_id:
                alert['assigned_to'] = assignee
                alert['status'] = 'assigned'
                return {
                    "message": f"Alert {alert_id} assigned to {assignee}",
                    "alert": alert
                }
        
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{alert_id}/resolve", response_model=Dict)
async def resolve_alert(alert_id: str):
    """Mark alert as resolved"""
    try:
        for alert in alerts_db:
            if alert.get('id') == alert_id:
                alert['status'] = 'resolved'
                alert['resolved_at'] = datetime.now().isoformat()
                return {
                    "message": f"Alert {alert_id} resolved",
                    "alert": alert
                }
        
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear", response_model=Dict)
async def clear_alerts():
    """Clear all alerts"""
    try:
        global alerts_db
        count = len(alerts_db)
        alerts_db.clear()
        
        # Add one default alert
        from backend.api.dashboard import generate_sample_alerts
        generate_sample_alerts(1)
        
        return {
            "message": f"Cleared {count} alerts",
            "remaining": len(alerts_db)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))