"""
Adaptive Training Module (ATM) Service
Uses scikit-learn Logistic Regression to calculate the Probability of Failure (P_fail)
for each user and assign them to a risk tier (High, Medium, Low).
"""
import os
import pickle
import numpy as np
import pandas as pd
from typing import List, Tuple
from datetime import datetime, timezone

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

from models.schemas import RiskTier, EventType, UserProfile
import upt_service

# Path to the persisted model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "risk_model.pkl")

# Training modules catalog – mapped by risk tier
TRAINING_MODULES = {
    RiskTier.HIGH: [
        {"id": "tm-h-001", "title": "Phishing Attack Deep Dive: Credential Harvesting"},
        {"id": "tm-h-002", "title": "Recognizing Spoofed Senders & Urgent Requests"},
        {"id": "tm-h-003", "title": "What To Do When You've Clicked a Suspicious Link"},
    ],
    RiskTier.MEDIUM: [
        {"id": "tm-m-001", "title": "Phishing Fundamentals: How to Spot Red Flags"},
        {"id": "tm-m-002", "title": "Safe Email Practices at Work"},
    ],
    RiskTier.LOW: [
        {"id": "tm-l-001", "title": "Security Quick Tips: Monthly Refresher"},
    ],
}


# ─────────────────────────────────────────
# Feature Extraction
# ─────────────────────────────────────────

def extract_features(user: UserProfile) -> np.ndarray:
    """
    Converts a UserProfile into a feature vector for the ML model.
    """
    failure_rate = (
        user.total_failures / user.total_simulations
        if user.total_simulations > 0
        else 0.0
    )

    if user.last_simulation_date:
        days_since = (datetime.now(timezone.utc) - user.last_simulation_date).days
    else:
        days_since = 999  # User has never been tested 

    sus_vec = user.susceptibility_vector
    avg_resp = user.avg_response_time
    
    def rate(ptype):
        total_fail_for_type = sus_vec.get(ptype, 0)
        return total_fail_for_type / user.total_failures if user.total_failures > 0 else 0.0

    features = np.array([
        user.total_simulations,
        failure_rate,
        user.total_reports,
        min(days_since, 365),
        min(avg_resp, 600), # Cap at 10 minutes
        rate("Credential_Harvest"),
        rate("Link_Only"),
        rate("Attachment"),
        rate("Urgency"),
    ]).reshape(1, -1)

    return features


# ─────────────────────────────────────────
# Model Training (using mock/seed data)
# ─────────────────────────────────────────

def _generate_seed_training_data() -> Tuple[np.ndarray, np.ndarray]:
    """Generates realistic synthetic training data for the 9-feature model."""
    np.random.seed(42)

    # Low-Risk users (label=0) - slow response, low rates
    low_risk = pd.DataFrame({
        "total_simulations": np.random.randint(5, 20, 200),
        "failure_rate": np.random.uniform(0.0, 0.25, 200),
        "total_reports": np.random.randint(2, 10, 200),
        "days_since_training": np.random.randint(0, 30, 200),
        "avg_response": np.random.uniform(120.0, 600.0, 200),
        "rate_cred": np.random.uniform(0.0, 0.2, 200),
        "rate_link": np.random.uniform(0.0, 0.2, 200),
        "rate_att": np.random.uniform(0.0, 0.2, 200),
        "rate_urg": np.random.uniform(0.0, 0.2, 200),
    })
    low_risk["label"] = 0

    # High/Medium-Risk users (label=1) - mostly impulsive or highly susceptible
    high_risk = pd.DataFrame({
        "total_simulations": np.random.randint(1, 15, 300),
        "failure_rate": np.random.uniform(0.4, 1.0, 300),
        "total_reports": np.random.randint(0, 3, 300),
        "days_since_training": np.random.randint(30, 365, 300),
        "avg_response": np.random.uniform(5.0, 60.0, 300), # highly impulsive
        "rate_cred": np.random.uniform(0.3, 0.8, 300),
        "rate_link": np.random.uniform(0.2, 0.6, 300),
        "rate_att": np.random.uniform(0.1, 0.5, 300),
        "rate_urg": np.random.uniform(0.5, 0.9, 300),
    })
    high_risk["label"] = 1

    data = pd.concat([low_risk, high_risk], ignore_index=True).sample(frac=1, random_state=42)
    features = [
        "total_simulations", "failure_rate", "total_reports", "days_since_training", 
        "avg_response", "rate_cred", "rate_link", "rate_att", "rate_urg"
    ]
    X = data[features].values
    y = data["label"].values
    return X, y


def train_model(save=True) -> Pipeline:
    """Trains the Logistic Regression pipeline and optionally persists it to disk."""
    X, y = _generate_seed_training_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(max_iter=1000, random_state=42, C=0.5)),
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    report = classification_report(y_test, y_pred, target_names=["Low/Safe", "High/Medium Risk"])
    print("=== ATM Model Training Report ===")
    print(report)

    if save:
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(pipeline, f)
        print(f"Model saved to {MODEL_PATH}")

    return pipeline


