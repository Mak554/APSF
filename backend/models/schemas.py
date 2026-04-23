"""
Pydantic data models for the APSF backend.
These define the structure of requests and responses, and document the Firestore schema.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ─────────────────────────────────────────
# Enums
# ─────────────────────────────────────────

class RiskTier(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    NEW = "New"

class EventType(str, Enum):
    EMAIL_SENT = "Email_Sent"
    EMAIL_OPENED = "Email_Opened"
    LINK_CLICKED = "Link_Clicked"
    DATA_SUBMITTED = "Data_Submitted"
    EMAIL_REPORTED = "Email_Reported"

class PhishingType(str, Enum):
    CREDENTIAL_HARVEST = "Credential_Harvest"
    LINK_ONLY = "Link_Only"
    ATTACHMENT = "Attachment"
    URGENCY = "Urgency"

class Difficulty(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


# ─────────────────────────────────────────
# User Models
# ─────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    department: str

class UserProfile(BaseModel):
    """Firestore Collection: /users/{user_id}"""
    user_id: str
    email: EmailStr
    full_name: str
    department: str
    risk_tier: RiskTier = RiskTier.NEW
    p_fail: float = Field(default=0.0, ge=0.0, le=1.0, description="Probability of failure (0.0-1.0)")
    total_simulations: int = 0
    total_failures: int = 0
    total_reports: int = 0
    training_completed: int = 0
    last_simulation_date: Optional[datetime] = None
    susceptibility_vector: dict = Field(default_factory=dict, description="Failure counts/rates per PhishingType")
    avg_response_time: float = Field(default=0.0, description="Avg interaction time in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ─────────────────────────────────────────
# Campaign Models
# ─────────────────────────────────────────

class CampaignCreate(BaseModel):
    name: str
    phishing_type: PhishingType
    email_template_id: str
    target_user_ids: List[str]
    sender_name: str = "IT Security Team"
    sender_email: str = "security@company.com"
    subject: str
    urgency_level: int = Field(default=1, ge=1, le=5, description="1=Low urgency, 5=Extreme urgency")
    difficulty: Difficulty = Difficulty.MEDIUM

class Campaign(BaseModel):
    """Firestore Collection: /campaigns/{campaign_id}"""
    campaign_id: str
    name: str
    phishing_type: PhishingType
    email_template_id: str
    sender_name: str
    sender_email: str
    subject: str
    urgency_level: int
    difficulty: Difficulty
    target_count: int
    emails_sent: int = 0
    clicks: int = 0
    submissions: int = 0
    reports: int = 0
    click_rate: float = 0.0
    status: str = "draft"  # draft, running, completed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


# ─────────────────────────────────────────
# Event Models
# ─────────────────────────────────────────

class InteractionEvent(BaseModel):
    """Firestore Collection: /events/{event_id}"""
    event_id: str
    user_id: str
    campaign_id: str
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    submitted_data: Optional[dict] = None  # Captures what a user submitted on a fake form


# ─────────────────────────────────────────
# ATM / Training Models
# ─────────────────────────────────────────

class TrainingAssignment(BaseModel):
    """Firestore Collection: /training-assignments/{assignment_id}"""
    assignment_id: str
    user_id: str
    campaign_id: str
    module_id: str
    module_title: str
    reason: str  # e.g., "High risk score after clicking Link_Clicked event"
    is_mandatory: bool
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    is_completed: bool = False


# ─────────────────────────────────────────
# API Response Models
# ─────────────────────────────────────────

class DashboardStats(BaseModel):
    total_users: int
    total_campaigns: int
    overall_click_rate: float
    high_risk_users: int
    medium_risk_users: int
    low_risk_users: int
    recent_campaigns: List[Campaign]
    top_risk_users: List[UserProfile]
