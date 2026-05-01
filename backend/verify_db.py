import os
import sys

sys.path.append(os.path.dirname(__file__))

from firebase_config import get_db

def test_queries():
    try:
        from firebase_admin import firestore
        db = get_db()
        
        print("Testing get_all_campaigns query...")
        docs = db.collection("campaigns").order_by("created_at", direction=firestore.Query.DESCENDING).limit(1).stream()
        for d in docs: pass
        print("campaigns query successful.")

        print("Testing get_user_events query (where + order_by)...")
        docs = db.collection("events").where("user_id", "==", "test_user").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1).stream()
        for d in docs: pass
        print("events query successful.")
            
    except Exception as e:
        print(f"Error querying Firestore: {e}")

if __name__ == '__main__':
    test_queries()
