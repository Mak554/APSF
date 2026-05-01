"""
send_final_campaign.py
Waits for Render to redeploy, then fires a final IT Hard campaign with correct tracking links.
"""
import time, httpx, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "https://apsf.onrender.com"
client = httpx.Client(base_url=BASE, timeout=60)

print("Waiting 90s for Render to finish redeploying...")
time.sleep(90)

# Get unique real users only
REAL = {"m7md-_-0101@hotmail.com", "jassim.kfo@gmail.com", "abra9778@gmail.com"}
users = client.get("/users/").json()
seen_emails = set()
ids = []
for u in users:
    if u["email"] in REAL and u["email"] not in seen_emails:
        ids.append(u["user_id"])
        seen_emails.add(u["email"])

print(f"Targeting {len(ids)} unique real users: {list(seen_emails)}")

payload = {
    "name": "FINAL - IT Hard (fixed links)",
    "phishing_type": "Credential_Harvest",
    "email_template_id": "tpl-it-hard",
    "subject": "[NexaCore Identity] Action Required: Zero-Trust Re-authentication",
    "sender_name": "IT Security Team",
    "sender_email": "security@apsf.site",
    "urgency_level": 5,
    "target_user_ids": ids,
}

rc = client.post("/campaigns/", json=payload)
if rc.status_code != 201:
    print(f"ERROR creating campaign: {rc.status_code} {rc.text}")
    sys.exit(1)

cid = rc.json()["campaign_id"]
print(f"Campaign created: {cid}")

rl = client.post(f"/campaigns/{cid}/launch")
res = rl.json()
sent = res.get("sent", 0)
failed = res.get("failed", 0)
print(f"Result -> Sent: {sent}, Failed: {failed}")
for e in res.get("errors", []):
    print(f"  Error: {e}")

print("\nDone! Check spam/junk folders for:")
for e in seen_emails:
    print(f"  - {e}")
print("\nWhen you click the link it should open: https://apsf-sandy.vercel.app/landing/...")
