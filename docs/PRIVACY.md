# SarkariSach Privacy & Data Governance Policy

SarkariSach is built on a **Zero Personally Identifiable Information (Zero-PII)** architectural commitment designed to comply with the principles of the **Digital Personal Data Protection (DPDP) Act, 2023** of India.

---

## 1. Zero-Retention Guarantee

| Data Type | Processed During Check? | Stored on Server Disk/Database? |
| :--- | :---: | :---: |
| **Raw Message Text** | Yes (in ephemeral RAM) | ❌ **NEVER** |
| **Aadhaar / PAN Numbers** | Checked for credential harvesting | ❌ **NEVER** |
| **Complainant Phone Numbers** | Extracted only for complaint summary | ❌ **NEVER** |
| **Uploaded Screenshots & PDFs** | Converted to in-memory buffers | ❌ **NEVER** (discarded immediately) |
| **Voice Recordings** | Transcribed in RAM | ❌ **NEVER** |
| **User IP Addresses** | Checked by rate limiter in memory | ❌ **NEVER** logged to DB |

---

## 2. What We Store in the Public Database
To power the public threat intelligence dashboard and alert citizens to emerging fraud waves, we store strictly aggregated statistical counters:
1. `timestamp`: Date and hour of check.
2. `scam_type`: Categorical label (e.g., "Digital Arrest Scam", "TRAI SIM Deactivation").
3. `risk_bucket`: Verdict classification ("LIKELY SCAM", "SUSPICIOUS", "LOOKS GENUINE").
4. `risk_score`: Calibrated integer score (0–100).
5. `language`: Language code used for the query ("hi", "mr", "en", etc.).
6. `input_type`: Form factor ("text", "image", "audio", "url").
7. `user_state`: Complainant state if voluntarily selected (e.g., "Maharashtra").
8. `is_sample`: Boolean indicator distinguishing real telemetry from initial seed sample data.

---

## 3. Client-Side Processing & Sandboxing
- Local text highlighting and audio rendering occur directly in the citizen's browser.
- Voice recording via `MediaRecorder` prompts browser microphone permissions and releases the media stream immediately upon stopping.
- The complaint summary is generated on demand and copied to the user's local clipboard or downloaded as a `.txt` file onto the user's device without being logged.

