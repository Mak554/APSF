"""
Firebase / Local DB configuration.

If USE_LOCAL_DB=true in .env  OR  the serviceAccountKey.json file is missing,
the backend uses a fully in-memory store (local_db.py) so you can run without
any Firebase account.

Set USE_LOCAL_DB=false and provide serviceAccountKey.json to use real Firestore.
"""
import os
from dotenv import load_dotenv

load_dotenv()

USE_LOCAL = os.getenv("USE_LOCAL_DB", "true").lower() == "true"
_cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "./serviceAccountKey.json")

# Automatically fall back to local mode if credentials file is absent
if not os.path.exists(_cred_path):
    USE_LOCAL = True

_db = None


def get_db():
    """Returns a singleton DB client (Firestore or in-memory depending on config)."""
    global _db
    if _db is not None:
        return _db

    if USE_LOCAL:
        from local_db import get_local_db
        _db = get_local_db()
        print("[DB] Running with LOCAL in-memory database (no Firebase needed)")
    else:
        import firebase_admin
        from firebase_admin import credentials, firestore
        if not firebase_admin._apps:
            cred = credentials.Certificate(_cred_path)
            firebase_admin.initialize_app(cred)
        _db = firestore.client()
        print("[DB] Connected to Firebase Firestore")

    return _db
