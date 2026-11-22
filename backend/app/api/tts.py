"""
Text to Speech API: POST /api/tts
Synthesizes verdict and action steps into spoken audio across 8 Indian languages.
"""
from fastapi import APIRouter, HTTPException, Response
from app.services.tts_service import TTSService, SUPPORTED_TTS_LANGUAGES
from app.models.schemas import TTSRequest

router = APIRouter(tags=["Text to Speech"])


@router.post("/tts")
async def text_to_speech(payload: TTSRequest):
    """
    Generates an MP3 audio file from the provided explanation text
    in the requested Indian language (en, hi, mr, ta, te, bn, gu, kn).
    """
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text parameter cannot be empty.")

    lang = payload.language.lower()
    if lang not in SUPPORTED_TTS_LANGUAGES:
        lang = "en"

    mp3_bytes = TTSService.generate_speech(payload.text, language=lang)

    return Response(
        content=mp3_bytes,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f'inline; filename="sarkarisach_{lang}.mp3"'
        }
    )

