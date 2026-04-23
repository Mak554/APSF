"""
User Performance Tracker (UPT) Service
Handles all Firestore CRUD operations for users, events, and training records.
Works with both Firebase Firestore and the local in-memory fallback.
"""
import uuid
import os
from datetime import datetime
from typing import List, Optional

def _get_helpers():
    """Returns (Increment, Query) from the correct backend."""
    from firebase_config import USE_LOCAL
    if USE_LOCAL:
        import local_db
        return local_db.Increment, local_db.Query
    else:
        from firebase_admin import firestore
        return firestore.Increment, firestore.Query
from firebase_config import get_db
from models.schemas import (
    UserCreate, UserProfile, InteractionEvent, EventType,
    Campaign, TrainingAssignment, RiskTier
)


# ─────────────────────────────────────────
# User Operations
# ─────────────────────────────────────────

def create_user(user_data: UserCreate) -> UserProfile:
    """Creates a new user in the /users collection."""
    db = get_db()
    user_id = str(uuid.uuid4())
    profile = UserProfile(
        user_id=user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        department=user_data.department,
    )
    db.collection("users").document(user_id).set(profile.model_dump())
    return profile


def get_user(user_id: str) -> Optional[UserProfile]:
    """Fetches a user by their ID."""
    db = get_db()
    doc = db.collection("users").document(user_id).get()
    if doc.exists:
        return UserProfile(**doc.to_dict())
    return None


def get_all_users() -> List[UserProfile]:
    """Fetches all user profiles from Firestore."""
    db = get_db()
    users = db.collection("users").stream()
    return [UserProfile(**u.to_dict()) for u in users]


def update_user_risk(user_id: str, p_fail: float, risk_tier: RiskTier):
    """Updates a user's risk score and tier after ATM calculation."""
    db = get_db()
    db.collection("users").document(user_id).update({
        "p_fail": p_fail,
        "risk_tier": risk_tier.value,
    })


def increment_user_stats(user_id: str, event_type: EventType, campaign_id: Optional[str] = None):
    """Atomically increments the relevant counter on a user's profile and updates behavioral vectors."""
    db = get_db()
    Increment, _ = _get_helpers()
    ref = db.collection("users").document(user_id)
    doc = ref.get()
    
    if not doc.exists:
        return
        
    user_data = doc.to_dict()
    update_payload = {}
    
    if event_type in (EventType.LINK_CLICKED, EventType.DATA_SUBMITTED):
        update_payload["total_failures"] = Increment(1)
        update_payload["total_simulations"] = Increment(1)
        update_payload["last_simulation_date"] = datetime.utcnow()
        
        # Adaptive Pattern updates
        if campaign_id:
            campaign = get_campaign(campaign_id)
            if campaign:
                # Update Susceptibility Vector
                ptype = campaign.phishing_type.value
                sus_vec = user_data.get("susceptibility_vector", {})
                sus_vec[ptype] = sus_vec.get(ptype, 0) + 1
                update_payload["susceptibility_vector"] = sus_vec
                
                # Calculate Response Time
                events = get_user_events(user_id)
                sent_event = next((e for e in events if e.campaign_id == campaign_id and e.event_type == EventType.EMAIL_SENT), None)
                click_event = next((e for e in events if e.campaign_id == campaign_id and e.event_type == event_type), None)
                
                if sent_event and click_event:
                    rt_seconds = (click_event.timestamp - sent_event.timestamp).total_seconds()
                    # Calculate rolling average
                    avg_rt = user_data.get("avg_response_time", 0.0)
                    total_fails = user_data.get("total_failures", 0) + 1
                    
                    if avg_rt > 0:
                        new_avg = ((avg_rt * (total_fails - 1)) + rt_seconds) / total_fails
                    else:
                        new_avg = rt_seconds
                        
                    update_payload["avg_response_time"] = new_avg

        ref.update(update_payload)
        
    elif event_type == EventType.EMAIL_REPORTED:
        ref.update({"total_reports": Increment(1)})
    elif event_type == EventType.EMAIL_SENT:
        ref.update({"total_simulations": Increment(1)})


# ─────────────────────────────────────────
# Event Logging
# ─────────────────────────────────────────

def log_event(
    user_id: str,
    campaign_id: str,
    event_type: EventType,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    submitted_data: Optional[dict] = None,
) -> InteractionEvent:
    """Logs a user interaction event to the /events collection."""
    db = get_db()
    event_id = str(uuid.uuid4())
    event = InteractionEvent(
        event_id=event_id,
        user_id=user_id,
        campaign_id=campaign_id,
        event_type=event_type,
        ip_address=ip_address,
        user_agent=user_agent,
        submitted_data=submitted_data,
    )
    db.collection("events").document(event_id).set(event.model_dump())
    # Also update the campaign counters
    _update_campaign_stats(campaign_id, event_type)
    return event


def get_user_events(user_id: str) -> List[InteractionEvent]:
    """Fetches all interaction events for a given user."""
    db = get_db()
    _, Query = _get_helpers()
    docs = (
        db.collection("events")
        .where("user_id", "==", user_id)
        .order_by("timestamp", direction=Query.DESCENDING)
        .stream()
    )
    return [InteractionEvent(**d.to_dict()) for d in docs]


def _update_campaign_stats(campaign_id: str, event_type: EventType):
    """Internal helper: Atomically increments campaign-level counters."""
    db = get_db()
    Increment, _ = _get_helpers()
    ref = db.collection("campaigns").document(campaign_id)
    update_map = {
        EventType.EMAIL_SENT: {"emails_sent": Increment(1)},
        EventType.EMAIL_OPENED: {},
        EventType.LINK_CLICKED: {"clicks": Increment(1)},
        EventType.DATA_SUBMITTED: {"submissions": Increment(1)},
        EventType.EMAIL_REPORTED: {"reports": Increment(1)},
    }
    if update_map.get(event_type):
        ref.update(update_map[event_type])


# ─────────────────────────────────────────
# Campaign Operations
# ─────────────────────────────────────────

def get_campaign(campaign_id: str) -> Optional[Campaign]:
    """Fetches a single campaign by ID."""
    db = get_db()
    doc = db.collection("campaigns").document(campaign_id).get()
    if doc.exists:
        return Campaign(**doc.to_dict())
    return None


def get_all_campaigns() -> List[Campaign]:
    """Fetches all campaigns."""
    db = get_db()
    _, Query = _get_helpers()
    campaigns = (
        db.collection("campaigns")
        .order_by("created_at", direction=Query.DESCENDING)
        .stream()
    )
    return [Campaign(**c.to_dict()) for c in campaigns]


# ─────────────────────────────────────────
# Training Assignment Operations
# ─────────────────────────────────────────

def assign_training(
    user_id: str,
    campaign_id: str,
    module_id: str,
    module_title: str,
    reason: str,
    is_mandatory: bool,
) -> TrainingAssignment:
    """Creates a training assignment record in Firestore."""
    db = get_db()
    assignment_id = str(uuid.uuid4())
    assignment = TrainingAssignment(
        assignment_id=assignment_id,
        user_id=user_id,
        campaign_id=campaign_id,
        module_id=module_id,
        module_title=module_title,
        reason=reason,
        is_mandatory=is_mandatory,
    )
    db.collection("training-assignments").document(assignment_id).set(
        assignment.model_dump()
    )
    return assignment


def complete_training(assignment_id: str):
    """Marks a training assignment as completed."""
    db = get_db()
    db.collection("training-assignments").document(assignment_id).update({
        "is_completed": True,
        "completed_at": datetime.utcnow(),
    })
    # Update the user's training completion count not shown for brevity
