"""Dashboard summary API route."""
from fastapi import APIRouter
from models.schemas import RiskTier
import upt_service, atm_service

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats():
    """
    Returns aggregated statistics for the admin dashboard.
    Includes overall click rates, risk distribution, and top-risk users.
    """
    users = upt_service.get_all_users()
    campaigns = upt_service.get_all_campaigns()

    total_emails_sent = sum(c.emails_sent for c in campaigns)
    total_clicks = sum(c.clicks for c in campaigns)
    overall_click_rate = (total_clicks / total_emails_sent * 100) if total_emails_sent > 0 else 0

    risk_distribution = {RiskTier.HIGH: 0, RiskTier.MEDIUM: 0, RiskTier.LOW: 0, RiskTier.NEW: 0}
    for user in users:
        risk_distribution[user.risk_tier] = risk_distribution.get(user.risk_tier, 0) + 1

    top_risk_users = sorted(users, key=lambda u: u.p_fail, reverse=True)[:10]

    return {
        "total_users": len(users),
        "total_campaigns": len(campaigns),
        "overall_click_rate": round(overall_click_rate, 2),
        "risk_distribution": {k.value: v for k, v in risk_distribution.items()},
        "top_risk_users": [u.model_dump() for u in top_risk_users],
        "recent_campaigns": [c.model_dump() for c in campaigns[:5]],
        "campaign_click_rates": [
            {
                "name": c.name,
                "click_rate": round((c.clicks / c.emails_sent * 100) if c.emails_sent > 0 else 0, 2),
                "emails_sent": c.emails_sent,
                "clicks": c.clicks,
                "reports": c.reports,
            }
            for c in campaigns
        ],
    }
