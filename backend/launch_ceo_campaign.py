"""
launch_ceo_campaign.py
Sends the CEO Wire Transfer spear-phishing campaign to real employees.
"""
import httpx, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://localhost:8009"
REAL_EMAILS = {"m7md-_-0101@hotmail.com", "jassim.kfo@gmail.com", "abra9778@gmail.com"}

client = httpx.Client(base_url=BASE_URL, timeout=60)

print("=== Fetching employees ===")
users = client.get("/users/").json()
real_ids = [u["user_id"] for u in users if u["email"] in REAL_EMAILS]
print(f"Real employee IDs ({len(real_ids)}): {real_ids}")

if not real_ids:
    print("[ERROR] No real employees found. Run seed_data.py first.")
    sys.exit(1)

print("\n=== Creating CEO Wire Transfer campaign ===")
rc = client.post("/campaigns/", json={
    "name": "Live Test - CEO Wire Transfer",
    "phishing_type": "Credential_Harvest",
    "email_template_id": "tpl-003",
    "subject": "Confidential - Urgent Wire Transfer Required",
    "sender_name": "Mohammed Al-Ghamdi (CEO)",
    "sender_email": "mak554321xi@gmail.com",
    "urgency_level": 5,
    "target_user_ids": real_ids,
})
if rc.status_code != 201:
    print(f"[ERROR] {rc.status_code} {rc.text}"); sys.exit(1)

campaign_id = rc.json()["campaign_id"]
print(f"  [OK] Campaign created (id: {campaign_id})")

print("\n=== Launching campaign ===")
rl = client.post(f"/campaigns/{campaign_id}/launch")
result = rl.json()
print(f"  Sent:   {result.get('sent', 0)}")
print(f"  Failed: {result.get('failed', 0)}")
print("\n[DONE] Check the inboxes!")
