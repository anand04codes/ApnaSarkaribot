"""
Tests for FusionEngine calibration, disagreement handling, and confidence scoring.
"""
from app.core.fusion import FusionEngine
from app.models.schemas import RulesEvaluation, LLMEvaluation, RedFlag, RecommendedAction


def test_fusion_fallback_rules_only():
    rules_eval = RulesEvaluation(
        score=85,
        matched_rules=["RULE_DIGITAL_ARREST"],
        red_flags=[RedFlag(text_span="digital arrest", reason="Fake", category="Extortion", severity="HIGH")],
        scam_type="Digital Arrest Scam"
    )
    res = FusionEngine.fuse(rules_eval=rules_eval, llm_eval=None)
    assert res.verdict == "LIKELY SCAM"
    assert res.risk_score == 85
    assert res.confidence == "MEDIUM"
    assert "local Heuristic" in (res.disagreement_warning or "")


def test_fusion_high_confidence_agreement_scam():
    rules_eval = RulesEvaluation(
        score=90,
        matched_rules=["RULE_DIGITAL_ARREST"],
        red_flags=[RedFlag(text_span="digital arrest", reason="Fake", category="Extortion", severity="HIGH")],
        scam_type="Digital Arrest Scam"
    )
    llm_eval = LLMEvaluation(
        risk_score=95,
        verdict="LIKELY SCAM",
        confidence="HIGH",
        scam_type="Digital Arrest Extortion",
        plain_explanation="This is an extortion scam.",
        red_flags=[RedFlag(text_span="Skype call", reason="Law enforcement does not call", category="Impersonation", severity="HIGH")],
        recommended_actions=[RecommendedAction(step=1, title="Block", description="Block caller", action_type="SAFETY")]
    )
    res = FusionEngine.fuse(rules_eval=rules_eval, llm_eval=llm_eval)
    assert res.verdict == "LIKELY SCAM"
    assert res.risk_score >= 90
    assert res.confidence == "HIGH"
    assert len(res.red_flags) == 2


def test_fusion_high_confidence_agreement_genuine():
    rules_eval = RulesEvaluation(score=5, scam_type="Legitimate Notification")
    llm_eval = LLMEvaluation(
        risk_score=0,
        verdict="LOOKS GENUINE",
        confidence="HIGH",
        scam_type="Bank Transaction SMS",
        plain_explanation="Legitimate bank alert",
        what_it_really_means="Your balance changed"
    )
    res = FusionEngine.fuse(rules_eval=rules_eval, llm_eval=llm_eval)
    assert res.verdict == "LOOKS GENUINE"
    assert res.risk_score <= 10
    assert res.confidence == "HIGH"


def test_fusion_disagreement_lowers_confidence():
    # Rules detected low score, but LLM flagged high score (e.g. novel scam phrasing)
    rules_eval = RulesEvaluation(score=20, scam_type="Unknown")
    llm_eval = LLMEvaluation(
        risk_score=85,
        verdict="LIKELY SCAM",
        confidence="HIGH",
        scam_type="Novel Phishing Attack",
        plain_explanation="AI detected novel extortion script."
    )
    res = FusionEngine.fuse(rules_eval=rules_eval, llm_eval=llm_eval)
    assert res.confidence == "LOW"
    assert res.confidence_score <= 0.65
    assert "divergence" in (res.disagreement_warning or "")
