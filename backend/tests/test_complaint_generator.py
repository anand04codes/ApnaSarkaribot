"""
Tests for ComplaintGenerator.
Tests formatting of cybercrime.gov.in / 1930 incident reports,
entity extraction, and legal format compliance.
"""
from app.core.rules_engine import IndianScamRulesEngine
from app.services.complaint_generator import ComplaintGenerator


def test_complaint_generator_digital_arrest(rules_engine: IndianScamRulesEngine):
    text = (
        "CBI Headquarters notice: You are placed under DIGITAL ARREST. Contact Inspector Sharma on "
        "+91-9876543210 immediately. Transfer Rs 2,50,000 to rbi-security@okhdfcbank."
    )
    rules_eval = rules_engine.evaluate(text)
    complaint = ComplaintGenerator.generate_complaint(
        text=text,
        rules_eval=rules_eval,
        user_state="Maharashtra"
    )

    assert complaint.filing_portal == "https://cybercrime.gov.in"
    assert complaint.helpline == "1930"
    assert "Maharashtra" in complaint.summary_text
    assert "CBI" in (complaint.claimed_agency or "")
    assert len(complaint.suspect_numbers) >= 1
    assert len(complaint.suspect_upi_ids) >= 1
    assert "rbi-security@okhdfcbank" in complaint.suspect_upi_ids
    assert "2,50,000" in (complaint.demanded_amount or "")
    assert "PRAYER / RELIEF SOUGHT" in complaint.summary_text

