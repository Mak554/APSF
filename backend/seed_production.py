"""
seed_production.py
Seeds the production Render backend with the 3 real employees and fires
a fresh IT Hard campaign with the now-correct tracking links.
"""
import httpx, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "https://apsf.onrender.com"
client = httpx.Client(base_url=BASE, timeout=60)

# --- 1. Seed users ---
print("=== Seeding Users ===")
USERS = [
    {"full_name": "Mohammed Alkhateeb", "email": "m7md-_-0101@hotmail.com",  "department": "IT"},
    {"full_name": "Jassim Alharbi",     "email": "jassim.kfo@gmail.com",      "department": "Finance"},
    {"full_name": "Ibrahim Aloufi",     "email": "abra9778@gmail.com",         "department": "Engineering"},
]

real_ids = []
for u in USERS:
    r = client.post("/users/", json=u)
    if r.status_code == 201:
        uid = r.json()["user_id"]
        real_ids.append(uid)
        print(f"  [OK] {u['full_name']} -> {uid}")
    else:
        # Already exists — find by email
        all_users = client.get("/users/").json()
        match = next((x for x in all_users if x["email"] == u["email"]), None)
        if match:
            real_ids.append(match["user_id"])
            print(f"  [EXISTS] {u['full_name']} -> {match['user_id']}")
        else:
            print(f"  [ERR] {u['full_name']}: {r.status_code} {r.text[:80]}")

print(f"\nReal user IDs: {real_ids}")

# --- 2. Launch IT Hard campaign ---
print("\n=== Launching IT Hard Campaign ===")
payload = {
    "name": "IT Hard - Fixed Tracking Links",
    "phishing_type": "Credential_Harvest",
    "email_template_id": "tpl-it-hard",
    "subject": "[NexaCore Identity] Action Required: Zero-Trust Re-authentication",
    "sender_name": "IT Security Team",
    "sender_email": "security@apsf.site",
    "urgency_level": 5,
    "target_user_ids": real_ids,
}

rc = client.post("/campaigns/", json=payload)
if rc.status_code != 201:
    print(f"ERROR: {rc.status_code} {rc.text}")
    sys.exit(1)

cid = rc.json()["campaign_id"]
print(f"Campaign: {cid}")

rl = client.post(f"/campaigns/{cid}/launch")
res = rl.json()
print(f"Sent: {res.get('sent', 0)}, Failed: {res.get('failed', 0)}")
for e in res.get("errors", []):
    print(f"  Error: {e}")

print("\n[DONE] Emails sent! Check spam/junk in all 3 inboxes.")
print("The link in the email will open: https://apsf-sandy.vercel.app/landing/...")
