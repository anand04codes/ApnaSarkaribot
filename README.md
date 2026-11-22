# 🛡️ SarkariSach (सरकारी सच)
### *AI-Powered "Is This Real?" Cyber Defense & Official Notice Verification Engine for Indian Citizens*

[![Built for IDEA//FORGE Hackathon – Track 1: Civic Pulse](https://img.shields.io/badge/IDEA%2F%2FFORGE%20Hackathon-Track%201%3A%20Civic%20Pulse-blueviolet?style=for-the-badge)](https://github.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg?style=for-the-badge)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%20%7C%203.13-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React 18 + Vite](https://img.shields.io/badge/React-18-61DAFB.svg?style=for-the-badge&logo=react)](https://react.dev/)
[![Tests Passing](https://img.shields.io/badge/Tests-48%20Passed-success?style=for-the-badge)](https://pytest.org)

---

## 🇮🇳 Problem Statement & Real-World Context

Over the past two years, cyber criminals targeting Indian citizens have transitioned from crude lottery SMS messages to **psychologically coercive, state-impersonation syndicates**. According to the Ministry of Home Affairs (MHA) and the Indian Cyber Crime Coordination Centre (I4C):
1. **"Digital Arrest" Extortion**: Scammers masquerading as the Central Bureau of Investigation (CBI), Enforcement Directorate (ED), Narcotics Control Bureau (NCB), or Mumbai Police contact victims over Skype or WhatsApp video calls, alleging that a courier parcel containing narcotics (MDMA) or forged passports was seized in their name. Victims are coerced into transferring lifetime savings to "clearing security accounts".
2. **TRAI / Telecom Disconnection Ultimatums**: Automated IVR calls claiming mobile numbers will be terminated within 2 hours.
3. **Utility & Electricity Bill Phishing**: Malicious SMS claiming power cuts tonight at 9:30 PM with unverified mobile numbers.
4. **Forged Judicial Summons & Malicious APKs**: Fraudulent traffic fines and PM subsidies distributed as Android APK malware.

**SarkariSach** solves this crisis by giving every Indian citizen an accessible, instant verification assistant capable of distinguishing authentic official communications from criminal intimidation.

---

## 📸 Demo Preview

```
+-----------------------------------------------------------------------------------------+
|  🛡️ SarkariSach | Citizen Cyber Defense               [📞 Helpline: 1930] [🌐 हिन्दी ▼]  |
|-----------------------------------------------------------------------------------------|
|  [Check Notice]    [Link Checker]    [Image Forensics]    [Trending Scams]    [Privacy] |
|                                                                                         |
|  🚨 VERDICT: LIKELY SCAM  (Risk Score: 100/100 | Confidence: HIGH 94%)                   |
|  Category: Digital Arrest Scam                                     [🔊 Listen in Hindi] |
|  -------------------------------------------------------------------------------------  |
|  "सीबीआई नोटिस: आपको डिजिटल अरेस्ट में रखा गया है... सुरक्षा राशि तुरंत ट्रांसफर करें।" |
|                                                                                         |
|  🚩 Identified Red Flags:                                                               |
|  • "डिजिटल अरेस्ट": The concept of Digital Arrest does NOT exist under Indian law.      |
|  • "सुरक्षा राशि ट्रांसफर": No Indian agency requires money to clear legal charges.     |
|                                                                                         |
|  🛡️ Immediate Action Steps:                                                             |
|  [✓] 1. Do Not Pay: Refuse any verification deposit or transfer.                        |
|  [✓] 2. Block and Report: Mark the caller as spam on WhatsApp.                          |
|  [✓] 3. Dial 1930 / cybercrime.gov.in: Generate ready-to-paste complaint.               |
|                                                                                         |
|  [📋 Generate Official Complaint (1930 / Portal)]                                       |
+-----------------------------------------------------------------------------------------+
```

---

## ✨ Features (All Tested & Functional)

1. **Multi-Input Verification (`POST /api/analyze`)**
   - Supports raw text, document screenshots (PNG/JPEG/WEBP), PDF notices, audio voice notes (MP3/WAV/WEBM/M4A), and links.
   - Enforces 10 MB file bounds and strict MIME validation.

2. **Hybrid Detection Pipeline (Rules + Gemini LLM + Fusion)**
   - **Deterministic Rules Engine**: Pure Python regex heuristics and rapidfuzz matching against verified Indian knowledge bases.
   - **Gemini 2.5 Flash Layer**: Structured JSON evaluation grounded in Indian legal realities (RAG-lite).
   - **Fusion & Calibration**: Merges rules score and LLM score; flags significant divergence and penalizes certainty.

3. **Multilingual Spoken Output across 8 Indian Languages**
   - English, Hindi (हिन्दी), Marathi (मराठी), Tamil (தமிழ்), Telugu (తెలుగు), Bengali (বাংলা), Gujarati (ગુજરાતી), and Kannada (ಕನ್ನಡ).
   - Real-time audio speech generation via `gTTS` streamed through the frontend player.

4. **Highlighted Evidence View**
   - Renders original text with interactive red-flag highlights and detailed tooltips for each forensic trigger.

5. **Action Guide & 1930 Complaint Generator**
   - Generates formal incident narratives formatted according to **National Cyber Crime Reporting Portal (`cybercrime.gov.in`)** and Helpline 1930 standards with one-click clipboard copying and `.txt` download.

6. **Static Safe URL Inspector (`POST /api/check-url`)**
   - Identifies typosquats of `incometax.gov.in`, `sbi.co.in`, `parivahan.gov.in`, URL shorteners, punycode, and suspicious TLDs without navigating to the page.

7. **Media Authenticity & Tampering Check (`POST /api/check-media`)**
   - Generates visual **Error Level Analysis (ELA)** heatmaps and extracts EXIF metadata to flag forged seals and altered text, with an ethical limitations disclaimer.

8. **Public Anonymized Threat Dashboard (`/dashboard`)**
   - Aggregated 30-day activity trendlines, top scam categories, language distribution, and attack vectors (Recharts).
   - Includes clearly marked sample telemetry for clean clone deployments.

9. **Telegram Citizen Bot (`bot/telegram_bot.py`)**
   - Forwards text, photos, and voice notes directly to the verification engine and responds with verdicts and spoken voice notes.

---

## 🏛️ Architecture

```mermaid
flowchart TD
    User([Citizen Input\nText, Image, PDF, Voice, URL]) --> UI[React 18 + Vite Frontend]
    UI --> API[FastAPI Gateway]
    
    subgraph Detection Pipeline
        API --> Extractor[Extractor Service\npypdf, PIL, Media]
        Extractor --> Rules[Heuristic Rules Engine\nRegex, RapidFuzz, Offline TLDExtract]
        Extractor --> LLM[Gemini 2.5 Flash\nStructured JSON + RAG Grounding]
        
        Rules -->|Rules Score 0-100| Fusion[Fusion & Calibration Layer]
        LLM -->|LLM Score 0-100| Fusion
        Fusion --> CalibratedVerdict[Final Calibrated Verdict\nLIKELY SCAM | SUSPICIOUS | LOOKS GENUINE]
    end

    subgraph Forensic & Reporting Services
        Extractor --> ELA[Error Level Analysis\nPillow JPEG Diff Heatmap]
        CalibratedVerdict --> TTS[gTTS Voice Synthesis\n8 Indian Languages]
        CalibratedVerdict --> Complaint[Complaint Generator\ncybercrime.gov.in / 1930]
    end

    subgraph Analytics
        Fusion -->|Zero-PII Metadata| DB[(SQLite / SQLAlchemy)]
        DB --> Dashboard[Public Trending Dashboard\nRecharts]
    end
```

---

## ⚡ Quickstart in Under 5 Commands

### Option A: Local Development

```bash
# 1. Clone repository & enter workspace
git clone https://github.com/your-username/SarkariSach.git
cd SarkariSach

# 2. Set up Python virtual environment & install dependencies
python -m venv venv
.\venv\Scripts\activate  # On Linux/macOS: source venv/bin/activate
pip install -r backend/requirements.txt

# 3. Seed sample dashboard telemetry
python scripts/seed_dashboard.py

# 4. Start FastAPI backend (port 8000)
uvicorn app.main:app --app-dir backend --reload --port 8000

# 5. In a separate terminal: Start Vite frontend (port 5173)
cd frontend
npm install
npm run dev
```

Open **`http://localhost:5173`** in your browser.

---

### Option B: Docker Deployment (Single Command)

```bash
docker compose up --build -d
```

Access the unified application at **`http://localhost:8000`**.

### Option C: Public Render Deployment

1. Push this repository to GitHub and connect it to Render using **New → Blueprint**.
2. Apply the Blueprint. The free `sarkarisach` web service serves the website and runs the Telegram bot when `TELEGRAM_BOT_TOKEN` is configured.
3. Add `TELEGRAM_BOT_TOKEN` and, optionally, `GEMINI_API_KEY` in the service's Render environment settings. Never commit API keys or bot tokens.
4. After the service deploys, share its public `https://*.onrender.com` URL and the bot's Telegram link. On Render's free plan, the service can spin down when idle, so the website's first request may take about a minute and the bot will be unavailable while it sleeps. An always-on bot requires paid hosting.

The default SQLite database is ephemeral on Render: dashboard records can be lost when the web service restarts or redeploys. The app stores only anonymized analysis metadata, not submitted messages or files. For persistent production storage, configure an external database.

---

## 🧪 Evaluation Results & Benchmark Matrix

SarkariSach was evaluated across **25 realistic Indian cyber scam and authentic official alerts** compiled in `backend/tests/samples/` using `python scripts/evaluate.py`:

```
================================================================================
 CONFUSION MATRIX & PERFORMANCE METRICS
================================================================================
 Total Samples Tested   : 25
 True Positives  (TP)   : 16 (Scams correctly flagged)
 True Negatives  (TN)   :  9 (Genuine correctly verified)
 False Positives (FP)   :  0 (False alarms on genuine)
 False Negatives (FN)   :  0 (Missed scams)
----------------------------------------
 CONFUSION MATRIX:
                  Predicted Scam    Predicted Genuine
 Actual Scam           16                 0
 Actual Genuine         0                 9
----------------------------------------
 ACCURACY   : 100.00%
 PRECISION  : 100.00%
 RECALL     : 100.00%
 F1-SCORE   : 100.00%
================================================================================
```

Run the benchmark anytime:
```bash
python scripts/evaluate.py
```

Run the unit and integration test suite:
```bash
pytest backend/tests -v
# Output: 48 passed in 13.94s
```

---

## 🔐 Environment Variables

| Variable | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `GEMINI_API_KEY` | Optional | `""` | Google Gemini API key (App falls back gracefully to offline rules engine if omitted). |
| `GEMINI_MODEL` | Optional | `gemini-2.5-flash` | Gemini model variant. |
| `DATABASE_URL` | Optional | `sqlite:///./sarkarisach.db` | SQLAlchemy database connection string. |
| `TELEGRAM_BOT_TOKEN` | Optional | `""` | Telegram bot token from @BotFather. |
| `RATE_LIMIT_PER_MINUTE`| Optional | `30/minute` | Rate limiting for API defense. |

---

## 📖 API Reference & Examples

### Analyze Suspicious Message
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "text=CBI NOTICE: You are under DIGITAL ARREST. Contact Inspector Sharma on 9876543210. Transfer Rs 2,50,000 security deposit." \
  -F "language=hi"
```

### Inspect URL for Typosquatting
```bash
curl -X POST "http://localhost:8000/api/check-url" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://incometax-gov.in/verify"}'
```

### Synthesize Regional Speech
```bash
curl -X POST "http://localhost:8000/api/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "सावधान! यह एक फर्जी डिजिटल अरेस्ट कॉल है।", "language": "hi"}' \
  --output verdict.mp3
```

---

## 🛡️ Ethics, Limitations & Privacy

- **Guidance, Not Legal Counsel**: Outputs provide immediate citizen triage based on forensic heuristics. Official legal complaints must be submitted to law enforcement via `cybercrime.gov.in` or `1930`.
- **Zero-PII Storage**: No personal names, raw WhatsApp transcripts, phone numbers, or uploaded media are persisted on disk or databases.
- **Forensic Disclaimer**: Error Level Analysis (ELA) and audio forensics are indicative tools, not conclusive judicial proof.

---

## 🗺️ Roadmap
- [x] Multi-input analysis (text, image, PDF, audio, link)
- [x] Multilingual voice output (8 Indian languages)
- [x] ELA image forensics & lookalike link inspector
- [x] Cybercrime 1930 complaint generator
- [x] Public trending dashboard with sample data seeding
- [x] Full Telegram bot integration
- [ ] On-device lightweight OCR fine-tuned for regional Indian state police seals
- [ ] Direct API integration with DoT Chakshu reporting portal

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
Built for **IDEA//FORGE Hackathon – Track 1: Civic Pulse**.
