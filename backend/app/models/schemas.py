"""
Pydantic schemas and data contracts for SarkariSach.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RedFlag(BaseModel):
    text_span: str = Field(..., description="The exact problematic substring in the content")
    reason: str = Field(..., description="Human-readable reason why this is a red flag")
    category: str = Field("General", description="Category of threat, e.g., Impersonation, Urgency, Financial")
    severity: str = Field("HIGH", description="Severity level: HIGH, MEDIUM, LOW")
    start_char: Optional[int] = Field(None, description="Starting character index in original text")
    end_char: Optional[int] = Field(None, description="Ending character index in original text")


class RecommendedAction(BaseModel):
    step: int
    title: str
    description: str
    action_type: str = Field("SAFETY", description="SAFETY, REPORTING, VERIFICATION")
    link: Optional[str] = None


class ComplaintSummary(BaseModel):
    incident_date: str
    scam_category: str
    suspect_numbers: List[str] = []
    suspect_urls: List[str] = []
    suspect_upi_ids: List[str] = []
    claimed_agency: Optional[str] = None
    demanded_amount: Optional[str] = None
    summary_text: str
    filing_portal: str = "https://cybercrime.gov.in"
    helpline: str = "1930"


class RulesEvaluation(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Risk score from rule engine (0-100)")
    matched_rules: List[str] = []
    red_flags: List[RedFlag] = []
    scam_type: Optional[str] = None
    details: Dict[str, Any] = {}


class LLMEvaluation(BaseModel):
    risk_score: int = Field(..., ge=0, le=100)
    verdict: str
    confidence: str = Field("HIGH", description="HIGH, MEDIUM, LOW")
    scam_type: str
    plain_explanation: str
    what_it_really_means: Optional[str] = None
    red_flags: List[RedFlag] = []
    recommended_actions: List[RecommendedAction] = []


class AnalysisResponse(BaseModel):
    verdict: str = Field(..., description="LIKELY SCAM | SUSPICIOUS | LOOKS GENUINE")
    risk_score: int = Field(..., ge=0, le=100, description="Final fused risk score (0-100)")
    confidence: str = Field("HIGH", description="HIGH | MEDIUM | LOW")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    scam_type: str
    language: str = "en"
    plain_explanation: str
    what_it_really_means: Optional[str] = None
    red_flags: List[RedFlag] = []
    recommended_actions: List[RecommendedAction] = []
    complaint_summary: Optional[ComplaintSummary] = None
    extracted_text: Optional[str] = None
    input_type: str = "text"
    rules_score: int
    llm_score: Optional[int] = None
    disagreement_warning: Optional[str] = None
    media_analysis: Optional[Dict[str, Any]] = None


class UrlCheckResponse(BaseModel):
    url: str
    normalized_url: str
    domain: str
    registered_domain: str
    is_safe_domain: bool = False
    is_lookalike: bool = False
    lookalike_target: Optional[str] = None
    similarity_score: float = 0.0
    is_shortener: bool = False
    suspicious_tld: bool = False
    is_ip_address: bool = False
    has_punycode: bool = False
    has_https: bool = False
    risk_score: int = Field(..., ge=0, le=100)
    verdict: str = Field(..., description="LIKELY SCAM | SUSPICIOUS | LOOKS GENUINE")
    reasons: List[str] = []
    whois_info: Optional[Dict[str, Any]] = None


class MediaAuthenticityResponse(BaseModel):
    media_type: str
    has_manipulation_signs: bool
    confidence: str
    confidence_score: float
    ela_heatmap_base64: Optional[str] = None
    metadata: Dict[str, Any] = {}
    analysis_notes: str
    limitations_disclaimer: str = (
        "Indicative forensic analysis only, not legal proof. "
        "Compression artifacts and re-encoding can simulate editing artifacts."
    )


class TTSRequest(BaseModel):
    text: str
    language: str = "hi"  # en, hi, mr, ta, te, bn, gu, kn


class DashboardStatsResponse(BaseModel):
    total_checks: int
    scams_detected: int
    suspicious_detected: int
    genuine_detected: int
    scam_type_breakdown: List[Dict[str, Any]]
    daily_trends: List[Dict[str, Any]]
    top_red_flags: List[Dict[str, Any]]
    language_distribution: List[Dict[str, Any]]
    is_sample_data: bool = False
