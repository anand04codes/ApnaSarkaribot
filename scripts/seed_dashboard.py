"""
Seed script: Populates realistic, clearly labeled SAMPLE statistics in the database
so the public dashboard exhibits rich trends on a clean clone.
All records are marked with is_sample=True.
"""
import sys
import random
from pathlib import Path
from datetime import datetime, timedelta

backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.models.database import SessionLocal, AnonymizedCheckLog, init_db

SCAM_TYPES = [
    ("Digital Arrest Scam", "LIKELY SCAM", 95, "Impersonation & Extortion"),
    ("FedEx / Courier Narcotics Scam", "LIKELY SCAM", 92, "Courier Contraband"),
    ("TRAI SIM Deactivation Threat", "LIKELY SCAM", 88, "Telecom Impersonation"),
    ("Electricity Bill Disconnection Scam", "LIKELY SCAM", 85, "Utility Disconnection"),
    ("SBI YONO / Bank KYC Phishing", "LIKELY SCAM", 94, "Credential Harvesting"),
    ("Fake Traffic E-Challan APK", "LIKELY SCAM", 90, "Malware Distribution"),
    ("Part-Time Telegram Job Fraud", "LIKELY SCAM", 82, "Work From Home"),
    ("KBC / Lottery Prize Fraud", "LIKELY SCAM", 80, "Lottery Fraud"),
    ("Income Tax Notice Verification", "LOOKS GENUINE", 5, "Official Communication"),
    ("SBI Bank Debit Alert", "LOOKS GENUINE", 0, "Legitimate Banking Alert"),
    ("Parivahan Genuine Challan", "LOOKS GENUINE", 2, "Official Portal"),
    ("Unsolicited Promotion SMS", "SUSPICIOUS", 45, "Unverified Marketing")
]

LANGUAGES = ["hi", "en", "mr", "ta", "te", "bn", "gu", "kn"]
INDIAN_STATES = ["Maharashtra", "Delhi", "Uttar Pradesh", "Karnataka", "Tamil Nadu", "Gujarat", "West Bengal", "Telangana", "Rajasthan"]
INPUT_TYPES = ["text", "image", "audio", "url", "pdf"]


def seed():
    init_db()
    db = SessionLocal()
    try:
        # Check if already seeded
        existing_sample_count = db.query(AnonymizedCheckLog).filter(AnonymizedCheckLog.is_sample == True).count()
        if existing_sample_count > 50:
            print(f"Database already contains {existing_sample_count} sample records. Skipping seed.")
            return

        print("Seeding database with 120 realistic anonymized sample records...")
        now = datetime.utcnow()

        for i in range(120):
            days_ago = random.randint(0, 29)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            timestamp = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

            scam_type, risk_bucket, base_score, top_cat = random.choice(SCAM_TYPES)
            score = max(0, min(100, base_score + random.randint(-5, 5)))

            log = AnonymizedCheckLog(
                timestamp=timestamp,
                scam_type=scam_type,
                risk_bucket=risk_bucket,
                risk_score=score,
                language=random.choices(LANGUAGES, weights=[40, 25, 10, 8, 7, 4, 3, 3])[0],
                input_type=random.choices(INPUT_TYPES, weights=[45, 25, 15, 10, 5])[0],
                matched_rules_count=random.randint(1, 4) if risk_bucket != "LOOKS GENUINE" else 0,
                top_rule_category=top_cat if risk_bucket != "LOOKS GENUINE" else "None",
                user_state=random.choice(INDIAN_STATES),
                is_sample=True
            )
            db.add(log)

        db.commit()
        print("Successfully seeded 120 sample records into database.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

