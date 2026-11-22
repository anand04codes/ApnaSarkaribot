# SarkariSach API Documentation & Curl Reference

The SarkariSach backend is a high-performance REST API built with FastAPI and Pydantic v2.

**Base URL**: `http://localhost:8000/api`

---

## 1. Multi-Input Analysis: `POST /api/analyze`

Accepts text, image files, PDF documents, audio recordings, or URLs.

### Request (Multipart Form)
- `text` (optional string): Text content to inspect.
- `url` (optional string): Suspicious URL.
- `file` (optional binary): File upload (PNG, JPG, PDF, MP3, WAV, WEBM). Max 10 MB.
- `language` (optional string, default `"en"`): Target language code (`en`, `hi`, `mr`, `ta`, `te`, `bn`, `gu`, `kn`).
- `user_state` (optional string): State of the complainant for jurisdiction.

### Example Curl Request
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "text=CRIME BRANCH: You are under DIGITAL ARREST. Contact Inspector Sharma on +91-9876543210. Pay Rs 2,50,000 security deposit." \
  -F "language=hi" \
  -F "user_state=Delhi"
```

### Example Response
```json
{
  "verdict": "LIKELY SCAM",
  "risk_score": 100,
  "confidence": "HIGH",
  "confidence_score": 0.94,
  "scam_type": "Digital Arrest Scam",
  "language": "hi",
  "plain_explanation": "सावधान: यह 100% एक फर्जी 'डिजिटल अरेस्ट' कॉल है। भारतीय कानून में डिजिटल अरेस्ट नाम की कोई व्यवस्था नहीं है।",
  "what_it_really_means": null,
  "red_flags": [
    {
      "text_span": "DIGITAL ARREST",
      "reason": "The concept of 'Digital Arrest' does NOT exist under Indian law.",
      "category": "Impersonation & Extortion",
      "severity": "HIGH",
      "start_char": 27,
      "end_char": 41
    }
  ],
  "recommended_actions": [
    {
      "step": 1,
      "title": "Do Not Pay or Transfer Any Money",
      "description": "Immediately refuse any payment. No Indian agency requires money to clear charges.",
      "action_type": "SAFETY"
    }
  ],
  "complaint_summary": {
    "incident_date": "2026-11-21 20:30 IST",
    "scam_category": "Digital Arrest Scam",
    "suspect_numbers": ["9876543210"],
    "claimed_agency": "Crime Branch",
    "demanded_amount": "Rs 2,50,000",
    "filing_portal": "https://cybercrime.gov.in",
    "helpline": "1930"
  }
}
```

---

## 2. Static URL Inspector: `POST /api/check-url`

Statically analyzes suspicious links, look-alike typo-squats, shorteners, and punycode.

### Example Curl Request
```bash
curl -X POST "http://localhost:8000/api/check-url" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://incometax-gov.in/portal/login"}'
```

### Example Response
```json
{
  "url": "http://incometax-gov.in/portal/login",
  "domain": "incometax-gov.in",
  "registered_domain": "incometax-gov.in",
  "is_safe_domain": false,
  "is_lookalike": true,
  "lookalike_target": "incometax.gov.in",
  "similarity_score": 0.94,
  "is_shortener": false,
  "suspicious_tld": false,
  "is_ip_address": false,
  "has_punycode": false,
  "has_https": false,
  "risk_score": 75,
  "verdict": "LIKELY SCAM",
  "reasons": [
    "Domain 'incometax-gov.in' is a look-alike spoof of official 'incometax.gov.in' (94% similarity).",
    "Connection is not secured with HTTPS (unencrypted HTTP protocol)."
  ]
}
```

---

## 3. Multilingual Text-to-Speech: `POST /api/tts`

Generates spoken audio in any of the 8 supported Indian languages.

### Example Curl Request
```bash
curl -X POST "http://localhost:8000/api/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "सावधान! यह एक फर्जी डिजिटल अरेस्ट कॉल है।", "language": "hi"}' \
  --output verdict_hindi.mp3
```

---

## 4. Public Threat Trends: `GET /api/dashboard/stats`

Returns aggregated statistics for citizen awareness.

### Example Curl Request
```bash
curl -X GET "http://localhost:8000/api/dashboard/stats"
```

