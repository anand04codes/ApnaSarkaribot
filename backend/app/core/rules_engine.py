"""
Pure Python Rules Engine for Indian Cyber Scam Detection.
Uses regex, heuristics, rapidfuzz, and offline tldextract. No LLM dependency.
"""
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from rapidfuzz import fuzz
import tldextract

from app.models.schemas import RedFlag, RulesEvaluation


class IndianScamRulesEngine:
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).resolve().parent.parent / "data"
        self.data_dir = data_dir
        self.knowledge = self._load_json("knowledge_base.json")
        self.domains_data = self._load_json("official_domains.json")
        
        self.official_domains = set(self.domains_data.get("official_domains", []))
        self.safe_tlds = set(self.domains_data.get("safe_tlds", ["gov.in", "nic.in", "res.in", "ac.in", "edu.in", "mil.in"]))
        self.suspicious_tlds = set(self.domains_data.get("suspicious_tlds", []))
        self.shorteners = set(self.domains_data.get("shortener_domains", []))
        self.remote_apps = self.domains_data.get("remote_access_apps", [])
        
        # Offline TLDExtract to prevent unwanted sandbox DNS lookups
        self.tld_extractor = tldextract.TLDExtract(cache_dir=False, suffix_list_urls=None)
        
        self._compile_patterns()

    def _load_json(self, filename: str) -> Dict[str, Any]:
        filepath = self.data_dir / filename
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _compile_patterns(self):
        # 1. Digital Arrest / Law Enforcement Impersonation
        self.re_digital_arrest = re.compile(
            r"(?i)\b(digital\s*arrest|digital\s*custody|डिजिटल\s*अरेस्ट|"
            r"video\s*call\s*(?:interrogation|investigation|statement)|skype\s*(?:interrogation|call)|"
            r"stay\s*on\s*(?:camera|skype|call)\s*till\s*clearance)\b"
        )
        self.re_law_enforcement = re.compile(
            r"(?i)\b(cbi|central\s*bureau\s*of\s*investigation|enforcement\s*directorate|directorate\s*of\s*enforcement|"
            r"\bed\b\s*(?:summons|notice|office|inquiry)|pmla|narcotics\s*control\s*bureau|ncb|"
            r"mumbai\s*police|delhi\s*police|crime\s*investigation\s*dept|cyber\s*crime\s*cell|cyber\s*branch|"
            r"customs\s*(?:department|officer|clearance)?|interpol|supreme\s*court\s*of\s*india|"
            r"सीबीआई|प्रवर्तन\s*निदेशालय|दिल्ली\s*पुलिस|मुंबई\s*पुलिस|साइबर\s*क्राइम)\b"
        )
        self.re_parcel_drugs = re.compile(
            r"(?i)\b(parcel|courier|consignment|fedex|dhl|shipment)\b.*?\b(drugs|narcotics|mdma|contraband|"
            r"fake\s*passports?|money\s*laundering|seized|illegal\s*substances?|पार्सल|ड्रग्स|अवैध)\b"
        )
        self.re_arrest_threat = re.compile(
            r"(?i)\b(arrest\s*warrant|warrant\s*of\s*arrest|non-bailable|गिरफ्तारी\s*वारंट|"
            r"immediate\s*(?:police\s*)?arrest|police\s*custody|freeze\s*(?:all\s*)?your\s*accounts|"
            r"national\s*security\s*act|fir\s*#[0-9]+)\b"
        )

        # 2. Telecom / TRAI Disconnection Threats
        self.re_trai_telecom = re.compile(
            r"(?i)\b(trai|telecom\s*regulatory|sim\s*(?:services?|card)?\s*will\s*be\s*(?:terminated|blocked|deactivated)|"
            r"(?:terminated|disconnected|blocked)\s*within\s*(?:[1-4]\s*hours?|2\s*hours?)|"
            r"press\s*9\s*or\s*contact|telecom\s*verification\s*desk)\b"
        )

        # 3. Urgency and Threat Language
        self.re_urgency = re.compile(
            r"(?i)\b(within\s*(?:[1-4]\s*hours?|24\s*hours?|few\s*minutes)|"
            r"immediately\s*or\s*(?:else|be\s*disconnected|blocked|cancelled)|"
            r"tonight\s*at\s*9(?::30)?\s*(?:pm)?|power\s*will\s*be\s*disconnected|"
            r"sim\s*(?:card)?\s*will\s*be\s*(?:deactivated|blocked|terminated)|"
            r"permanent\s*debit\s*block|2\s*घंटे\s*के\s*भीतर|आज\s*रात|बिजली\s*काट\s*दी\s*जाएगी|तुरंत\s*कार्रवाई)\b"
        )

        # 4. Sensitive Credentials / Remote Access Apps
        self.re_sensitive_creds = re.compile(
            r"(?i)\b(enter\s*(?:your\s*)?(?:upi\s*)?pin|share\s*(?:your\s*)?otp|"
            r"one\s*time\s*password|cvv\s*number|cvv\s*and\s*atm\s*pin|card\s*expiry|atm\s*pin|"
            r"user\s*id,\s*password\s*and\s*otp|submit\s*aadhaar\s*and\s*otp|"
            r"ओटीपी|यूपीआई\s*पिन|सीवीवी)\b"
        )
        
        # 5. Financial demands & fake clearance / security deposits
        self.re_money_clearance = re.compile(
            r"\b(?:deposit|transfer)\b.*?\b(?:clearing|security|verification|escrow|rbi|secret|safe).{0,30}?\baccount\b|"
            r"\b(?:pay|deposit|transfer|demanding|demand)\b.*?\b(?:rs\.?|₹)?[0-9,]+.*?\b(?:avoid|clear|cancel|settle)\s*(?:arrest|police|custody|case|warrant|action)\b|"
            r"\b(clearance\s*(?:deposit|fee|tax)|refundable\s*security\s*deposit|"
            r"pay\s*(?:penalty|tax\s*fee)\s*to\s*(?:avoid|clear|release)|settlement\s*(?:fee|amount)|"
            r"release\s*(?:funds?|lottery\s*amount)\s*fee|आरबीआई\s*सत्यापन\s*खाता|सुरक्षा\s*राशि|मामला\s*रफा-दफा)\b",
            re.IGNORECASE
        )

        # 6. Phishing / Fake Utilities / Freebies / APKs / Lottery / Task Scams
        self.re_fake_utility_apk = re.compile(
            r"(?i)\b(electricity\s*(?:power|bill)?\s*will\s*be\s*disconnected|previous\s*month\s*bill\s*was\s*not\s*updated|"
            r"electricity\s*officer|bijli\s*bill|power\s*grid|"
            r"pm\s*kisan\s*(?:1[0-9]th)?\s*installment|free\s*recharge|"
            r"lottery\s*winner|lucky\s*draw|kbc|kaun\s*banega\s*crorepati|won\s*[0-9]+\s*lakh|"
            r"part\s*time\s*(?:online\s*)?job|youtube\s*(?:like|video)\s*job|earn\s*(?:rs|₹)?[0-9]+(?:\s*to\s*[0-9]+)?\s*daily|"
            r"globalhr_task|telegram\s*(?:manager|payout)|"
            r"fastag\s*is\s*blacklisted|double\s*toll|reactivate\s*immediately|"
            r"reward\s*points\s*worth\s*(?:rs|₹)|expiring\s*today\s*at\s*midnight|"
            r"\.apk\b|download\s*our\s*app\s*from\s*link|pm\s*yojana|लाडली\s*बहना)\b"
        )

        # 7. Suspicious WhatsApp / personal number / international spoof
        self.re_intl_caller = re.compile(
            r"(?:\+92|\+880|\+93|\+1\s*\(?[0-9]{3}\)?|\+44)[-\s]?[0-9]{7,10}"
        )
        self.re_indian_mobile = re.compile(
            r"(?:(?:\+91|91|0)?[-\s]?[6-9]\d{9})"
        )
        self.re_whatsapp_claim = re.compile(
            r"(?i)\b(contact\s*(?:us\s*)?on\s*whatsapp|whatsapp\s*video\s*call|whatsapp\s*call|whatsapp\s*officer|wa\.me/|t\.me/)\b"
        )

        # 8. URLs extraction
        self.re_urls = re.compile(
            r"https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z0-9/._?=%#&~+-]+"
        )

        # 9. Genuine Indicators
        self.re_genuine_bank_alert = re.compile(
            r"(?i)(debited\s*by|credited\s*to|upi\s*ref|avl\s*bal|if\s*not\s*done\s*by\s*you\s*(?:forward|sms|call)|"
            r"toll[\s-]*free\s*1800|forward\s*this\s*sms\s*to\s*922|block\s*card\s*call|netbanking\s*login\s*otp|"
            r"do\s*not\s*share\s*this\s*otp\s*with\s*anyone|e-statement\s*for.*?a/c)"
        )
        self.re_genuine_gov_notice = re.compile(
            r"(?i)(income\s*tax\s*department|ay\s*20[2-3][0-9]|intimation\s*u/s\s*143\(1\)|"
            r"pan\s*[a-z]{5}[0-9]{4}[a-z]|din\s*no|vide\s*cmp|acknowledgment\s*receipt|"
            r"central\s*board\s*of\s*direct\s*taxes|ministry\s*of\s*external\s*affairs|"
            r"speed\s*post\s*tracking|epf\s*account|monthly\s*contribution|umang\s*app|"
            r"biometric\s*authentication|maadhaar|bharat\s*billpay|bbps)"
        )

    def extract_urls(self, text: str) -> List[str]:
        return self.re_urls.findall(text)

    def extract_phone_numbers(self, text: str) -> List[str]:
        matches = self.re_indian_mobile.findall(text)
        intl = self.re_intl_caller.findall(text)
        return list(set(m.strip() for m in matches + intl))

    def extract_upi_ids(self, text: str) -> List[str]:
        re_upi = re.compile(r"[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}")
        matches = re_upi.findall(text)
        common_emails = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com"}
        return [m for m in matches if m.split("@")[-1].lower() not in common_emails]

    def extract_amounts(self, text: str) -> List[str]:
        re_amt = re.compile(
            r"(?i)(?:rs\.?|inr|₹)\s*[0-9]+(?:,[0-9]+)*(?:\.[0-9]{2})?|\b[0-9]+(?:,[0-9]+)*\s*(?:rupees|lakh|crore)\b"
        )
        return [m.strip() for m in re_amt.findall(text)]

    def is_official_gov_domain(self, domain: str) -> bool:
        """Check if domain ends with authenticated Indian government / institutional suffixes."""
        domain_lower = domain.lower()
        if domain_lower.endswith(".gov.in") or domain_lower.endswith(".nic.in") or domain_lower.endswith(".mil.in"):
            return True
        if domain_lower in self.official_domains:
            return True
        return False

    def inspect_url_heuristics(self, url: str) -> Tuple[int, List[RedFlag]]:
        score = 0
        red_flags: List[RedFlag] = []
        try:
            extracted = self.tld_extractor(url)
            domain = extracted.registered_domain.lower()
            suffix = extracted.suffix.lower()
        except Exception:
            return 20, [RedFlag(
                text_span=url,
                reason="Malformed or unparseable URL.",
                category="Phishing Link",
                severity="MEDIUM"
            )]

        # Check official authenticated Gov/Bank domain
        if self.is_official_gov_domain(domain):
            # Safe official government or verified domain - negative score (trust boost)
            return -50, []

        # IP address URL
        if re.match(r"^https?://[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", url):
            score += 45
            red_flags.append(RedFlag(
                text_span=url,
                reason="URL points directly to an IP address instead of an authenticated domain name.",
                category="Phishing Link",
                severity="HIGH"
            ))

        # Punycode / IDN
        if "xn--" in url.lower():
            score += 40
            red_flags.append(RedFlag(
                text_span=url,
                reason="Punycode detected (xn--): used to deceive users with visually identical Unicode characters.",
                category="Phishing Link",
                severity="HIGH"
            ))

        # URL Shortener
        if domain in self.shorteners:
            score += 35
            red_flags.append(RedFlag(
                text_span=url,
                reason=f"URL shortener ({domain}) hides the actual destination website. Official agencies never use shorteners.",
                category="Phishing Link",
                severity="HIGH"
            ))

        # Suspicious TLD (.xyz, .top, .buzz, etc.)
        if suffix in self.suspicious_tlds:
            score += 40
            red_flags.append(RedFlag(
                text_span=url,
                reason=f"Suspicious top-level domain (.{suffix}) frequently used by cyber criminals for short-lived phishing websites.",
                category="Phishing Link",
                severity="HIGH"
            ))

        # APK download in URL
        if ".apk" in url.lower():
            score += 50
            red_flags.append(RedFlag(
                text_span=url,
                reason="Link directly triggers an Android APK application download. Common malware delivery technique.",
                category="Malware Distribution",
                severity="HIGH"
            ))

        # Lookalike domain check against official domains
        for off_dom in self.official_domains:
            if domain == off_dom:
                return -50, []
            
            # Typo-squatting
            similarity = fuzz.ratio(domain, off_dom)
            if 70 <= similarity < 100:
                score += 50
                red_flags.append(RedFlag(
                    text_span=domain,
                    reason=f"Lookalike / Typo-squatting domain imitating official '{off_dom}' ({similarity}% similarity).",
                    category="Spoofed Domain",
                    severity="HIGH"
                ))
                break
            
            # Keyword embedded in unofficial domain (e.g. sbi-kyc-update.xyz, echallan-vahan.top)
            keyword = off_dom.split(".")[0]
            if len(keyword) > 3 and keyword in domain and not (domain.endswith(".gov.in") or domain.endswith(".nic.in")):
                score += 40
                red_flags.append(RedFlag(
                    text_span=domain,
                    reason=f"Domain contains official brand '{keyword}' but does not belong to official '{off_dom}'.",
                    category="Phishing Link",
                    severity="HIGH"
                ))
                break

        return score, red_flags

    def evaluate(self, text: str) -> RulesEvaluation:
        text_clean = text.strip()
        matched_rules: List[str] = []
        red_flags: List[RedFlag] = []
        raw_score = 0
        detected_scam_type = None

        if not text_clean:
            return RulesEvaluation(
                score=0,
                matched_rules=[],
                red_flags=[],
                scam_type="Unknown",
                details={"reason": "Empty input"}
            )

        # 1. Digital Arrest Check (FATAL RED FLAG in India)
        da_match = self.re_digital_arrest.search(text_clean)
        if da_match:
            raw_score += 65
            matched_rules.append("RULE_DIGITAL_ARREST")
            detected_scam_type = "Digital Arrest Scam"
            start, end = da_match.span()
            red_flags.append(RedFlag(
                text_span=da_match.group(0),
                reason="The concept of 'Digital Arrest' does NOT exist under Indian law. No Indian agency ever arrests or interrogates citizens over video calls.",
                category="Impersonation & Extortion",
                severity="HIGH",
                start_char=start,
                end_char=end
            ))

        # 2. Law Enforcement / Official Agency Impersonation
        le_match = self.re_law_enforcement.search(text_clean)
        if le_match:
            matched_rules.append("RULE_LAW_ENFORCEMENT_MENTION")
            if (self.re_parcel_drugs.search(text_clean) or 
                self.re_arrest_threat.search(text_clean) or 
                self.re_money_clearance.search(text_clean) or 
                self.re_whatsapp_claim.search(text_clean) or 
                da_match):
                raw_score += 40
                if not detected_scam_type:
                    detected_scam_type = "Law Enforcement Impersonation"
                start, end = le_match.span()
                red_flags.append(RedFlag(
                    text_span=le_match.group(0),
                    reason="Impersonating central law enforcement agencies (CBI, ED, Police, Narcotics, Customs) to intimidate the victim.",
                    category="Impersonation",
                    severity="HIGH",
                    start_char=start,
                    end_char=end
                ))

        # 3. Parcel seized with drugs / contraband
        parcel_match = self.re_parcel_drugs.search(text_clean)
        if parcel_match:
            raw_score += 45
            matched_rules.append("RULE_PARCEL_DRUGS_SEIZURE")
            if not detected_scam_type:
                detected_scam_type = "Fake Parcel / Courier Scam"
            start, end = parcel_match.span()
            red_flags.append(RedFlag(
                text_span=parcel_match.group(0),
                reason="False claim that an illegal courier/parcel containing drugs or contraband in your name was intercepted.",
                category="Extortion",
                severity="HIGH",
                start_char=start,
                end_char=end
            ))

        # 4. Immediate Arrest Threat / Account Freeze
        arrest_match = self.re_arrest_threat.search(text_clean)
        if arrest_match:
            raw_score += 35
            matched_rules.append("RULE_ARREST_THREAT")
            start, end = arrest_match.span()
            red_flags.append(RedFlag(
                text_span=arrest_match.group(0),
                reason="Threatening immediate arrest or bank account freeze. Real legal summons are served physically, not over SMS or WhatsApp.",
                category="Intimidation",
                severity="HIGH",
                start_char=start,
                end_char=end
            ))

        # 5. TRAI / Telecom 2-Hour Disconnection Scam
        trai_match = self.re_trai_telecom.search(text_clean)
        if trai_match:
            raw_score += 45
            matched_rules.append("RULE_TRAI_DISCONNECTION")
            if not detected_scam_type:
                detected_scam_type = "TRAI Telecom Disconnection Scam"
            start, end = trai_match.span()
            red_flags.append(RedFlag(
                text_span=trai_match.group(0),
                reason="TRAI and DoT never issue 2-hour disconnection ultimatums or demand phone verifications to keep SIMs active.",
                category="Impersonation",
                severity="HIGH",
                start_char=start,
                end_char=end
            ))

        # 6. Extreme Urgency / Disconnection Ultimatums
        urgency_match = self.re_urgency.search(text_clean)
        if urgency_match:
            raw_score += 30
            matched_rules.append("RULE_ARTIFICIAL_URGENCY")
            start, end = urgency_match.span()
            red_flags.append(RedFlag(
                text_span=urgency_match.group(0),
                reason="Artificial urgency designed to cause panic so the victim acts before verifying facts.",
                category="Psychological Manipulation",
                severity="HIGH",
                start_char=start,
                end_char=end
            ))

        # 7. Sensitive Financial Credentials Demanded
        cred_match = self.re_sensitive_creds.search(text_clean)
        if cred_match:
            raw_score += 50
            matched_rules.append("RULE_CREDENTIAL_HARVESTING")
            if not detected_scam_type:
                detected_scam_type = "Banking / Credential Phishing"
            start, end = cred_match.span()
            red_flags.append(RedFlag(
                text_span=cred_match.group(0),
                reason="Demand for confidential credentials (OTP, UPI PIN, CVV, Passwords). Official bodies and banks NEVER ask for your PIN or OTP.",
                category="Credential Harvesting",
                severity="HIGH",
                start_char=start,
                end_char=end
            ))

        # 8. Remote Access App Installation
        text_lower = text_clean.lower()
        for app in self.remote_apps:
            if app in text_lower:
                raw_score += 50
                matched_rules.append(f"RULE_REMOTE_APP_{app.upper()}")
                if not detected_scam_type:
                    detected_scam_type = "Remote Access Tech Support Fraud"
                idx = text_lower.find(app)
                red_flags.append(RedFlag(
                    text_span=text_clean[idx:idx+len(app)],
                    reason=f"Asking to install '{app}' allows scammers to gain full remote control of your phone and bank accounts.",
                    category="Remote Access Scam",
                    severity="HIGH",
                    start_char=idx,
                    end_char=idx+len(app)
                ))
                break

        # 9. Money Transfer to 'RBI / Verification / Clearing' Account
        clear_match = self.re_money_clearance.search(text_clean)
        if clear_match:
            raw_score += 60
            matched_rules.append("RULE_DEMAND_CLEARANCE_TRANSFER")
            if not detected_scam_type:
                detected_scam_type = "Financial Extortion Fraud"
            start, end = clear_match.span()
            red_flags.append(RedFlag(
                text_span=clear_match.group(0),
                reason="Demand to transfer funds to a 'security', 'verification', 'escrow' or 'RBI account'. The Reserve Bank of India does not hold individual verification accounts.",
                category="Financial Fraud",
                severity="HIGH",
                start_char=start,
                end_char=end
            ))

        # 10. Fake Utility / E-Challan / PM Scheme / Lottery / Task Scams
        util_match = self.re_fake_utility_apk.search(text_clean)
        if util_match:
            raw_score += 45
            matched_rules.append("RULE_FAKE_UTILITY_OR_SCHEME")
            if not detected_scam_type:
                match_txt = util_match.group(0).lower()
                if "electricity" in match_txt or "power" in match_txt or "bijli" in match_txt:
                    detected_scam_type = "Electricity Bill Disconnection Scam"
                elif "lottery" in match_txt or "kbc" in match_txt:
                    detected_scam_type = "Lottery / Prize Draw Fraud"
                elif "job" in match_txt or "youtube" in match_txt or "task" in match_txt:
                    detected_scam_type = "Part-Time Task / Telegram Job Scam"
                elif "fastag" in match_txt:
                    detected_scam_type = "FASTag Blacklist Scam"
                elif "pm kisan" in match_txt or "yojana" in match_txt:
                    detected_scam_type = "Fake PM Subsidy Scheme Scam"
                else:
                    detected_scam_type = "Phishing / Social Engineering Scam"
            start, end = util_match.span()
            red_flags.append(RedFlag(
                text_span=util_match.group(0),
                reason="Typical lure text for electricity disconnection, lottery, fake PM subsidy, fraudulent job task, or APK malware.",
                category="Phishing",
                severity="HIGH",
                start_char=start,
                end_char=end
            ))

        # 11. WhatsApp or Personal Mobile Contact for Official Business
        wa_match = self.re_whatsapp_claim.search(text_clean)
        if wa_match:
            raw_score += 35
            matched_rules.append("RULE_OFFICIAL_USING_WHATSAPP")
            start, end = wa_match.span()
            red_flags.append(RedFlag(
                text_span=wa_match.group(0),
                reason="Government authorities, courts and police never conduct official proceedings or support via WhatsApp personal chat or Telegram channels.",
                category="Impersonation",
                severity="HIGH",
                start_char=start,
                end_char=end
            ))

        # 12. URLs Analysis
        urls = self.extract_urls(text_clean)
        for u in urls:
            url_score, url_flags = self.inspect_url_heuristics(u)
            raw_score += url_score
            red_flags.extend(url_flags)
            if url_score > 20:
                matched_rules.append("RULE_MALICIOUS_OR_SUSPICIOUS_URL")

        # 13. Counterbalance with Genuine Indicators (safeguarding against false alarms)
        is_genuine_bank = bool(self.re_genuine_bank_alert.search(text_clean))
        is_genuine_gov = bool(self.re_genuine_gov_notice.search(text_clean))
        has_official_gov_domain = any(self.is_official_gov_domain(self.tld_extractor(u).registered_domain) for u in urls) if urls else False

        # If genuine indicators present and NO toxic scam patterns:
        toxic_triggers = (da_match or cred_match or clear_match or parcel_match or trai_match)
        if (is_genuine_bank or is_genuine_gov or has_official_gov_domain) and not toxic_triggers:
            # Grant strong credibility discount
            raw_score = 0
            red_flags.clear()
            detected_scam_type = "Legitimate Notification"

        # Final score bounding (0 - 100)
        final_score = max(0, min(100, raw_score))

        if not detected_scam_type:
            if final_score >= 65:
                detected_scam_type = "Suspected Cyber Fraud"
            elif final_score >= 35:
                detected_scam_type = "Suspicious Communication"
            else:
                detected_scam_type = "Likely Genuine Communication"

        return RulesEvaluation(
            score=final_score,
            matched_rules=matched_rules,
            red_flags=red_flags,
            scam_type=detected_scam_type,
            details={
                "extracted_urls": urls,
                "extracted_phone_numbers": self.extract_phone_numbers(text_clean),
                "extracted_upi_ids": self.extract_upi_ids(text_clean),
                "extracted_amounts": self.extract_amounts(text_clean)
            }
        )
