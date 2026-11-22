"""
Multi-Input Analysis API: POST /api/analyze
Core pipeline accepting Text, Image, PDF, Audio, or URL.
Extracts content, runs Rules Engine + Gemini LLM + Fusion calibration,
generates actionable complaint summary and logs strictly anonymized statistics.
"""
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.rules_engine import IndianScamRulesEngine
from app.core.fusion import FusionEngine
from app.core.media_authenticity import MediaAuthenticityInspector
from app.core.url_inspector import StaticUrlInspector
from app.services.gemini_service import GeminiService
from app.services.extractor_service import ExtractorService
from app.services.complaint_generator import ComplaintGenerator
from app.models.database import get_db, AnonymizedCheckLog
from app.models.schemas import AnalysisResponse

router = APIRouter(tags=["Analysis Engine"])

rules_engine = IndianScamRulesEngine()
gemini_service = GeminiService()
url_inspector = StaticUrlInspector()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(
    text: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    language: str = Form("en"),
    user_state: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Main verification pipeline for suspicious messages, notices, warrants, audio, or files.
    """
    input_type = "text"
    extracted_text = ""
    media_analysis = None
    image_bytes = None
    image_mime = None
    audio_bytes = None
    audio_mime = None

    # 1. Handle File Upload (Image, PDF, Audio)
    if file:
        file_bytes = await file.read()
        file_size = len(file_bytes)
        try:
            category, mime = ExtractorService.validate_file(file.filename, file.content_type, file_size)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        input_type = category

        if category == "image":
            image_bytes = file_bytes
            image_mime = mime
            # Error Level Analysis & EXIF inspection
            media_resp = MediaAuthenticityInspector.inspect_image(file_bytes)
            media_analysis = media_resp.model_dump()
            # If user also provided text caption, use it; otherwise OCR will happen in Gemini
            extracted_text = text.strip() if text else "[Image Notice / Screenshot Document]"

        elif category == "pdf":
            extracted_text = ExtractorService.extract_text_from_pdf(file_bytes)
            if not extracted_text:
                extracted_text = "[Scanned PDF - Visual Analysis Required]"
            if text:
                extracted_text = f"{text}\n\n{extracted_text}"

        elif category == "audio":
            audio_bytes = file_bytes
            audio_mime = mime
            media_resp = MediaAuthenticityInspector.inspect_audio(file_bytes, file.filename)
            media_analysis = media_resp.model_dump()
            extracted_text = text.strip() if text else "[Voice Recording / Audio Notice]"

    elif url:
        input_type = "url"
        url_resp = url_inspector.inspect(url)
        extracted_text = (
            f"Suspicious URL: {url}\n"
            f"Domain: {url_resp.domain}\n"
            f"Risk Score: {url_resp.risk_score}\n"
            f"Reasons: {', '.join(url_resp.reasons)}"
        )
        if text:
            extracted_text = f"{text}\n\n{extracted_text}"

    elif text:
        input_type = "text"
        extracted_text = text.strip()

    else:
        raise HTTPException(
            status_code=400, 
            detail="No input provided. Please submit text, a URL, or upload a document/screenshot/audio file."
        )

    # 2. Rules Engine Layer (Deterministic Heuristics)
    rules_eval = rules_engine.evaluate(extracted_text)

    # 3. LLM Layer (Gemini Multimodal / RAG-lite)
    llm_eval = await gemini_service.analyze_content(
        text=extracted_text,
        image_bytes=image_bytes,
        image_mime=image_mime,
        audio_bytes=audio_bytes,
        audio_mime=audio_mime,
        language=language
    )

    # 4. Fusion Layer (Calibrated Hybrid Verdict)
    analysis = FusionEngine.fuse(
        rules_eval=rules_eval,
        llm_eval=llm_eval,
        language=language,
        input_type=input_type,
        extracted_text=extracted_text,
        media_analysis=media_analysis
    )

    # 5. Generate Complaint Summary if deemed a Scam or Suspicious
    if analysis.verdict != "LOOKS GENUINE":
        analysis.complaint_summary = ComplaintGenerator.generate_complaint(
            text=extracted_text,
            rules_eval=rules_eval,
            fused_verdict=analysis.verdict,
            user_state=user_state
        )

    # 6. Log Anonymized Metadata to Database (Zero PII!)
    try:
        top_rule = rules_eval.red_flags[0].category if rules_eval.red_flags else None
        log_entry = AnonymizedCheckLog(
            scam_type=analysis.scam_type,
            risk_bucket=analysis.verdict,
            risk_score=analysis.risk_score,
            language=language,
            input_type=input_type,
            matched_rules_count=len(rules_eval.matched_rules),
            top_rule_category=top_rule,
            user_state=user_state,
            is_sample=False
        )
        db.add(log_entry)
        db.commit()
    except Exception:
        db.rollback()

    return analysis

