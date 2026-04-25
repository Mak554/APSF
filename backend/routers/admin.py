"""
routers/admin.py
Admin utility endpoints — database reset/seed.
"""
from fastapi import APIRouter
import local_db

router = APIRouter()

SEED_USERS = [
    {"full_name": "Mohammed Alkhateeb", "email": "m7md-_-0101@hotmail.com", "department": "IT"},
    {"full_name": "Jassim Alharbi",     "email": "jassim.kfo@gmail.com",    "department": "Finance"},
    {"full_name": "Ibrahim Aloufi",     "email": "abra9778@gmail.com",       "department": "Engineering"},
]


@router.post("/reset", tags=["Admin"])
def reset_database():
    """
    Wipes all in-memory data and re-seeds the 3 real target employees.
    Use this after a Render cold-start wipes the DB.
    """
    # Clear all in-memory stores
    local_db.users_db.clear()
    local_db.campaigns_db.clear()
    local_db.events_db.clear()

    # Re-seed the 3 real users
    import upt_service, uuid
    seeded = []
    for u in SEED_USERS:
        uid = str(uuid.uuid4())
        from models.schemas import UserProfile
        profile = UserProfile(
            user_id=uid,
            full_name=u["full_name"],
            email=u["email"],
            department=u["department"],
        )
        local_db.users_db[uid] = profile
        seeded.append({"user_id": uid, "full_name": u["full_name"], "email": u["email"]})

    return {
        "status": "reset_complete",
        "message": f"Database wiped and re-seeded with {len(seeded)} users.",
        "users": seeded,
    }


@router.post("/seed-users", tags=["Admin"])
def seed_users_only():
    """
    Adds the 3 real target employees if they don't already exist (safe to call multiple times).
    """
    import uuid
    from models.schemas import UserProfile

    added = []
    already_exists = []

    existing_emails = {u.email for u in local_db.users_db.values()}

    for u in SEED_USERS:
        if u["email"] in existing_emails:
            already_exists.append(u["email"])
            continue
        uid = str(uuid.uuid4())
        profile = UserProfile(
            user_id=uid,
            full_name=u["full_name"],
            email=u["email"],
            department=u["department"],
        )
        local_db.users_db[uid] = profile
        added.append({"user_id": uid, "email": u["email"]})

    return {
        "status": "ok",
        "added": added,
        "already_existed": already_exists,
    }
