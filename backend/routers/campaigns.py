"""Campaign management API routes."""
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List

from models.schemas import CampaignCreate, Campaign
import pse_service
import upt_service

router = APIRouter()


@router.post("/", response_model=Campaign, status_code=201)
def create_campaign(campaign_data: CampaignCreate):
    """Creates a new phishing simulation campaign (in draft status)."""
    return pse_service.create_campaign(campaign_data)


@router.get("/", response_model=List[Campaign])
def list_campaigns():
    """Returns all campaigns."""
    return upt_service.get_all_campaigns()


@router.get("/{campaign_id}", response_model=Campaign)
def get_campaign(campaign_id: str):
    """Returns a specific campaign by ID."""
    campaign = upt_service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.post("/{campaign_id}/launch")
def launch_campaign(campaign_id: str):
    """
    Launches a campaign: sends phishing emails to the campaign's stored target users.
    Falls back to all non-placeholder users if no specific targets were saved.
    """
    campaign = upt_service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status == "running":
        raise HTTPException(status_code=400, detail="Campaign is already running")

    # Prefer the campaign's own target list; fall back to all real users
    if campaign.target_user_ids:
        target_user_ids = campaign.target_user_ids
    else:
        all_users = upt_service.get_all_users()
        target_user_ids = [u.user_id for u in all_users if not u.email.endswith("@company.sa")]

    result = pse_service.send_campaign_emails(campaign, target_user_ids)
    return result


@router.get("/templates/list")
def list_templates():
    """Returns all available phishing email templates."""
    return pse_service.get_templates()
