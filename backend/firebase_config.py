"""
Firebase DB configuration.

Requires serviceAccountKey.json to be present in the directory.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

_cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "./serviceAccountKey.json")

if not os.path.exists(_cred_path):
    print(f"[FATAL] Firebase credentials not found at {_cred_path}")
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
