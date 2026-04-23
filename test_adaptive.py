import sys
from pprint import pprint

# Setup paths
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend.models.schemas import UserCreate, CampaignCreate, Campaign, PhishingType, EventType
from backend import upt_service
from backend import atm_service

def run_test():
    print("Creating user...")
    user = upt_service.create_user(UserCreate(
        email="test_adaptive@example.com",
        full_name="Adaptive Tester",
        department="Testing"
    ))
    user_id = user.user_id
    
    print("Creating campaign (Urgency)...")
    campaign1 = upt_service.get_db().collection("campaigns").document("test-camp-1")
    campaign1.set(Campaign(
        campaign_id="test-camp-1",
        name="Urgent Test",
        phishing_type=PhishingType.URGENCY,
        email_template_id="tpl-001",
        sender_name="IT",
        sender_email="it@test.com",
        subject="Test",
        urgency_level=5,
        target_count=1
    ).model_dump())
    
    print(f"Logging SENT event for campaign 1")
    # we need to simulate the delay between sent and clicked
    import time
    upt_service.log_event(user_id, "test-camp-1", EventType.EMAIL_SENT)
    upt_service.increment_user_stats(user_id, EventType.EMAIL_SENT, "test-camp-1")
    
    # Wait minimal time to have response time > 0
    time.sleep(1)
    
    print(f"Logging CLICKED event for campaign 1")
    upt_service.log_event(user_id, "test-camp-1", EventType.LINK_CLICKED)
    upt_service.increment_user_stats(user_id, EventType.LINK_CLICKED, "test-camp-1")
    atm_service.process_user_event(user_id, "test-camp-1", EventType.LINK_CLICKED)
    
    user_profile = upt_service.get_user(user_id)
    print("\n--- User Profile After Campaign 1 ---")
    print(f"Total Failures: {user_profile.total_failures}")
    print(f"Susceptibility: {user_profile.susceptibility_vector}")
    print(f"Avg Response Time (seconds): {user_profile.avg_response_time:.2f}")
    
    recommendation = atm_service.recommend_next_simulation(user_id)
    print(f"\n--- Recommendation ---")
    pprint(recommendation)

if __name__ == "__main__":
    # Ensure local DB is used
    import os
    os.environ['USE_LOCAL_DB'] = 'true'
    run_test()
