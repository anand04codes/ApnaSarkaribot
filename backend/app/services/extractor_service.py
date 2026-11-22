"""
Extractor Service: Handles file validation, PDF parsing, Image preprocessing, and Audio conversion.
Validates file types, enforces 10MB size limit, rejects bad inputs with clear errors.
"""
import io
from typing import Tuple, Optional
from pypdf import PdfReader
from PIL import Image

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
ALLOWED_PDF_TYPES = {"application/pdf"}
ALLOWED_AUDIO_TYPES = {
    "audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav", 
    "audio/webm", "audio/m4a", "audio/x-m4a", "audio/ogg", "audio/aac"
}
MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB


class ExtractorService:
    @staticmethod
    def validate_file(filename: str, content_type: str, file_size: int) -> Tuple[str, str]:
        """
        Validates uploaded file size and content type.
        Returns (detected_category, normalized_mime_type).
        """
        if file_size > MAX_FILE_BYTES:
            raise ValueError(f"File size ({file_size / (1024*1024):.2f} MB) exceeds maximum allowed limit of 10 MB.")

        ct = content_type.lower()
        if ct in ALLOWED_IMAGE_TYPES or filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            return "image", ct
        if ct in ALLOWED_PDF_TYPES or filename.lower().endswith(".pdf"):
            return "pdf", ct
        if ct in ALLOWED_AUDIO_TYPES or filename.lower().endswith((".mp3", ".wav", ".webm", ".m4a", ".ogg", ".aac")):
            return "audio", ct

        raise ValueError(
            f"Unsupported file type '{content_type}'. Allowed types: Images (PNG, JPG, WEBP), PDFs, and Audio (MP3, WAV, WEBM, M4A)."
        )

    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        """Extract text from PDF pages using pypdf."""
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            text_parts = []
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text.strip())
            return "\n\n".join(text_parts).strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF document: {str(e)}")

    @staticmethod
    def inspect_image_dimensions(image_bytes: bytes) -> Tuple[int, int, str]:
        """Inspect image format and dimensions."""
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                return img.width, img.height, img.format or "JPEG"
        except Exception as e:
            raise ValueError(f"Corrupted or invalid image file: {str(e)}")

