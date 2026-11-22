"""
Tests for TTSService and multilingual voice output generation across Indian languages.
"""
from app.services.tts_service import TTSService, SUPPORTED_TTS_LANGUAGES


def test_supported_languages_list():
    assert "hi" in SUPPORTED_TTS_LANGUAGES
    assert "mr" in SUPPORTED_TTS_LANGUAGES
    assert "ta" in SUPPORTED_TTS_LANGUAGES
    assert "te" in SUPPORTED_TTS_LANGUAGES
    assert "bn" in SUPPORTED_TTS_LANGUAGES
    assert "gu" in SUPPORTED_TTS_LANGUAGES
    assert "kn" in SUPPORTED_TTS_LANGUAGES
    assert "en" in SUPPORTED_TTS_LANGUAGES


def test_tts_generation_hindi():
    text = "सावधान! यह एक फर्जी डिजिटल अरेस्ट कॉल है।"
    audio_bytes = TTSService.generate_speech(text, language="hi")
    assert isinstance(audio_bytes, bytes)
    assert len(audio_bytes) > 500  # valid MP3 binary stream


def test_tts_generation_english():
    text = "Warning: this is a fraudulent message impersonating law enforcement."
    audio_bytes = TTSService.generate_speech(text, language="en")
    assert isinstance(audio_bytes, bytes)
    assert len(audio_bytes) > 500


def test_tts_fallback_for_unknown_language():
    text = "Generic alert message."
    audio_bytes = TTSService.generate_speech(text, language="xx_unsupported")
    assert isinstance(audio_bytes, bytes)
    assert len(audio_bytes) > 500

