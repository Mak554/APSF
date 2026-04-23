"""
Seed Data Script - Populates APSF with realistic demo data.
Run AFTER the backend is started on port 8000.
Usage:  python seed_data.py
"""
import httpx
import sys

BASE_URL = "http://localhost:8009"

# Force UTF-8 output to avoid encoding issues on Windows
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ─── Realistic Saudi company employees ────────────────────────────────────────
USERS = [
    {"email": "m7md-_-0101@hotmail.com",  "full_name": "Mohammed Alkhateeb",   "department": "IT"},
    {"email": "jassim.kfo@gmail.com",    "full_name": "Jassim Alharbi",     "department": "Finance"},
    {"email": "abra9778@gmail.com",    "full_name": "Ibrahim Aloufi",     "department": "Engineering"},
    {"email": "nora.hassan@company.sa",       "full_name": "Nora Hassan",        "department": "IT Security"},
    {"email": "khalid.omar@company.sa",       "full_name": "Khalid Omar",        "department": "Operations"},
    {"email": "fatimah.ali@company.sa",       "full_name": "Fatimah Ali",        "department": "Human Resources"},
    {"email": "yasir.almayhubi@company.sa",   "full_name": "Yasir Almayhubi",   "department": "Management"},
    {"email": "sara.alqahtani@company.sa",    "full_name": "Sara Alqahtani",    "department": "Marketing"},
    {"email": "omar.alshehri@company.sa",     "full_name": "Omar Alshehri",     "department": "Finance"},
    {"email": "lina.alabdulaziz@company.sa",  "full_name": "Lina Alabdulaziz", "department": "Legal"},
    {"email": "faisal.almutairi@company.sa",  "full_name": "Faisal Almutairi", "department": "Operations"},
    {"email": "hana.alzahrani@company.sa",    "full_name": "Hana Alzahrani",    "department": "Human Resources"},
]

# ─── Campaigns ────────────────────────────────────────────────────────────────
CAMPAIGNS = [
    {
        "name": "Q1 - IT Password Reset Lure",
        "phishing_type": "Credential_Harvest",
        "email_template_id": "tpl-001",
        "subject": "Urgent: Your Password Expires in 24 Hours",
        "sender_name": "IT Security Team",
        "sender_email": "security@company.sa",
        "urgency_level": 4,
    },
    {
        "name": "Q1 - CEO Wire Transfer Spear Phish",
        "phishing_type": "Credential_Harvest",
        "email_template_id": "tpl-003",
        "subject": "Confidential - Urgent Wire Transfer Required",
        "sender_name": "Mohammed Al-CEO",
        "sender_email": "m.alghamdi@company.sa",
        "urgency_level": 5,
    },
    {
        "name": "Q2 - HR Benefits Update",
        "phishing_type": "Link_Only",
        "email_template_id": "tpl-002",
        "subject": "Action Required: Update Your Benefits by Friday",
        "sender_name": "HR Department",
        "sender_email": "hr@company.sa",
        "urgency_level": 3,
    },
    {
        "name": "Q3 - Month 3 Adaptive Retest",
        "phishing_type": "Credential_Harvest",
        "email_template_id": "tpl-001",
        "subject": "Security Alert: Verify Your Account Immediately",
        "sender_name": "IT Help Desk",
        "sender_email": "helpdesk@company.sa",
        "urgency_level": 4,
    },
]

# ─── Interaction simulation ────────────────────────────────────────────────────
# (user_index, campaign_index, event)  event = "click" | "submit" | "report"
INTERACTIONS = [
    # Q1 Password Reset - high failure rate
    (0, 0, "click"),  (0, 0, "submit"),  # Ahmad - Finance (high risk)
    (4, 0, "click"),  (4, 0, "submit"),  # Jassim - Finance
    (8, 0, "click"),                     # Omar - Finance (link only)
    (1, 0, "click"),                     # Fatimah - HR
    (7, 0, "report"),                    # Sara reported it
    (3, 0, "report"),                    # Nora (IT) reported it

    # Q1 CEO Wire - very high failure (spear phishing)
    (0, 1, "click"),  (0, 1, "submit"),
    (4, 1, "click"),  (4, 1, "submit"),
    (6, 1, "click"),                     # Yasir - Management
    (9, 1, "report"),                    # Lina - Legal reported

    # Q2 HR Benefits - medium failure
    (1, 2, "click"),
    (11, 2, "click"), (11, 2, "submit"),
    (2, 2, "click"),
    (5, 2, "report"),                    # Ibrahim reported
    (3, 2, "report"),

    # Q3 Adaptive Retest - lower failure (training impact)
    (8, 3, "click"),                     # Omar still struggling
    (7, 3, "report"),
    (3, 3, "report"),
    (5, 3, "report"),
    (9, 3, "report"),
    (10, 3, "report"),
]


def seed():
    print("=== APSF Seed Data Script ===")
    print("=" * 45)

    client = httpx.Client(base_url=BASE_URL, timeout=10)

    # 1. Create users
    print("\n[1/3] Creating 12 employees...")
    user_ids = []
    for u in USERS:
        try:
            r = client.post("/users/", json=u)
            if r.status_code == 201:
                user_ids.append(r.json()["user_id"])
                print(f"  [OK]    {u['full_name']} ({u['department']})")
            else:
                print(f"  [ERROR] {u['full_name']}: {r.status_code}")
                user_ids.append(None)
        except Exception as e:
            print(f"  [ERROR] {e}")
            user_ids.append(None)

    # 2. Create campaigns
    print(f"\n[2/3] Creating {len(CAMPAIGNS)} campaigns...")
    campaign_ids = []
    for c in CAMPAIGNS:
        payload = {**c, "target_user_ids": [uid for uid in user_ids if uid]}
        try:
            r = client.post("/campaigns/", json=payload)
            if r.status_code == 201:
                campaign_ids.append(r.json()["campaign_id"])
                print(f"  [OK]    {c['name']}")
            else:
                print(f"  [ERROR] {c['name']}: {r.status_code} {r.text[:80]}")
                campaign_ids.append(None)
        except Exception as e:
            print(f"  [ERROR] {e}")
            campaign_ids.append(None)

    # 3. Simulate interactions
    print(f"\n[3/3] Simulating {len(INTERACTIONS)} interactions...")
    for user_idx, camp_idx, event in INTERACTIONS:
        uid = user_ids[user_idx] if user_idx < len(user_ids) else None
        cid = campaign_ids[camp_idx] if camp_idx < len(campaign_ids) else None
        if not uid or not cid:
            continue
        name = USERS[user_idx]["full_name"]
        try:
            if event == "click":
                client.get(f"/track/click/{cid}/{uid}")
                print(f"  [CLICK]  {name} - Campaign {camp_idx + 1}")
            elif event == "submit":
                client.post(f"/track/submit/{cid}/{uid}", json={"demo": "data"})
                print(f"  [SUBMIT] {name} - Campaign {camp_idx + 1}")
            elif event == "report":
                client.post(f"/track/report/{cid}/{uid}")
                print(f"  [REPORT] {name} - Campaign {camp_idx + 1}")
        except Exception as e:
            print(f"  [ERROR]  {name}: {e}")

    print("\n[DONE] Seeding complete!")
    print("Refresh the dashboard at http://localhost:3000")
    print("=" * 45)


if __name__ == "__main__":
    seed()
