"""
Dashboard API: GET /api/dashboard/stats
Public aggregated trends: top scam types, 30-day trends, language distribution, top red flags.
Strictly zero PII is accessed or exposed.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.database import get_db, AnonymizedCheckLog
from app.models.schemas import DashboardStatsResponse

router = APIRouter(tags=["Public Dashboard"])


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Returns aggregated public statistical trends for citizen education.
    """
    total_count = db.query(AnonymizedCheckLog).count()

    # Determine if current dataset consists solely of sample data
    real_count = db.query(AnonymizedCheckLog).filter(AnonymizedCheckLog.is_sample == False).count()
    is_sample_data = (real_count == 0 and total_count > 0)

    # Risk bucket distribution
    scam_count = db.query(AnonymizedCheckLog).filter(AnonymizedCheckLog.risk_bucket == "LIKELY SCAM").count()
    suspicious_count = db.query(AnonymizedCheckLog).filter(AnonymizedCheckLog.risk_bucket == "SUSPICIOUS").count()
    genuine_count = db.query(AnonymizedCheckLog).filter(AnonymizedCheckLog.risk_bucket == "LOOKS GENUINE").count()

    # Scam type breakdown
    scam_types_raw = (
        db.query(AnonymizedCheckLog.scam_type, func.count(AnonymizedCheckLog.id).label("count"))
        .filter(AnonymizedCheckLog.risk_bucket.in_(["LIKELY SCAM", "SUSPICIOUS"]))
        .group_by(AnonymizedCheckLog.scam_type)
        .order_by(func.count(AnonymizedCheckLog.id).desc())
        .limit(8)
        .all()
    )
    scam_type_breakdown = [{"name": s[0] or "Unclassified", "value": s[1]} for s in scam_types_raw]

    # Daily trends for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_raw = (
        db.query(
            func.date(AnonymizedCheckLog.timestamp).label("day"),
            func.count(AnonymizedCheckLog.id).label("count")
        )
        .filter(AnonymizedCheckLog.timestamp >= thirty_days_ago)
        .group_by(func.date(AnonymizedCheckLog.timestamp))
        .order_by(func.date(AnonymizedCheckLog.timestamp))
        .all()
    )
    daily_trends = [{"date": str(d[0]), "checks": d[1]} for d in daily_raw]

    # Top red flags / categories
    top_flags_raw = (
        db.query(AnonymizedCheckLog.top_rule_category, func.count(AnonymizedCheckLog.id).label("count"))
        .filter(AnonymizedCheckLog.top_rule_category != None)
        .group_by(AnonymizedCheckLog.top_rule_category)
        .order_by(func.count(AnonymizedCheckLog.id).desc())
        .limit(6)
        .all()
    )
    top_red_flags = [{"category": f[0], "count": f[1]} for f in top_flags_raw]

    # Language usage distribution
    lang_raw = (
        db.query(AnonymizedCheckLog.language, func.count(AnonymizedCheckLog.id).label("count"))
        .group_by(AnonymizedCheckLog.language)
        .order_by(func.count(AnonymizedCheckLog.id).desc())
        .all()
    )
    lang_labels = {
        "en": "English", "hi": "Hindi (हिंदी)", "mr": "Marathi (मराठी)", 
        "ta": "Tamil (தமிழ்)", "te": "Telugu (తెలుగు)", "bn": "Bengali (বাংলা)", 
        "gu": "Gujarati (ગુજરાતી)", "kn": "Kannada (ಕನ್ನಡ)"
    }
    language_distribution = [
        {"language": lang_labels.get(l[0], l[0].upper()), "code": l[0], "count": l[1]} 
        for l in lang_raw
    ]

    return DashboardStatsResponse(
        total_checks=total_count,
        scams_detected=scam_count,
        suspicious_detected=suspicious_count,
        genuine_detected=genuine_count,
        scam_type_breakdown=scam_type_breakdown,
        daily_trends=daily_trends,
        top_red_flags=top_red_flags,
        language_distribution=language_distribution,
        is_sample_data=is_sample_data
    )

