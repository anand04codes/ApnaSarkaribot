"""
Link Checker API: POST /api/check-url
Inspects suspicious domains, look-alikes, shorteners, punycode and TLD abuse.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.core.url_inspector import StaticUrlInspector
from app.models.schemas import UrlCheckResponse

router = APIRouter(tags=["URL Inspection"])
inspector = StaticUrlInspector()


class UrlPayload(BaseModel):
    url: str


@router.post("/check-url", response_model=UrlCheckResponse)
async def check_url(payload: UrlPayload):
    """
    Statically analyzes a suspicious URL without navigating to it or executing scripts.
    Identifies typosquats of government and banking portals, suspicious TLDs, and URL shorteners.
    """
    if not payload.url or not payload.url.strip():
        raise HTTPException(status_code=400, detail="URL parameter cannot be empty.")
    
    return inspector.inspect(payload.url.strip())

