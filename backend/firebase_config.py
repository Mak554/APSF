"""
Firebase DB configuration.

On Render: Secret files are placed at /etc/secrets/<filename>
Locally:   serviceAccountKey.json lives in the backend directory
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Check Render's secret file path first, then fall back to local path
_RENDER_PATH = "/etc/secrets/serviceAccountKey.json"
_LOCAL_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "./serviceAccountKey.json")
_cred_path = _RENDER_PATH if os.path.exists(_RENDER_PATH) else _LOCAL_PATH

if not os.path.exists(_cred_path):
    print(f"[FATAL] Firebase credentials not found at {_cred_path} or {_RENDER_PATH}")
    sys.exit(1)

_db = None

def get_db():
    """Returns a singleton Firestore client."""
    global _db
    if _db is not None:
        return _db

    import firebase_admin
    from firebase_admin import credentials, firestore
    
    if not firebase_admin._apps:
        cred = credentials.Certificate(_cred_path)
        firebase_admin.initialize_app(cred)
        
    _db = firestore.client()
    print("[DB] Connected to Firebase Firestore")

    return _db
