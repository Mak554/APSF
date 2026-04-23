"""
launch_campaign.py
Fetches the 3 real employees from the DB and launches a phishing campaign
sending real emails via the configured SMTP settings.
"""
import httpx
import sys
import json

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://localhost:8009"
REAL_EMAILS = {"m7md-_-0101@hotmail.com", "jassim.kfo@gmail.com", "abra9778@gmail.com"}

client = httpx.Client(base_url=BASE_URL, timeout=60)

# 1. Get all users and find the real employee IDs
print("=== Fetching employees ===")
r = client.get("/users/")
users = r.json()
real_ids = []
for u in users:
    marker = "<-- REAL EMAIL" if u["email"] in REAL_EMAILS else ""
    print(f"  {u['full_name']:25s}  {u['email']:35s}  {marker}")
    if u["email"] in REAL_EMAILS:
        real_ids.append(u["user_id"])

print(f"\nReal employee IDs ({len(real_ids)}): {real_ids}")

if not real_ids:
    print("[ERROR] No real employees found in DB. Please run seed_data.py first.")
    sys.exit(1)

# 2. Create a fresh campaign targeting only the 3 real employees
print("\n=== Creating targeted campaign ===")
campaign_payload = {
    "name": "Live Test - IT Security Alert",
    "phishing_type": "Credential_Harvest",
    "email_template_id": "tpl-001",
    "subject": "Urgent: Your Password Expires in 24 Hours",
    "sender_name": "IT Security Team",
    "sender_email": "mak554321xi@gmail.com",
    "urgency_level": 4,
    "target_user_ids": real_ids,
}

rc = client.post("/campaigns/", json=campaign_payload)
if rc.status_code != 201:
    print(f"[ERROR] Failed to create campaign: {rc.status_code} {rc.text}")
    sys.exit(1)

campaign = rc.json()
campaign_id = campaign["campaign_id"]
print(f"  [OK] Campaign created: {campaign['name']} (id: {campaign_id})")

# 3. Launch the campaign (triggers real SMTP send)
print("\n=== Launching campaign (sending real emails) ===")
rl = client.post(f"/campaigns/{campaign_id}/launch")
if rl.status_code != 200:
    print(f"[ERROR] Launch failed: {rl.status_code} {rl.text}")
    sys.exit(1)

result = rl.json()
print(f"  Sent:   {result.get('sent', 0)}")
print(f"  Failed: {result.get('failed', 0)}")
if result.get("errors"):
    print("  Errors:")
    for e in result["errors"]:
        print(f"    - {e}")

print("\n[DONE] Check the inboxes of all 3 employees!")
print("  m7md-_-0101@hotmail.com  (Mohammed Alkhateeb)")
print("  jassim.kfo@gmail.com     (Jassim Alharbi)")
print("  abra9778@gmail.com       (Ibrahim Aloufi)")
