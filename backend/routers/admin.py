"""
routers/admin.py
Admin utility endpoints — database reset/seed.
Works with both Firestore and the local in-memory fallback via upt_service.
"""
from fastapi import APIRouter
import uuid
import upt_service
from models.schemas import UserCreate

router = APIRouter()

SEED_USERS = [
    {"full_name": "Mohammed Alkhateeb", "email": "m7md-_-0101@hotmail.com", "department": "IT"},
    {"full_name": "Jassim Alharbi",     "email": "jassim.kfo@gmail.com",    "department": "Finance"},
    {"full_name": "Ibrahim Aloufi",     "email": "abra9778@gmail.com",       "department": "Engineering"},
]


@router.post("/reset", tags=["Admin"])
def reset_database():
    """
    Deletes all users, campaigns, events, and training assignments from the DB,
    then re-seeds the 3 real target employees.
    Works with both Firestore and local mode.
    """
    from firebase_config import get_db
    db = get_db()

    # Delete all documents in each collection
    for collection_name in ["users", "campaigns", "events", "training-assignments"]:
        docs = db.collection(collection_name).stream()
        for doc in docs:
            db.collection(collection_name).document(doc.id).delete()

    # Re-seed the 3 real users
    seeded = []
    for u in SEED_USERS:
        profile = upt_service.create_user(UserCreate(
            full_name=u["full_name"],
            email=u["email"],
            department=u["department"],
        ))
        seeded.append({"user_id": profile.user_id, "full_name": profile.full_name, "email": profile.email})

    return {
        "status": "reset_complete",
        "message": f"Database wiped and re-seeded with {len(seeded)} users.",
        "users": seeded,
    }


@router.post("/seed-users", tags=["Admin"])
def seed_users_only():
    """
    Adds the 3 real target employees if they don't already exist (safe to call multiple times).
    Uses upt_service so it works with both Firestore and local mode.
    """
    existing = upt_service.get_all_users()
    existing_emails = {u.email for u in existing}

    added = []
    already_exists = []

    for u in SEED_USERS:
        if u["email"] in existing_emails:
            already_exists.append(u["email"])
            continue

        profile = upt_service.create_user(UserCreate(
            full_name=u["full_name"],
            email=u["email"],
            department=u["department"],
        ))
        added.append({"user_id": profile.user_id, "email": profile.email})

    return {
        "status": "ok",
        "added": added,
        "already_existed": already_exists,
    }
