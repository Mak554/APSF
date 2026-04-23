"""
APSF FastAPI Backend – Main Entry Point
Run with: uvicorn main:app --reload --port 8000
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import base64

from routers import users, campaigns, tracking, atm, dashboard
from models.schemas import EventType
import upt_service, atm_service

app = FastAPI(
    title="APSF – Adaptive Phishing Simulation Framework",
    description="An adaptive phishing simulation and training system for employee security.",
    version="1.0.0",
)

# ─────────────────────────────────────────
# CORS (allow Next.js frontend)
# ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
# Routers
# ─────────────────────────────────────────
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
app.include_router(tracking.router, prefix="/track", tags=["Event Tracking"])
app.include_router(atm.router, prefix="/atm", tags=["Adaptive Training Module"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])


# ─────────────────────────────────────────
# Tracking Pixel Route (Email Open Detection)
# ─────────────────────────────────────────
# This is served directly on the root to keep the URL simple
@app.get("/track/open/{campaign_id}/{user_id}", include_in_schema=False)
async def track_email_open(campaign_id: str, user_id: str, request: Request):
    """
    Logs an Email_Opened event. Returns a transparent 1x1 GIF so the email renders normally.
    This gets embedded as an <img> tag in phishing emails.
    """
    upt_service.log_event(
        user_id=user_id,
        campaign_id=campaign_id,
        event_type=EventType.EMAIL_OPENED,
        ip_address=request.client.host,
        user_agent=request.headers.get("User-Agent"),
    )
    # Return a transparent 1×1 GIF pixel
    pixel = base64.b64decode(
        "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
    )
    return Response(content=pixel, media_type="image/gif")


@app.get("/", tags=["Health"])
async def root():
    return {"status": "APSF API is running 🚀", "docs": "/docs"}
