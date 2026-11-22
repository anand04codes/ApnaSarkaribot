"""
Generate realistic test samples for Indian cyber scam verification and evaluation.
Includes 16 realistic scam samples and 9 realistic genuine samples with full metadata.
"""
import json
from pathlib import Path

SCAMS = [
    {
        "id": "scam_01",
        "title": "Digital Arrest CBI Supreme Court Order",
        "category": "Digital Arrest",
        "expected_verdict": "LIKELY SCAM",
        "text": "CRIME INVESTIGATION DEPT / CBI NOTICE: You are placed under DIGITAL ARREST immediately. A parcel containing MDMA narcotics and 5 fake passports in your name was intercepted by customs at Mumbai Airport. Stay on Skype video call camera until cleared. If you disconnect, non-bailable arrest warrant will be executed within 2 hours. Transfer Rs 2,50,000 security deposit to RBI verification account to prove innocence."
    },
    {
        "id": "scam_02",
        "title": "FedEx Customs Narcotics Threat",
        "category": "Courier / Narcotics",
        "expected_verdict": "LIKELY SCAM",
        "text": "FedEx Alert: Your shipment tracking #FDX984210 bound for Cambodia has been seized by Narcotics Control Bureau (NCB). 140g contraband detected. Delhi Police cyber branch officer Inspector Sharma is investigating. Connect on WhatsApp video call +91-9871234567 immediately to record statement before police custody."
    },
    {
        "id": "scam_03",
        "title": "TRAI 2-Hour Mobile Disconnection",
        "category": "Telecom Impersonation",
        "expected_verdict": "LIKELY SCAM",
        "text": "URGENT TRAI ALERT: All mobile services on this SIM will be terminated within 2 hours due to illegal advertisements and harassing calls reported against your Aadhaar. Press 9 or contact telecom verification desk on 9812345678 to prevent immediate deactivation."
    },
    {
        "id": "scam_04",
        "title": "Electricity Power Disconnection Tonight",
        "category": "Utility Fraud",
        "expected_verdict": "LIKELY SCAM",
        "text": "Dear Consumer, your electricity power will be disconnected tonight at 9:30 PM from the power grid because your previous month bill was not updated. Please immediately contact our Electricity Officer Mr. Verma at mobile 9834567890. Disconnection order #EB-9821."
    },
    {
        "id": "scam_05",
        "title": "SBI YONO Account Blocked KYC Phishing",
        "category": "Banking KYC Phishing",
        "expected_verdict": "LIKELY SCAM",
        "text": "Dear SBI Customer, your YONO account has been suspended today because your PAN card is not linked. Update immediately to prevent permanent debit block: http://sbi-kyc-update.xyz/login. Enter your user ID, password and OTP."
    },
    {
        "id": "scam_06",
        "title": "Fake Traffic E-Challan APK Download",
        "category": "Malware APK",
        "expected_verdict": "LIKELY SCAM",
        "text": "Notice: Pending traffic challan of Rs 1,000 for vehicle DL01AB1234. Pay immediately or your driving license will be cancelled within 24 hours. Download Parivahan challan app to settle: http://echallan-vahan.top/challan.apk"
    },
    {
        "id": "scam_07",
        "title": "PM Kisan 17th Installment Subsidy Lure",
        "category": "Government Scheme Phishing",
        "expected_verdict": "LIKELY SCAM",
        "text": "Pradhan Mantri Kisan Samman Nidhi: Congratulations! Your 17th installment of Rs 6,000 is ready for transfer. Claim your subsidy into your bank account now: http://bit.ly/pm-kisan-claim-2024. Submit Aadhaar and OTP."
    },
    {
        "id": "scam_08",
        "title": "Telegram YouTube Like Work From Home Scam",
        "category": "Job / Task Fraud",
        "expected_verdict": "LIKELY SCAM",
        "text": "Part Time Online Job Offer: Earn Rs 3,500 to Rs 8,000 daily by just liking YouTube videos and rating Google Maps hotels. Work 20 minutes from home. Instant payment via UPI. Join official Telegram manager now: https://t.me/GlobalHR_Task_Payout"
    },
    {
        "id": "scam_09",
        "title": "Enforcement Directorate Money Laundering Extortion",
        "category": "Law Enforcement Impersonation",
        "expected_verdict": "LIKELY SCAM",
        "text": "DIRECTORATE OF ENFORCEMENT (ED): Summons under PMLA Section 50. Inquiry regarding laundering of Rs 48 Crores linked to your bank account. Immediate police custody order issued. To cancel physical arrest and freeze of assets, deposit Rs 5,00,000 in clearing security account rbi-escrow@okhdfcbank."
    },
    {
        "id": "scam_10",
        "title": "Bank Tech Support Remote Access AnyDesk",
        "category": "Remote Access Fraud",
        "expected_verdict": "LIKELY SCAM",
        "text": "HDFC Customer Care: A unauthorized international transaction of Rs 49,999 was attempted. To reverse this charge, please install AnyDesk remote app from Play Store and provide 9-digit code to our security officer to stop debit."
    },
    {
        "id": "scam_11",
        "title": "Digital Arrest Hindi Language Scam",
        "category": "Digital Arrest",
        "expected_verdict": "LIKELY SCAM",
        "text": "सीबीआई और मुंबई पुलिस नोटिस: आपके आधार कार्ड से 16 गैरकानूनी सिम कार्ड खरीदे गए हैं और नशीली दवाओं का अवैध पार्सल भेजा गया है। आपको डिजिटल अरेस्ट में रखा जाता है। स्काइप वीडियो कॉल पर 2 घंटे के भीतर पेश हों, वरना गैर-जमानती गिरफ्तारी वारंट जारी होगा। मामला रफा-दफा करने के लिए सुरक्षा राशि ट्रांसफर करें।"
    },
    {
        "id": "scam_12",
        "title": "Kaun Banega Crorepati Lottery Fraud",
        "category": "Lottery Fraud",
        "expected_verdict": "LIKELY SCAM",
        "text": "KBC Lucky Draw: Congratulations! Your mobile number won 25 Lakh Rupees in all-India lottery draw. To release lottery amount, contact SBI KBC manager Rana Pratap on WhatsApp +91-9988776655 and deposit Rs 12,500 government tax fee."
    },
    {
        "id": "scam_13",
        "title": "Customs International Gift Duty Scam",
        "category": "Customs Duty Fraud",
        "expected_verdict": "LIKELY SCAM",
        "text": "Delhi IGI Airport Customs: A valuable diplomatic parcel containing gold jewellery and iPhone 16 Pro from UK is addressed to you. Pay clearance tax of Rs 35,000 to customs account officer within 4 hours or legal action will be initiated under Customs Act."
    },
    {
        "id": "scam_14",
        "title": "Credit Card Reward Points Expiry Phishing",
        "category": "Card Phishing",
        "expected_verdict": "LIKELY SCAM",
        "text": "ICICI Bank Notice: Your 8,450 reward points worth Rs 8,450 are expiring today at midnight. Redeem cash directly to your card account now: http://reward-icicicard.top/redeem. Enter 16-digit card number, CVV and ATM PIN."
    },
    {
        "id": "scam_15",
        "title": "FASTag Blacklisted Urgent Recharge Link",
        "category": "FASTag Phishing",
        "expected_verdict": "LIKELY SCAM",
        "text": "NHAI FASTag Alert: Your vehicle FASTag is blacklisted due to incomplete KYC. You will be charged double toll fee at toll plazas. Reactivate immediately by submitting KYC documents at: http://fastag-nhai-kyc.buzz/verify"
    },
    {
        "id": "scam_16",
        "title": "WhatsApp Crime Branch Video Interrogation",
        "category": "Police Impersonation",
        "expected_verdict": "LIKELY SCAM",
        "text": "Notice from Delhi Police Cyber Cell: FIR #482/24 registered against your phone number for cyber terrorism. Join WhatsApp video call immediately on +91-8812349999 for verification statement. Failure to answer will lead to immediate arrest at your registered address."
    }
]

