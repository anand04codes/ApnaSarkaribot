"""
Multilingual Text-to-Speech (TTS) Service using gTTS.
Supports Indian languages: English, Hindi, Marathi, Tamil, Telugu, Bengali, Gujarati, Kannada.
Generates MP3 audio streams for browser playback.
"""
import io
import logging
from typing import Optional
from gtts import gTTS

logger = logging.getLogger(__name__)

# gTTS supported language codes for India
SUPPORTED_TTS_LANGUAGES = {
    "en": {"name": "English", "tld": "co.in"},
    "hi": {"name": "Hindi", "tld": "co.in"},
    "mr": {"name": "Marathi", "tld": "co.in"},
    "ta": {"name": "Tamil", "tld": "co.in"},
    "te": {"name": "Telugu", "tld": "co.in"},
    "bn": {"name": "Bengali", "tld": "co.in"},
    "gu": {"name": "Gujarati", "tld": "co.in"},
    "kn": {"name": "Kannada", "tld": "co.in"}
}


class TTSService:
    @staticmethod
    def generate_speech(text: str, language: str = "hi") -> bytes:
        """
        Synthesize spoken audio from text using gTTS.
        Returns MP3 bytes.
        """
        lang = language.lower()
        if lang not in SUPPORTED_TTS_LANGUAGES:
            lang = "hi" if any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in text) else "en"

        tld = SUPPORTED_TTS_LANGUAGES.get(lang, {}).get("tld", "co.in")

        # Sanitize text for TTS (limit length to prevent memory overload)
        clean_text = text.strip()[:1000]
        if not clean_text:
            clean_text = "चेतावनी: कोई संदेश नहीं मिला।" if lang == "hi" else "Warning: No text provided."

        try:
            tts = gTTS(text=clean_text, lang=lang, tld=tld, slow=False, timeout=2.0)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp.read()
        except Exception as e:
            logger.warning(f"gTTS online speech synthesis unreachable/timed out: {e}. Generating offline synthetic audio frame.")
            # Standard MP3 silent frame so audio players can load without error
            # MPEG-1 Audio Layer III frame header (sync word 0xFFFB)
            mp3_frame = b"\xff\xfb\x90\x64" + b"\x00" * 414
            return mp3_frame * 10
