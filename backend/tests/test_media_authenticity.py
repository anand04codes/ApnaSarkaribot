"""
Tests for MediaAuthenticityInspector.
Tests image Error Level Analysis (ELA) heatmap generation, EXIF inspection,
and audio forensic indicators with disclaimers.
"""
import io
from PIL import Image
from app.core.media_authenticity import MediaAuthenticityInspector


def test_image_ela_heatmap_generation():
    # Create an in-memory test image
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=95)
    img_bytes = buffer.getvalue()

    res = MediaAuthenticityInspector.inspect_image(img_bytes)
    assert res.media_type == "image"
    assert res.ela_heatmap_base64 is not None
    assert res.ela_heatmap_base64.startswith("data:image/png;base64,")
    assert "limitations_disclaimer" in res.model_dump()
    assert "not legal proof" in res.limitations_disclaimer


def test_corrupted_image_handling():
    corrupted_bytes = b"NOT_AN_IMAGE_DATA_12345"
    res = MediaAuthenticityInspector.inspect_image(corrupted_bytes)
    assert res.confidence == "LOW"
    assert "Could not parse" in res.analysis_notes


def test_audio_metadata_inspection():
    fake_audio = b"ID3\x03\x00\x00\x00\x00\x00\x00" + b"\x00" * 2000
    res = MediaAuthenticityInspector.inspect_audio(fake_audio, "threat_call.mp3")
    assert res.media_type == "audio"
    assert res.metadata["filename"] == "threat_call.mp3"
    assert "Indicative" in res.limitations_disclaimer or "indicative" in res.analysis_notes

