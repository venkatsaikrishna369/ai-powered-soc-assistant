from fastapi import FastAPI, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.exceptions import HTTPException
import uvicorn
import httpx
import os
import sys
from datetime import datetime
from typing import Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api import dashboard, alerts, logs, threats
from config.settings import APP_NAME, VERSION, HOST, PORT

app = FastAPI(
    title=APP_NAME,
    version=VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])
app.include_router(threats.router, prefix="/api/threats", tags=["Threats"])

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Static files
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def serve_root():
        login_path = os.path.join(FRONTEND_DIR, "login.html")
        if os.path.exists(login_path):
            with open(login_path, 'r', encoding='utf-8') as f:
                return f.read()
        return "<h1>Login page not found</h1>"

    @app.get("/dashboard.html", response_class=HTMLResponse)
    async def serve_dashboard():
        dash_path = os.path.join(FRONTEND_DIR, "dashboard.html")
        if os.path.exists(dash_path):
            with open(dash_path, 'r', encoding='utf-8') as f:
                return f.read()
        return "<h1>Dashboard not found</h1>"

    @app.get("/alerts.html", response_class=HTMLResponse)
    async def serve_alerts():
        alerts_path = os.path.join(FRONTEND_DIR, "alerts.html")
        if os.path.exists(alerts_path):
            with open(alerts_path, 'r', encoding='utf-8') as f:
                return f.read()
        return "<h1>Alerts page not found</h1>"

    @app.get("/js/{filename}")
    async def serve_js(filename: str):
        js_path = os.path.join(FRONTEND_DIR, "js", filename)
        if os.path.exists(js_path):
            return FileResponse(js_path, media_type="application/javascript")
        raise HTTPException(status_code=404, detail="JS file not found")

# Proxy endpoints for forgot-password (if needed)
FORGOT_SERVICE_URL = os.getenv('FORGOT_SERVICE_URL', 'http://127.0.0.1:3002')

@app.post('/send-sms')
async def proxy_send_sms(payload: dict = Body(...)):
    url = f"{FORGOT_SERVICE_URL}/send-sms"
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=payload, timeout=10.0)
            try:
                return JSONResponse(status_code=r.status_code, content=r.json())
            except Exception:
                return JSONResponse(status_code=r.status_code, content={"detail": r.text})
    except Exception as e:
        return JSONResponse(status_code=502, content={"error": "failed to reach forgot service", "reason": str(e)})

@app.post('/admin-reset-token')
async def proxy_admin_reset_token(payload: dict = Body(...)):
    url = f"{FORGOT_SERVICE_URL}/admin-reset-token"
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=payload, timeout=20.0)
            try:
                return JSONResponse(status_code=r.status_code, content=r.json())
            except Exception:
                return JSONResponse(status_code=r.status_code, content={"detail": r.text})
    except Exception as e:
        return JSONResponse(status_code=502, content={"error": "failed to reach forgot service", "reason": str(e)})

# Health check endpoint
@app.get("/api/health", response_model=Dict)
async def health_check():
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": VERSION,
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "dashboard": "/api/dashboard",
            "alerts": "/api/alerts",
            "logs": "/api/logs",
            "threats": "/api/threats"
        }
    }

# Root API endpoint
@app.get("/api/", response_model=Dict)
async def api_root():
    return {
        "message": "Network Security Intelligence Dashboard API",
        "version": VERSION,
        "endpoints": [
            {"url": "/api/health", "method": "GET", "description": "Health check"},
            {"url": "/api/dashboard/stats", "method": "GET", "description": "Dashboard statistics"},
            {"url": "/api/dashboard/charts", "method": "GET", "description": "Chart data"},
            {"url": "/api/alerts", "method": "GET", "description": "Get all alerts"},
            {"url": "/api/alerts/{id}", "method": "GET", "description": "Get specific alert"},
            {"url": "/api/threats/analyze", "method": "POST", "description": "Analyze threats"}
        ]
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "path": request.url.path,
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    print(f"🚀 Starting {APP_NAME} v{VERSION}")
    print(f"🌐 Login: http://{HOST}:{PORT}/")
    print(f"🌐 Dashboard: http://{HOST}:{PORT}/dashboard.html (protected)")
    print(f"🌐 API Docs: http://{HOST}:{PORT}/api/docs")
    print("\nPress Ctrl+C to stop the server")
    print("="*60)

    uvicorn.run(
        "backend.main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info",
        access_log=True
    )