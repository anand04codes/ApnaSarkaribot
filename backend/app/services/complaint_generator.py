"""
Complaint Summary Generator for Cyber Crime Reporting.
Formats reports specifically compliant with National Cyber Crime Reporting Portal (cybercrime.gov.in)
and helpline 1930 incident intake standards.
"""
from datetime import datetime
from typing import List, Optional
from app.models.schemas import ComplaintSummary, RulesEvaluation, AnalysisResponse


class ComplaintGenerator:
    @staticmethod
    def generate_complaint(
        text: str,
        rules_eval: RulesEvaluation,
        fused_verdict: Optional[str] = None,
        claimed_agency: Optional[str] = None,
        user_state: Optional[str] = None
    ) -> ComplaintSummary:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M IST")

        details = rules_eval.details
        suspect_numbers = details.get("extracted_phone_numbers", [])
        suspect_urls = details.get("extracted_urls", [])
        suspect_upi_ids = details.get("extracted_upi_ids", [])
        amounts = details.get("extracted_amounts", [])

        amount_str = ", ".join(amounts) if amounts else "Not specified / Demanded verbally"

        # If claimed agency was not given, guess from matched rules or text
        agency_name = claimed_agency or "Unknown / Impersonated Agency"
        if "RULE_LAW_ENFORCEMENT_MENTION" in rules_eval.matched_rules:
            for ag in ["CBI", "ED", "Mumbai Police", "Delhi Police", "Customs", "Narcotics Control Bureau", "TRAI"]:
                if ag.lower() in text.lower():
                    agency_name = ag
                    break

        scam_cat = rules_eval.scam_type or "Cyber Fraud / Financial Extortion"

        # Format ready-to-paste formal complaint statement for cybercrime.gov.in
        lines = [
            "===========================================================",
            "INCIDENT COMPLAINT SUMMARY FOR CYBERCRIME.GOV.IN / 1930",
            "Generated via SarkariSach Citizen Verification Assistant",
            "===========================================================",
            f"DATE & TIME OF COMPLAINT: {date_str}",
            f"SUSPECTED CRIME CATEGORY: {scam_cat}",
            f"IMPERSONATED AUTHORITY   : {agency_name}",
            f"AMOUNTS DEMANDED/LOST    : {amount_str}",
            f"SUSPECT MOBILE NUMBER(S) : {', '.join(suspect_numbers) if suspect_numbers else 'None detected in text'}",
            f"SUSPECT UPI ID(S)        : {', '.join(suspect_upi_ids) if suspect_upi_ids else 'None detected in text'}",
            f"SUSPECT URL(S) / DOMAINS : {', '.join(suspect_urls) if suspect_urls else 'None detected'}",
            f"COMPLAINANT JURISDICTION : {user_state or 'India'}",
            "-----------------------------------------------------------",
            "INCIDENT NARRATIVE / FACTS OF COMPLAINT:",
            "The victim received unsolicited communication from perpetrators claiming to represent",
            f"law enforcement/official utility authorities ({agency_name}). The communication employed",
            "intimidation tactics, false allegations of contraband/arrest warrants, or urgency to coerce",
            "unauthorized financial transfers or harvesting of sensitive credentials.",
            "",
            "INCIDENT EVIDENCE EXCERPT:",
            f'"{text.strip()[:600]}"' + ("..." if len(text.strip()) > 600 else ""),
            "-----------------------------------------------------------",
            "PRAYER / RELIEF SOUGHT:",
            "1. Register this grievance on the National Cyber Crime Reporting Portal under IT Act 2000 / BNS.",
            "2. Block and trace the suspect phone number(s) and UPI VPA(s) under DoT Chakshu & NPCI protocols.",
            "3. If any fund transfer occurred, instruct the designated nodal bank officer to freeze the beneficiary account.",
            "==========================================================="
        ]

        summary_text = "\n".join(lines)

        return ComplaintSummary(
            incident_date=date_str,
            scam_category=scam_cat,
            suspect_numbers=suspect_numbers,
            suspect_urls=suspect_urls,
            suspect_upi_ids=suspect_upi_ids,
            claimed_agency=agency_name,
            demanded_amount=amount_str,
            summary_text=summary_text,
            filing_portal="https://cybercrime.gov.in",
            helpline="1930"
        )

