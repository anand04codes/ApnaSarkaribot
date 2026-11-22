"""
Tests for IndianScamRulesEngine.
Tests detection of digital arrest, police impersonation, urgency, credentials,
fake schemes, lottery, genuine notices, and entity extraction.
"""
import pytest
from app.core.rules_engine import IndianScamRulesEngine


def test_empty_input(rules_engine: IndianScamRulesEngine):
    res = rules_engine.evaluate("")
    assert res.score == 0
    assert len(res.red_flags) == 0


def test_digital_arrest_detection(rules_engine: IndianScamRulesEngine):
    text = "You are placed under DIGITAL ARREST. Stay on Skype video call camera immediately."
    res = rules_engine.evaluate(text)
    assert res.score >= 65
    assert "RULE_DIGITAL_ARREST" in res.matched_rules
    assert any("Digital Arrest" in rf.reason for rf in res.red_flags)


def test_hindi_digital_arrest_detection(rules_engine: IndianScamRulesEngine):
    text = "सीबीआई नोटिस: आपको डिजिटल अरेस्ट में रखा गया है। तुरंत स्काइप वीडियो कॉल पर पेश हों।"
    res = rules_engine.evaluate(text)
    assert res.score >= 65
    assert "RULE_DIGITAL_ARREST" in res.matched_rules


def test_law_enforcement_and_narcotics_threat(rules_engine: IndianScamRulesEngine):
    text = "FedEx Customs Mumbai: Your parcel containing MDMA drugs has been seized by Narcotics Control Bureau (NCB)."
    res = rules_engine.evaluate(text)
    assert res.score >= 70
    assert "RULE_PARCEL_DRUGS_SEIZURE" in res.matched_rules


def test_trai_sim_deactivation(rules_engine: IndianScamRulesEngine):
    text = "TRAI notice: Your mobile number will be terminated within 2 hours. Press 9 to contact verification desk."
    res = rules_engine.evaluate(text)
    assert res.score >= 65
    assert "RULE_TRAI_DISCONNECTION" in res.matched_rules


def test_electricity_bill_scam(rules_engine: IndianScamRulesEngine):
    text = "Dear consumer your electricity power will be disconnected tonight at 9:30 PM. Call electricity officer."
    res = rules_engine.evaluate(text)
    assert res.score >= 65
    assert "RULE_FAKE_UTILITY_OR_SCHEME" in res.matched_rules


def test_credential_harvesting_otp_pin(rules_engine: IndianScamRulesEngine):
    text = "Dear customer, submit Aadhaar and enter your UPI PIN to claim prize."
    res = rules_engine.evaluate(text)
    assert res.score >= 50
    assert "RULE_CREDENTIAL_HARVESTING" in res.matched_rules


def test_remote_access_anydesk_installation(rules_engine: IndianScamRulesEngine):
    text = "To resolve banking issue, please download and install AnyDesk remote app."
    res = rules_engine.evaluate(text)
    assert res.score >= 50
    assert any("REMOTE_APP" in r for r in res.matched_rules)


def test_rbi_clearance_account_demand(rules_engine: IndianScamRulesEngine):
    text = "Deposit Rs 50,000 in clearing security account to cancel arrest warrant."
    res = rules_engine.evaluate(text)
    assert res.score >= 60
    assert "RULE_DEMAND_CLEARANCE_TRANSFER" in res.matched_rules


def test_lottery_kbc_scam(rules_engine: IndianScamRulesEngine):
    text = "Congratulations! You won 25 Lakh Rupees in KBC Lucky Draw lottery winner."
    res = rules_engine.evaluate(text)
    assert res.score >= 40
    assert "RULE_FAKE_UTILITY_OR_SCHEME" in res.matched_rules


def test_telegram_work_from_home(rules_engine: IndianScamRulesEngine):
    text = "Part time online job: earn Rs 5000 daily by liking youtube video and rating hotels on Telegram."
    res = rules_engine.evaluate(text)
    assert res.score >= 40


def test_official_contact_via_whatsapp(rules_engine: IndianScamRulesEngine):
    text = "Delhi Police Cyber Crime Branch: Connect on WhatsApp video call +91-9876543210 for interrogation."
    res = rules_engine.evaluate(text)
    assert "RULE_OFFICIAL_USING_WHATSAPP" in res.matched_rules


def test_genuine_income_tax_notice(rules_engine: IndianScamRulesEngine):
    text = "Your refund of Rs. 14,280 for AY 2024-25 credited to account ending 4108 vide CMP. Income Tax Department."
    res = rules_engine.evaluate(text)
    assert res.score <= 15
    assert res.scam_type == "Legitimate Notification"


def test_genuine_bank_transaction_alert(rules_engine: IndianScamRulesEngine):
    text = "A/C debited by Rs 1,450.00 on 18-Nov-2024 by UPI Ref 432489128912. Bal: Rs 28,410. If not done by you forward this SMS to 9223008333."
    res = rules_engine.evaluate(text)
    assert res.score <= 15
    assert res.scam_type == "Legitimate Notification"


def test_genuine_echallan_notice(rules_engine: IndianScamRulesEngine):
    text = "Challan #MH022410190012 issued for Red Light Jumping. Pay online on official portal: https://echallan.parivahan.gov.in."
    res = rules_engine.evaluate(text)
    assert res.score <= 15


def test_extract_phone_numbers(rules_engine: IndianScamRulesEngine):
    text = "Call officer at +91 9876543210 or alternate 9812345678 or international +92-3001234567."
    phones = rules_engine.extract_phone_numbers(text)
    assert len(phones) >= 2


def test_extract_upi_ids(rules_engine: IndianScamRulesEngine):
    text = "Transfer money to scammer@okhdfcbank or recovery@paytm or contact info@gmail.com"
    upis = rules_engine.extract_upi_ids(text)
    assert "scammer@okhdfcbank" in upis
    assert "info@gmail.com" not in upis  # common email filtered out


def test_extract_amounts(rules_engine: IndianScamRulesEngine):
    text = "You must pay Rs. 25,000 or fine of ₹5,000 immediately or 2 Lakh rupees."
    amounts = rules_engine.extract_amounts(text)
    assert len(amounts) >= 2

