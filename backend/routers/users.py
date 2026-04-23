"""User management API routes."""
from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import UserCreate, UserProfile
import upt_service

router = APIRouter()


@router.post("/", response_model=UserProfile, status_code=201)
def create_user(user: UserCreate):
    """Creates a new employee user in the system."""
    return upt_service.create_user(user)


@router.get("/", response_model=List[UserProfile])
def list_users():
    """Returns all employee users."""
    return upt_service.get_all_users()


@router.get("/{user_id}", response_model=UserProfile)
def get_user(user_id: str):
    """Returns a specific user by ID."""
    user = upt_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/events")
def get_user_events(user_id: str):
    """Returns all interaction events for a user."""
    events = upt_service.get_user_events(user_id)
    return events
