"""
fix_campaigns.py
Lists all campaigns, launches any drafts, and sends a fresh test campaign.
"""
import httpx, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "https://apsf.onrender.com"
client = httpx.Client(base_url=BASE, timeout=60)

# 1. List all campaigns
print("=== All Campaigns ===")
r = client.get("/campaigns/")
campaigns = r.json()
for c in campaigns:
    status = c.get("status", "unknown")
    sent = c.get("emails_sent", 0)
    name = c.get("name", "")
    cid = c.get("campaign_id", "")
    print(f"  [{status:8s}] sent={sent} | {name} | {cid}")

# 2. Launch any that are still in Draft
print("\n=== Launching Draft Campaigns ===")
drafts = [c for c in campaigns if c.get("status") == "Draft"]
if not drafts:
    print("  No draft campaigns found.")
else:
    for c in drafts:
        cid = c["campaign_id"]
        name = c["name"]
        rl = client.post(f"/campaigns/{cid}/launch")
        if rl.status_code == 200:
            res = rl.json()
            print(f"  [OK] '{name}' -> Sent={res.get('sent',0)}, Failed={res.get('failed',0)}")
            for e in res.get("errors", []):
                print(f"       Error: {e}")
        else:
            print(f"  [ERR] '{name}': {rl.status_code} {rl.text[:100]}")

# 3. Send a fresh IT Hard campaign to all real users
print("\n=== Sending Fresh IT Hard Campaign ===")
r = client.get("/users/")
all_users = r.json()
REAL_EMAILS = {"m7md-_-0101@hotmail.com", "jassim.kfo@gmail.com", "abra9778@gmail.com"}
real_ids = [u["user_id"] for u in all_users if u["email"] in REAL_EMAILS]
print(f"  Targeting {len(real_ids)} real users")

payload = {
    "name": "IT Security Hard - Final Test",
    "phishing_type": "Credential_Harvest",
    "email_template_id": "tpl-it-hard",
    "subject": "[NexaCore Identity] Action Required: Zero-Trust Re-authentication",
    "sender_name": "IT Security Team",
    "sender_email": "security@apsf.site",
    "urgency_level": 5,
    "difficulty": "Hard",
    "target_user_ids": real_ids,
}
rc = client.post("/campaigns/", json=payload)
if rc.status_code != 201:
    print(f"  [ERR] Create: {rc.status_code} {rc.text[:100]}")
    sys.exit(1)

cid = rc.json()["campaign_id"]
print(f"  Campaign created: {cid}")

rl = client.post(f"/campaigns/{cid}/launch")
res = rl.json()
print(f"  Result -> Sent: {res.get('sent', 0)}, Failed: {res.get('failed', 0)}")
for e in res.get("errors", []):
    print(f"  Error: {e}")

print("\n=== DONE ===")
print("Check spam/junk in all 3 inboxes!")
print(f"  Tracking link base: https://apsf-sandy.vercel.app/landing")
