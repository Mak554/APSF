"""Add missing real-email users to the production Render database."""
import httpx, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "https://apsf.onrender.com"
client = httpx.Client(base_url=BASE, timeout=30)

users = [
    {"full_name": "Jassim Alharbi",  "email": "jassim.kfo@gmail.com", "department": "Finance"},
    {"full_name": "Ibrahim Aloufi",  "email": "abra9778@gmail.com",    "department": "Engineering"},
]

for u in users:
    r = client.post("/users/", json=u)
    if r.status_code == 201:
        data = r.json()
        print(f"[OK] {u['full_name']} -> {data['user_id']}")
    else:
        print(f"[ERR] {u['full_name']}: {r.status_code} {r.text[:120]}")

# Now launch a new campaign for all 3
print("\nFetching all real users...")
r = client.get("/users/")
all_users = r.json()
real_ids = [u["user_id"] for u in all_users if not u["email"].endswith("@company.sa")]
print(f"Found {len(real_ids)} real-email targets")

payload = {
    "name": "Live Test - Hard CEO Spear Phish",
    "phishing_type": "Credential_Harvest",
    "email_template_id": "tpl-ceo-hard",
    "subject": "[BOARD DIRECTIVE] Project Falcon: Escrow Authorization - Strictly Confidential",
    "sender_name": "CEO Office",
    "sender_email": "security@apsf.site",
    "urgency_level": 5,
    "difficulty": "Hard",
    "target_user_ids": real_ids,
}
rc = client.post("/campaigns/", json=payload)
if rc.status_code != 201:
    print(f"[ERR] Create campaign: {rc.status_code} {rc.text}")
    sys.exit(1)

cid = rc.json()["campaign_id"]
print(f"Campaign created: {cid}")

rl = client.post(f"/campaigns/{cid}/launch")
res = rl.json()
print(f"\nResult -> Sent: {res.get('sent', 0)}, Failed: {res.get('failed', 0)}")
for e in res.get("errors", []):
    print(f"  Error: {e}")
print("\nCheck all 3 inboxes!")
