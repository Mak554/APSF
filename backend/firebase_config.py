"""
Firebase DB configuration.

Supports three initialization methods (in priority order):
1. Individual environment variables (FIREBASE_PRIVATE_KEY etc.) — best for Render
2. Secret file at /etc/secrets/serviceAccountKey.json (Render Secret Files)
3. Local JSON file (FIREBASE_CREDENTIALS_PATH env var or ./serviceAccountKey.json)
"""
import os
import json
import sys
from dotenv import load_dotenv

load_dotenv()

_db = None


def _build_cred_dict_from_env() -> dict | None:
    """Build credentials dict from individual environment variables."""
    private_key = os.getenv("FIREBASE_PRIVATE_KEY", "")
    if not private_key:
        return None
    # Render stores env vars with literal \n — replace with real newlines
    private_key = private_key.replace("\\n", "\n")
    return {
        "type": "service_account",
        "project_id": os.getenv("FIREBASE_PROJECT_ID", ""),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID", ""),
        "private_key": private_key,
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL", ""),
        "client_id": os.getenv("FIREBASE_CLIENT_ID", ""),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL", ""),
        "universe_domain": "googleapis.com",
    }


def get_db():
    """Returns a singleton Firestore client."""
    global _db
    if _db is not None:
        return _db

    import firebase_admin
    from firebase_admin import credentials, firestore

    if not firebase_admin._apps:
        cred = None

        # Method 1: individual env vars (most reliable on Render)
        cred_dict = _build_cred_dict_from_env()
        if cred_dict and cred_dict["private_key"].strip():
            print("[DB] Using Firebase credentials from environment variables")
            cred = credentials.Certificate(cred_dict)

        # Method 2: Render Secret File path
        elif os.path.exists("/etc/secrets/serviceAccountKey.json"):
            print("[DB] Using Firebase credentials from /etc/secrets/serviceAccountKey.json")
            cred = credentials.Certificate("/etc/secrets/serviceAccountKey.json")

        # Method 3: Local file
        else:
            local_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "./serviceAccountKey.json")
            if os.path.exists(local_path):
                print(f"[DB] Using Firebase credentials from {local_path}")
                cred = credentials.Certificate(local_path)
            else:
                print("[FATAL] No Firebase credentials found. Set FIREBASE_PRIVATE_KEY env var or upload serviceAccountKey.json")
                sys.exit(1)

        firebase_admin.initialize_app(cred)

    _db = firestore.client()
    print("[DB] Connected to Firebase Firestore")
    return _db
