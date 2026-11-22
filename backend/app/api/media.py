"""
Media Authenticity API: POST /api/check-media
Forensic Error Level Analysis (ELA) for images and audio integrity inspection.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.media_authenticity import MediaAuthenticityInspector
from app.services.extractor_service import ExtractorService
from app.models.schemas import MediaAuthenticityResponse

router = APIRouter(tags=["Media Authenticity"])


@router.post("/check-media", response_model=MediaAuthenticityResponse)
async def check_media(file: UploadFile = File(...)):
    """
    Forensic analysis of uploaded media:
    - Image: Error Level Analysis (ELA) + EXIF metadata extraction
    - Audio: Acoustic stream verification with ethical limitation disclosure
    """
    contents = await file.read()
    file_size = len(contents)

    try:
        category, mime = ExtractorService.validate_file(file.filename, file.content_type, file_size)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if category == "image":
        return MediaAuthenticityInspector.inspect_image(contents)
    elif category == "audio":
        return MediaAuthenticityInspector.inspect_audio(contents, file.filename)
    else:
        raise HTTPException(
            status_code=400, 
            detail="Media authenticity check is supported for images (PNG, JPG) and audio files."
        )

