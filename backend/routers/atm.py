"""ATM (Adaptive Training Module) API routes."""
from fastapi import APIRouter
import atm_service
import upt_service

router = APIRouter()


@router.post("/train-model")
def retrain_model():
    """Retrains the Logistic Regression risk model with the latest data."""
    atm_service.train_model(save=True)
    return {"message": "Model retrained and saved successfully."}


@router.get("/risk-scores")
def get_all_risk_scores():
    """Returns current risk scores for all users (batch calculation)."""
    return atm_service.get_all_risk_scores()


@router.get("/risk-score/{user_id}")
def get_user_risk_score(user_id: str):
    """Calculates and returns the current risk score for a specific user."""
    from fastapi import HTTPException
    user = upt_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    p_fail, tier = atm_service.calculate_risk(user)
    return {"user_id": user_id, "p_fail": p_fail, "risk_tier": tier.value}


@router.get("/recommendation/{user_id}")
def get_user_recommendation(user_id: str):
    """Returns the recommended next simulation type based on user pattern and risk."""
    from fastapi import HTTPException
    recommendation = atm_service.recommend_next_simulation(user_id)
    if "error" in recommendation:
        raise HTTPException(status_code=404, detail=recommendation["error"])
    return recommendation


@router.get("/training-assignments/{user_id}")
def get_user_assignments(user_id: str):
    """Returns all training assignments for a user."""
    from firebase_config import get_db
    assignments = (
        get_db()
        .collection("training-assignments")
        .where("user_id", "==", user_id)
        .stream()
    )
    return [a.to_dict() for a in assignments]


@router.post("/complete-training/{assignment_id}")
def complete_training(assignment_id: str):
    """Marks a training assignment as complete."""
    upt_service.complete_training(assignment_id)
    return {"message": "Training marked as complete.", "assignment_id": assignment_id}


@router.get("/modules")
def get_training_modules():
    """Returns the training module catalog."""
    return {tier.value: modules for tier, modules in atm_service.TRAINING_MODULES.items()}
