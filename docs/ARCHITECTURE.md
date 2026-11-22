# SarkariSach Architecture & Forensic Pipeline

SarkariSach is engineered around a **defensive, hybrid zero-trust architecture** specifically designed to detect cyber fraud and fake government/judicial notices targeting Indian citizens.

---

## High-Level Architecture

```mermaid
flowchart TD
    User([Indian Citizen]) -->|Pasted Text, Screenshot, Audio, or URL| UI[React 18 + Vite Frontend]
    UI -->|Multipart POST /api/analyze| API[FastAPI Gateway]
    
    subgraph Detection Pipeline
        API --> Extractor[Extractor Service\npypdf, PIL, Media]
        Extractor --> CleanText[Extracted Content]
        
        CleanText --> Rules[Heuristics & Rules Engine\nRegex, RapidFuzz, Offline TLDExtract]
        CleanText --> LLM[Gemini 2.5 Flash\nStructured JSON + RAG-lite Grounding]
        
        Rules -->|Rules Score 0-100\nRed Flag Spans| Fusion[Fusion & Calibration Layer]
        LLM -->|LLM Score 0-100\nPlain Explanation| Fusion
        
        Fusion --> CalibratedVerdict[Final Calibrated Verdict\nLIKELY SCAM | SUSPICIOUS | LOOKS GENUINE]
    end

    subgraph Forensic & Voice Services
        Extractor --> ELA[Error Level Analysis\nPillow JPEG Diff Heatmap]
        CalibratedVerdict --> TTS[gTTS Voice Engine\n8 Indian Languages]
        CalibratedVerdict --> Complaint[Complaint Generator\ncybercrime.gov.in / 1930]
    end

    subgraph Data & Analytics
        Fusion -->|Zero PII Anonymized Stats| DB[(SQLite / SQLAlchemy)]
        DB --> Dashboard[Public Trending Dashboard\nRecharts]
    end
```

---

## 1. Multi-Input Ingestion & Extraction Layer
The ingestion endpoint accepts 5 distinct citizen input types:
- **Raw Text & SMS**: Pasted WhatsApp forward, SMS, or Telegram messages.
- **Document Screenshots (PNG/JPEG/WEBP)**: Official summons, forged FIRs, fake warrant letters.
- **PDF Notices**: Scanned police summons or tax notices parsed using `pypdf`.
- **Audio Voice Notes (MP3/WAV/WEBM/M4A)**: Recorded extortion calls captured directly in the browser via `MediaRecorder`.
- **Suspicious Links / URLs**: Analyzed statically through domain tokenization and typosquat matching.

---

## 2. Hybrid Detection Pipeline

### A. Rules & Heuristics Layer (Deterministic)
The rules engine operates entirely in pure Python without internet or LLM latency. It inspects:
- **Digital Arrest Triggers**: Detection of illegal video-call interrogation claims (`digital custody`, `Skype investigation`, `डिजिटल अरेस्ट`).
- **Agency Impersonation**: CBI, ED, Mumbai Police, Narcotics Control Bureau (NCB), customs departments, TRAI, and Supreme Court.
- **Extortion Ultimatums**: "Within 2 hours", "power disconnected tonight at 9:30 PM", "account frozen".
- **Credential Theft Patterns**: Demands for OTP, UPI PIN, CVV, or passwords.
- **Remote Access Apps**: Prompts to install AnyDesk, TeamViewer, QuickSupport, or RustDesk.
- **Deceptive Banking Demands**: Demands to deposit money into a "clearing account", "RBI verification escrow", or "secret penalty account".
- **Counterbalanced Genuine Rules**: Positive patterns from authentic Income Tax refund acknowledgments, bank debits with 1800 numbers, and official `.gov.in` URLs that negate false alarms.

### B. LLM Layer (Gemini 2.5 Flash via `google-genai`)
Grounded with Indian legal realities (RAG-lite):
- Strictly adheres to structured Pydantic schemas.
- Injects authoritative facts (e.g. *Digital Arrest does not exist under Indian law*; *No bank requires UPI PIN to receive money*).
- Outputs empathetic, natural spoken explanations in the user's selected regional Indian language.

### C. Fusion & Calibration Layer
Combines deterministic rules score and probabilistic LLM score:
- **Consensus**: When both agree, high confidence (0.90+) is awarded.
- **Divergence**: If the scores deviate by more than 35 points, confidence is lowered to `LOW`, and an explicit warning informs the user to apply extra human vigilance.

---

## 3. Forensic Media Authenticity
- **Error Level Analysis (ELA)**: Resaves image at 90% JPEG quality, computes pixel-wise absolute difference with the original, and enhances contrast 15x–20x. High localized compression artifacts indicate text splicing, forged rubber stamps, or pasted emblems.
- **EXIF Analysis**: Flags editing software signatures (Photoshop, GIMP, Canva, PicsArt).
- **Ethical Safeguard**: All media reports carry an explicit disclaimer noting that compression artifacts can simulate tampering, avoiding false legal certainty.

