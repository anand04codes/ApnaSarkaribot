"""
Static URL Inspector: Safe, non-executing link analysis.
Detects typosquatting/lookalike domains, shorteners, suspicious TLDs, IP URLs, punycode,
and queries WHOIS registration details safely.
"""
import re
import socket
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import tldextract
from rapidfuzz import fuzz

from app.models.schemas import UrlCheckResponse


class StaticUrlInspector:
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).resolve().parent.parent / "data"
        
        filepath = data_dir / "official_domains.json"
        domains_data = {}
        if filepath.exists():
            import json
            with open(filepath, "r", encoding="utf-8") as f:
                domains_data = json.load(f)

        self.official_domains = set(domains_data.get("official_domains", []))
        self.suspicious_tlds = set(domains_data.get("suspicious_tlds", []))
        self.shorteners = set(domains_data.get("shortener_domains", []))
        self.extractor = tldextract.TLDExtract(cache_dir=False, suffix_list_urls=None)

    def is_official_gov(self, domain: str) -> bool:
        d = domain.lower()
        return d.endswith(".gov.in") or d.endswith(".nic.in") or d.endswith(".mil.in") or d in self.official_domains

    def inspect(self, raw_url: str) -> UrlCheckResponse:
        url = raw_url.strip()
        if not url.startswith(("http://", "https://")):
            url = "http://" + url

        parsed = urlparse(url)
        extracted = self.extractor(url)

        domain = extracted.registered_domain.lower() if extracted.registered_domain else parsed.netloc.lower()
        suffix = extracted.suffix.lower()
        hostname = parsed.hostname.lower() if parsed.hostname else ""
        has_https = parsed.scheme.lower() == "https"

        risk_score = 0
        reasons: List[str] = []
        is_lookalike = False
        lookalike_target = None
        max_similarity = 0.0

        # 1. Official Government or Known Institution
        is_safe = self.is_official_gov(domain)
        if is_safe:
            risk_score = 0
            verdict = "LOOKS GENUINE"
            reasons.append(f"Authenticated official domain '{domain}'. Indian government suffixes (.gov.in, .nic.in) are restricted and cannot be purchased by fraudsters.")
            return UrlCheckResponse(
                url=raw_url,
                normalized_url=url,
                domain=hostname,
                registered_domain=domain,
                is_safe_domain=True,
                is_lookalike=False,
                lookalike_target=None,
                similarity_score=1.0,
                is_shortener=False,
                suspicious_tld=False,
                is_ip_address=False,
                has_punycode=False,
                has_https=has_https,
                risk_score=0,
                verdict="LOOKS GENUINE",
                reasons=reasons,
                whois_info={"status": "Official Registry Validated"}
            )

        # 2. IP-based Host
        is_ip = bool(re.match(r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$", hostname))
        if is_ip:
            risk_score += 55
            reasons.append(f"Host is an IP address ({hostname}) rather than a registered domain name. High probability of phishing or command server.")

        # 3. Punycode / IDN
        has_puny = "xn--" in hostname
        if has_puny:
            risk_score += 45
            reasons.append("Punycode (xn--) detected: deceptive domain masquerading as a legitimate brand using visually identical Unicode characters.")

        # 4. URL Shortener
        is_shortener = domain in self.shorteners
        if is_shortener:
            risk_score += 40
            reasons.append(f"Domain is a known link shortener ({domain}). Hides the final destination and is banned for official government communications.")

        # 5. Suspicious TLD
        is_suspicious_tld = suffix in self.suspicious_tlds
        if is_suspicious_tld:
            risk_score += 40
            reasons.append(f"Top-level domain (.{suffix}) has high abuse rates and is commonly utilized by temporary phishing campaigns.")

        # 6. APK or Executable in URL Path
        if url.lower().endswith(".apk") or ".apk?" in url.lower():
            risk_score += 50
            reasons.append("Direct Android Application Package (.apk) download link. Extreme risk of mobile Trojan or credential stealer.")

        # 7. Lookalike / Typosquatting Check
        for off_dom in self.official_domains:
            sim = fuzz.ratio(domain, off_dom)
            if sim > max_similarity:
                max_similarity = sim
            if 70 <= sim < 100:
                is_lookalike = True
                lookalike_target = off_dom
                risk_score += 50
                reasons.append(f"Domain '{domain}' is a look-alike spoof of official '{off_dom}' ({sim}% similarity).")
                break

            # Keyword embedded in domain (e.g. incometax-gov.online, sbi-quick.top)
            keyword = off_dom.split(".")[0]
            if len(keyword) > 3 and keyword in domain:
                is_lookalike = True
                lookalike_target = off_dom
                risk_score += 45
                reasons.append(f"Domain contains official keyword '{keyword}' in an unauthorized domain name.")
                break

        # 8. HTTPS status
        if not has_https:
            risk_score += 20
            reasons.append("Connection is not secured with HTTPS (unencrypted HTTP protocol).")

        # 9. WHOIS lookup (safe with graceful fallback)
        whois_data = self._safe_whois(domain)

        # Calibrate risk score and verdict
        risk_score = max(0, min(100, risk_score))
        if risk_score >= 65:
            verdict = "LIKELY SCAM"
        elif risk_score >= 35:
            verdict = "SUSPICIOUS"
        else:
            verdict = "LOOKS GENUINE"

        return UrlCheckResponse(
            url=raw_url,
            normalized_url=url,
            domain=hostname,
            registered_domain=domain,
            is_safe_domain=False,
            is_lookalike=is_lookalike,
            lookalike_target=lookalike_target,
            similarity_score=round(max_similarity / 100.0, 2),
            is_shortener=is_shortener,
            suspicious_tld=is_suspicious_tld,
            is_ip_address=is_ip,
            has_punycode=has_puny,
            has_https=has_https,
            risk_score=risk_score,
            verdict=verdict,
            reasons=reasons,
            whois_info=whois_data
        )

    def _safe_whois(self, domain: str) -> Dict[str, Any]:
        """Query whois safely with timeout; fallback to placeholder if offline or blocked."""
        try:
            import whois
            w = whois.whois(domain, timeout=1.0)
            if not w:
                raise ValueError("Empty WHOIS response")
            return {
                "registrar": str(w.get("registrar", "Unknown")),
                "creation_date": str(w.get("creation_date", "Unknown")),
                "expiration_date": str(w.get("expiration_date", "Unknown")),
                "country": str(w.get("country", "Unknown")),
                "status": "Queried successfully"
            }
        except Exception:
            return {
                "status": "WHOIS lookup unavailable or query timed out (safe fallback mode)"
            }
