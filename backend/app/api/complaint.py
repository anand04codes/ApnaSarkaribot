"""
Complaint Generator API: POST /api/generate-complaint
Generates ready-to-paste incident report for cybercrime.gov.in / Helpline 1930.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.rules_engine import IndianScamRulesEngine
from app.services.complaint_generator import ComplaintGenerator
from app.models.schemas import ComplaintSummary

router = APIRouter(tags=["Complaint Generation"])
rules_engine = IndianScamRulesEngine()


class ComplaintRequest(BaseModel):
    text: str
    claimed_agency: Optional[str] = None
    user_state: Optional[str] = None


@router.post("/generate-complaint", response_model=ComplaintSummary)
async def generate_complaint(payload: ComplaintRequest):
    """
    Extracts suspect phone numbers, URLs, UPI IDs, and demanded amounts from content,
    and produces a structured formal complaint ready to paste into cybercrime.gov.in.
    """
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    rules_eval = rules_engine.evaluate(payload.text)
    return ComplaintGenerator.generate_complaint(
        text=payload.text,
        rules_eval=rules_eval,
        claimed_agency=payload.claimed_agency,
        user_state=payload.user_state
    )