GENUINE = [
    {
        "id": "genuine_01",
        "title": "Income Tax Department Refund Credited",
        "category": "Income Tax Alert",
        "expected_verdict": "LOOKS GENUINE",
        "text": "Your refund of Rs. 14,280 for AY 2024-25 has been credited to your bank account ending in 4108 on 12-OCT-2024 vide CMP. Income Tax Department, Government of India. Track status at https://incometax.gov.in. ITD never asks for PIN or OTP."
    },
    {
        "id": "genuine_02",
        "title": "SBI Official Transaction Alert",
        "category": "Bank Transaction SMS",
        "expected_verdict": "LOOKS GENUINE",
        "text": "Dear SBI User, your A/C ending ...5821 debited by Rs 1,450.00 on 18-Nov-2024 at 14:22:10 by UPI Ref 432489128912. Bal: Rs 28,410.20. If not done by you, forward this SMS to 9223008333 or call toll-free 18001234."
    },
    {
        "id": "genuine_03",
        "title": "Parivahan Official E-Challan Notice",
        "category": "Traffic Police Notice",
        "expected_verdict": "LOOKS GENUINE",
        "text": "Challan #MH022410190012 has been issued against vehicle MH02DE4321 for Violation: Red Light Jumping on 19-Oct-2024 11:32 AM. View details and pay online on official government portal: https://echallan.parivahan.gov.in. MoRTH."
    },
    {
        "id": "genuine_04",
        "title": "HDFC Bank Official OTP Security Warning",
        "category": "Bank Security Warning",
        "expected_verdict": "LOOKS GENUINE",
        "text": "589214 is your HDFC Bank NetBanking login OTP. Valid for 3 mins. Do NOT share this OTP with anyone, including bank staff. HDFC Bank will never call you asking for your OTP, password or UPI PIN."
    },
    {
        "id": "genuine_05",
        "title": "BESCOM Electricity Bill Official Receipt",
        "category": "Utility Receipt",
        "expected_verdict": "LOOKS GENUINE",
        "text": "Dear Consumer, Payment of Rs. 1,840 received for Account ID 8721904123 via Bharat BillPay on 15-Nov-2024. Transaction ID: BBPS982141. Thank you, Bangalore Electricity Supply Company Limited (BESCOM)."
    },
    {
        "id": "genuine_06",
        "title": "EPFO Monthly Contribution Credit Alert",
        "category": "Government Provident Fund",
        "expected_verdict": "LOOKS GENUINE",
        "text": "Dear Member, your EPF account ending 8912 has received monthly contribution of Rs. 3,600 for the month of Oct-2024. Total balance is Rs. 1,42,800. View passbook on official website https://epfindia.gov.in or UMANG app. EPFO India."
    },
    {
        "id": "genuine_07",
        "title": "UIDAI Aadhaar Authentication Alert",
        "category": "Identity Verification Alert",
        "expected_verdict": "LOOKS GENUINE",
        "text": "Dear Aadhaar Holder, your Aadhaar ending 9012 was used for biometric authentication at 14:15:30 on 10-Nov-2024. If not done by you, lock your biometrics using mAadhaar app or visit https://uidai.gov.in. UIDAI never calls to ask for OTP."
    },
    {
        "id": "genuine_08",
        "title": "Passport India Speed Post Dispatch Alert",
        "category": "Passport Dispatch",
        "expected_verdict": "LOOKS GENUINE",
        "text": "Your Passport with Application No. DEL0784219901 has been dispatched on 16-Nov-2024 via India Post Speed Post tracking number EK894210984IN. Track your delivery at https://passportindia.gov.in or indiapost.gov.in. Ministry of External Affairs."
    },
    {
        "id": "genuine_09",
        "title": "Axis Bank Monthly Statement Ready",
        "category": "Bank Statement Notice",
        "expected_verdict": "LOOKS GENUINE",
        "text": "Dear Customer, your e-statement for Axis Bank A/C ending 3912 for period 01-Oct-2024 to 31-Oct-2024 has been sent to your registered email. To view, use password format: first 4 letters of name in CAPITAL + date & month of birth (DDMM)."
    }
]

def main():
    base_dir = Path(__file__).resolve().parent.parent / "backend" / "tests" / "samples"
    scams_dir = base_dir / "scams"
    genuine_dir = base_dir / "genuine"
    
    scams_dir.mkdir(parents=True, exist_ok=True)
    genuine_dir.mkdir(parents=True, exist_ok=True)
    
    for item in SCAMS:
        file_path = scams_dir / f"{item['id']}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(item, f, indent=2, ensure_ascii=False)
            
    for item in GENUINE:
        file_path = genuine_dir / f"{item['id']}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(item, f, indent=2, ensure_ascii=False)
            
    print(f"Generated {len(SCAMS)} scam samples in {scams_dir}")
    print(f"Generated {len(GENUINE)} genuine samples in {genuine_dir}")

if __name__ == "__main__":
    main()

