"""
Event tracking API routes.
These endpoints are called when users interact with simulated phishing emails.
"""
from fastapi import APIRouter, Request, HTTPException
from models.schemas import EventType
import upt_service
import atm_service

router = APIRouter()


@router.get("/click/{campaign_id}/{user_id}")
async def track_click(campaign_id: str, user_id: str, request: Request):
    """
    Logs a Link_Clicked event and triggers the ATM to recalculate risk.
    Users are then redirected to the phishing landing page (handled by frontend).
    """
    user = upt_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    upt_service.log_event(
        user_id=user_id,
        campaign_id=campaign_id,
        event_type=EventType.LINK_CLICKED,
        ip_address=request.client.host,
        user_agent=request.headers.get("User-Agent"),
    )
    upt_service.increment_user_stats(user_id, EventType.LINK_CLICKED, campaign_id)

    # Trigger ATM in background (don't block the redirect)
    atm_service.process_user_event(user_id, campaign_id, EventType.LINK_CLICKED)

    return {"redirected": True, "user_id": user_id, "campaign_id": campaign_id}


@router.post("/submit/{campaign_id}/{user_id}")
async def track_submission(
    campaign_id: str,
    user_id: str,
    request: Request,
    submitted_data: dict = None,
):
    """
    Logs a Data_Submitted event (highest severity failure).
    Called when a user fills out the fake landing page form.
    """
    user = upt_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    upt_service.log_event(
        user_id=user_id,
        campaign_id=campaign_id,
        event_type=EventType.DATA_SUBMITTED,
        ip_address=request.client.host,
        user_agent=request.headers.get("User-Agent"),
        submitted_data=submitted_data,
    )
    upt_service.increment_user_stats(user_id, EventType.DATA_SUBMITTED, campaign_id)
    atm_service.process_user_event(user_id, campaign_id, EventType.DATA_SUBMITTED)

    return {"logged": True, "severity": "critical"}


@router.post("/report/{campaign_id}/{user_id}")
async def track_report(campaign_id: str, user_id: str, request: Request):
    """
    Logs an Email_Reported event (positive behavior).
    Called when a user clicks the 'Report Phishing' button.
    """
    user = upt_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    upt_service.log_event(
        user_id=user_id,
        campaign_id=campaign_id,
        event_type=EventType.EMAIL_REPORTED,
        ip_address=request.client.host,
        user_agent=request.headers.get("User-Agent"),
    )
    upt_service.increment_user_stats(user_id, EventType.EMAIL_REPORTED, campaign_id)

    return {"logged": True, "message": "Thank you! Phishing report logged as positive behavior."}