def load_model() -> Pipeline:
    """Loads the persisted model, training a fresh one if not found."""
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    print("No saved model found. Training a new one with seed data…")
    return train_model(save=True)


# ─────────────────────────────────────────
# Risk Scoring & Tier Assignment
# ─────────────────────────────────────────

def calculate_risk(user: UserProfile) -> Tuple[float, RiskTier]:
    """
    Calculates P_fail and the risk tier for a given user.
    
    Returns:
        (p_fail, risk_tier) tuple
    """
    model = load_model()
    features = extract_features(user)
    # Get probability of class 1 (failure)
    p_fail = float(model.predict_proba(features)[0][1])

    if p_fail >= 0.70:
        tier = RiskTier.HIGH
    elif p_fail >= 0.40:
        tier = RiskTier.MEDIUM
    else:
        tier = RiskTier.LOW

    return round(p_fail, 4), tier


# ─────────────────────────────────────────
# Core ATM Decision Loop
# ─────────────────────────────────────────

def process_user_event(user_id: str, campaign_id: str, event_type: EventType):
    """
    The main ATM control loop.
    Called after any significant user event (click, submission, report).
    
    1. Fetch user data from UPT.
    2. Recalculate P_fail.
    3. Update user risk score in Firestore.
    4. If risky, assign appropriate training.
    """
    user = upt_service.get_user(user_id)
    if not user:
        print(f"[ATM] User {user_id} not found, skipping.")
        return

    p_fail, tier = calculate_risk(user)
    print(f"[ATM] User {user.email}: P_fail={p_fail:.2%}, Tier={tier.value}")

    # Update Firestore with new scores
    upt_service.update_user_risk(user_id, p_fail, tier)

    # Assign training based on tier and triggering event
    if event_type in (EventType.LINK_CLICKED, EventType.DATA_SUBMITTED):
        _assign_training_for_failure(user_id, campaign_id, tier, p_fail)


def _assign_training_for_failure(
    user_id: str, campaign_id: str, tier: RiskTier, p_fail: float
):
    """Selects and assigns the appropriate training module based on risk tier."""
    modules = TRAINING_MODULES.get(tier, TRAINING_MODULES[RiskTier.LOW])
    # Pick the first relevant module (in production: avoid reassigning the same module)
    module = modules[0]
    is_mandatory = tier == RiskTier.HIGH

    reason = (
        f"User clicked/submitted in a phishing simulation. "
        f"P_fail={p_fail:.2%}, Risk Tier={tier.value}."
    )

    assignment = upt_service.assign_training(
        user_id=user_id,
        campaign_id=campaign_id,
        module_id=module["id"],
        module_title=module["title"],
        reason=reason,
        is_mandatory=is_mandatory,
    )
    print(f"[ATM] Training assigned: '{module['title']}' for user {user_id}. Mandatory={is_mandatory}")
    return assignment


def get_all_risk_scores() -> List[dict]:
    """Batch-recalculates risk scores for all users. Used for dashboard refresh."""
    users = upt_service.get_all_users()
    results = []
    for user in users:
        p_fail, tier = calculate_risk(user)
        results.append({
            "user_id": user.user_id,
            "email": user.email,
            "p_fail": p_fail,
            "tier": tier.value,
        })
    return results

def recommend_next_simulation(user_id: str) -> dict:
    """
    Recommends the best next simulation for a user based on their adaptive pattern.
    - Low avg_response_time -> assign Urgency testing.
    - High Risk Tier -> Reduce difficulty (Link Only).
    - Low Risk Tier -> Increase difficulty (Credential Harvest).
    """
    user = upt_service.get_user(user_id)
    if not user:
        return {"error": "User not found"}
        
    p_fail, tier = calculate_risk(user)
    
    # 1. Check impulsivity first
    if 0 < user.avg_response_time < 60: # Under 1 minute
        return {
            "recommended_type": "Urgency",
            "urgency_level": 5,
            "reason": "User exhibits high impulsivity (clicks very fast). Needs extreme urgency testing."
        }
        
    # 2. Check susceptibility vector
    sus_vec = user.susceptibility_vector
    strongest_weakness = max(sus_vec, key=sus_vec.get) if sus_vec else None
    
    if tier == RiskTier.HIGH:
        # User is high risk, lower difficulty to build baseline
        return {
            "recommended_type": "Link_Only",
            "urgency_level": 1,
            "reason": "User is High Risk. Recommending baseline Link Only campaign."
        }
    elif tier == RiskTier.LOW:
        # User is low risk, challenge them
        return {
            "recommended_type": "Credential_Harvest",
            "urgency_level": 4,
            "reason": "User is Low Risk. Increasing difficulty to Credential Harvesting."
        }
    else:
        # Medium risk, target their biggest weakness
        rec_type = strongest_weakness if strongest_weakness else "Attachment"
        return {
            "recommended_type": rec_type,
            "urgency_level": 3,
            "reason": f"User is Medium Risk. Targeting their specific weakness: {rec_type}."
        }

