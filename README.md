# APSF – Adaptive Phishing Simulation Framework

A full-stack implementation of the Adaptive Phishing Simulation Framework described in the project report.

## Project Structure

```
apsf/
├── backend/              # Python FastAPI backend
│   ├── main.py           # FastAPI application entry point
│   ├── firebase_config.py # Firebase Admin SDK init
│   ├── atm_service.py    # Adaptive Training Module (ML risk scoring)
│   ├── pse_service.py    # Phishing Simulation Engine (email sending)
│   ├── upt_service.py    # User Performance Tracker (Firestore CRUD)
│   ├── models/schemas.py  # Pydantic data models
│   ├── routers/          # FastAPI routers (users, campaigns, tracking, atm, dashboard)
│   └── requirements.txt
└── frontend/             # Next.js frontend
    └── app/
        ├── page.tsx                         # Admin Dashboard
        ├── campaigns/new/page.tsx           # Campaign Creation Wizard
        └── landing/[campaign_id]/[user_id]/ # Phishing Landing Page + Training
            └── page.tsx
```

## Setup & Running

### 1. Firebase Setup
1. Create a Firebase project at https://console.firebase.google.com
2. Enable **Firestore Database** (Native mode)
3. Go to **Project Settings → Service Accounts** → Generate new private key
4. Save the JSON as `backend/serviceAccountKey.json`

### 2. Backend Setup
```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
copy .env.example .env
# Edit .env with your SMTP credentials and Firebase path

# Start the API server
uvicorn main:app --reload --port 8000
```

**API Docs**: Visit http://localhost:8000/docs for the full interactive Swagger UI.

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies (already done during setup)
npm install

# Start the development server
npm run dev
```

**Dashboard**: Visit http://localhost:3000

## Key API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/users/` | Create an employee user |
| GET | `/users/` | List all users |
| POST | `/campaigns/` | Create a campaign |
| POST | `/campaigns/{id}/launch` | Send phishing emails |
| GET | `/track/open/{campaign_id}/{user_id}` | Track email open (pixel) |
| GET | `/track/click/{campaign_id}/{user_id}` | Track link click |
| POST | `/track/submit/{campaign_id}/{user_id}` | Track form submission |
| POST | `/track/report/{campaign_id}/{user_id}` | Track phishing report |
| GET | `/atm/risk-score/{user_id}` | Get user risk score |
| GET | `/dashboard/stats` | Get dashboard analytics |

## Architecture

```
Employee → Phishing Email → Clicks Link
                                  ↓
                    PSE tracks click → UPT logs event
                                  ↓
                    ATM recalculates P_fail (Logistic Regression)
                                  ↓
                    High Risk? → Assign mandatory training
                                  ↓
                    Employee sees landing page + training module
                                  ↓
                    Admin Dashboard shows updated analytics
```

## Risk Tiers

| Tier | P(Fail) Range | Action |
|------|---------------|--------|
| 🔴 High | ≥ 0.70 | Mandatory training + 2x/week simulations |
| 🟡 Medium | 0.40–0.69 | Optional training + bi-weekly simulations |
| 🟢 Low | < 0.40 | Monthly monitoring simulations |
