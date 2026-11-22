"""
SQLAlchemy database setup and anonymized audit models.
Stores strictly NO PII, no raw messages, no uploaded files, no phone numbers.
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class AnonymizedCheckLog(Base):
    """
    Anonymized metadata for public dashboard analytics.
    Zero personal identifiable information (PII) is stored.
    """
    __tablename__ = "anonymized_check_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    scam_type = Column(String(100), index=True)
    risk_bucket = Column(String(50), index=True)  # LIKELY SCAM | SUSPICIOUS | LOOKS GENUINE
    risk_score = Column(Integer)
    language = Column(String(10), default="en")
    input_type = Column(String(20), default="text")
    matched_rules_count = Column(Integer, default=0)
    top_rule_category = Column(String(100), nullable=True)
    user_state = Column(String(100), nullable=True)
    is_sample = Column(Boolean, default=False, index=True)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
