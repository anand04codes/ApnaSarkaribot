"""
Integration and Unit Tests for SarkariSach FastAPI Endpoints.
Covers health, analysis, check-url, check-media, tts, complaint, dashboard,
file validation, and error boundaries.
"""
import io
from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "SarkariSach" in data["service"]


def test_check_url_endpoint(client: TestClient):
    payload = {"url": "http://incometax-gov.in/verify"}
    response = client.post("/api/check-url", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_lookalike"] is True
    assert data["verdict"] == "LIKELY SCAM"


def test_check_url_empty_validation(client: TestClient):
    response = client.post("/api/check-url", json={"url": "  "})
    assert response.status_code == 400


def test_generate_complaint_endpoint(client: TestClient):
    payload = {
        "text": "Cyber branch notice: Under DIGITAL ARREST. Contact 9876543210. Pay Rs 50,000.",
        "claimed_agency": "Cyber Crime Branch",
        "user_state": "Delhi"
    }
    response = client.post("/api/generate-complaint", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["helpline"] == "1930"
    assert "Delhi" in data["summary_text"]
    assert "9876543210" in data["suspect_numbers"]


def test_tts_endpoint(client: TestClient):
    payload = {"text": "यह एक साइबर धोखाधड़ी की चेतावनी है।", "language": "hi"}
    response = client.post("/api/tts", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert len(response.content) > 500


def test_dashboard_stats_endpoint(client: TestClient):
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_checks" in data
    assert "scam_type_breakdown" in data
    assert "daily_trends" in data
    assert "language_distribution" in data


def test_analyze_endpoint_text(client: TestClient):
    response = client.post(
        "/api/analyze",
        data={
            "text": "CRIME INVESTIGATION DEPT: You are placed under DIGITAL ARREST. Stay on Skype call. Transfer Rs 2,50,000.",
            "language": "en"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "LIKELY SCAM"
    assert data["risk_score"] >= 65
    assert data["complaint_summary"] is not None
    assert len(data["red_flags"]) >= 1


def test_analyze_endpoint_empty_error(client: TestClient):
    response = client.post("/api/analyze", data={})
    assert response.status_code == 400
    assert "No input provided" in response.json()["detail"]


def test_analyze_endpoint_bad_file_type(client: TestClient):
    bad_file = io.BytesIO(b"echo 'malicious script'")
    response = client.post(
        "/api/analyze",
        files={"file": ("exploit.exe", bad_file, "application/x-msdownload")}
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_analyze_endpoint_oversized_file(client: TestClient):
    # Simulate oversized file (>10MB)
    huge_file = io.BytesIO(b"A" * (11 * 1024 * 1024))
    response = client.post(
        "/api/analyze",
        files={"file": ("large_image.png", huge_file, "image/png")}
    )
    assert response.status_code == 400
    assert "exceeds maximum allowed limit" in response.json()["detail"]

