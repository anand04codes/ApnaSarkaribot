"""
Tests for StaticUrlInspector.
Tests lookalike detection, official domain recognition, IP hosts, shorteners,
suspicious TLDs, and punycode.
"""
from app.core.url_inspector import StaticUrlInspector


def test_official_gov_domain_genuine(url_inspector: StaticUrlInspector):
    res = url_inspector.inspect("https://incometax.gov.in/portal")
    assert res.is_safe_domain is True
    assert res.verdict == "LOOKS GENUINE"
    assert res.risk_score == 0


def test_official_echallan_domain(url_inspector: StaticUrlInspector):
    res = url_inspector.inspect("https://echallan.parivahan.gov.in/index/accused-challan")
    assert res.is_safe_domain is True
    assert res.verdict == "LOOKS GENUINE"


def test_lookalike_spoofed_domain(url_inspector: StaticUrlInspector):
    res = url_inspector.inspect("http://incometax-gov.in/login")
    assert res.is_lookalike is True
    assert res.verdict == "LIKELY SCAM"
    assert res.risk_score >= 45


def test_suspicious_tld(url_inspector: StaticUrlInspector):
    res = url_inspector.inspect("http://sbi-kyc-verify.xyz/update")
    assert res.suspicious_tld is True
    assert res.verdict in ["LIKELY SCAM", "SUSPICIOUS"]


def test_url_shortener(url_inspector: StaticUrlInspector):
    res = url_inspector.inspect("https://bit.ly/claim-pm-kisan-subsidy")
    assert res.is_shortener is True
    assert res.verdict in ["LIKELY SCAM", "SUSPICIOUS"]


def test_ip_address_host(url_inspector: StaticUrlInspector):
    res = url_inspector.inspect("http://192.168.1.100/download.apk")
    assert res.is_ip_address is True
    assert res.verdict == "LIKELY SCAM"


def test_punycode_detection(url_inspector: StaticUrlInspector):
    res = url_inspector.inspect("https://xn--e1afmkfd.xn--p1ai/bank")
    assert res.has_punycode is True
    assert res.verdict in ["LIKELY SCAM", "SUSPICIOUS"]


def test_unprefixed_url(url_inspector: StaticUrlInspector):
    res = url_inspector.inspect("cybercrime.gov.in")
    assert res.is_safe_domain is True
    assert res.verdict == "LOOKS GENUINE"

