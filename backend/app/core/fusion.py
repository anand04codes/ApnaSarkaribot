"""
Fusion Layer: Combines Rules Engine evaluation and Gemini LLM analysis
into a calibrated final risk verdict with explicit confidence scoring.
"""
from typing import Optional, List, Dict, Any, Tuple
from app.models.schemas import RedFlag, RecommendedAction, AnalysisResponse, RulesEvaluation, LLMEvaluation


class FusionEngine:
    @staticmethod
    def fuse(
        rules_eval: RulesEvaluation,
        llm_eval: Optional[LLMEvaluation] = None,
        language: str = "en",
        input_type: str = "text",
        extracted_text: Optional[str] = None,
        media_analysis: Optional[Dict[str, Any]] = None
    ) -> AnalysisResponse:
        """
        Calibrate and merge rules engine and LLM results.
        Gracefully handles LLM absence or network errors.
        """
        rules_score = rules_eval.score
        
        # 1. Fallback when LLM is unavailable
        if llm_eval is None:
            fused_score = rules_score
            confidence_level = "MEDIUM"
            confidence_val = 0.72
            disagreement_note = "Evaluation completed via local Heuristic & Knowledge-Base engine (AI LLM offline or bypassed)."

            if fused_score >= 65:
                verdict = "LIKELY SCAM"
                explanation = (
                    f"Warning: Multiple high-risk scam indicators detected matching known Indian fraud schemes ({rules_eval.scam_type}). "
                    "Do not transfer funds, share OTPs, or click any unverified links."
                )
                actions = FusionEngine._default_scam_actions()
            elif fused_score >= 35:
                verdict = "SUSPICIOUS"
                explanation = (
                    "This message contains ambiguous or unsolicited requests. Exercise caution before proceeding or replying."
                )
                actions = FusionEngine._default_suspicious_actions()
            else:
                verdict = "LOOKS GENUINE"
                explanation = (
                    "No prominent cyber fraud red flags found. However, always verify directly through official department websites."
                )
                actions = FusionEngine._default_genuine_actions()

            return AnalysisResponse(
                verdict=verdict,
                risk_score=fused_score,
                confidence=confidence_level,
                confidence_score=confidence_val,
                scam_type=rules_eval.scam_type or "Unknown",
                language=language,
                plain_explanation=explanation,
                what_it_really_means=None,
                red_flags=rules_eval.red_flags,
                recommended_actions=actions,
                extracted_text=extracted_text,
                input_type=input_type,
                rules_score=rules_score,
                llm_score=None,
                disagreement_warning=disagreement_note,
                media_analysis=media_analysis
            )

        # 2. Both Rules and LLM are present: Hybrid Fusion
        llm_score = llm_eval.risk_score
        score_diff = abs(rules_score - llm_score)
        
        disagreement_warning = None
        if score_diff >= 35:
            # Significant divergence
            confidence_level = "LOW"
            confidence_val = 0.58
            disagreement_warning = (
                f"Notice: Heuristic rules engine scored {rules_score}/100 while AI model scored {llm_score}/100. "
                "Because of this divergence, confidence is lowered. Exercise extra human vigilance."
            )
            # Conservative bias: lean slightly towards higher risk to protect user safety
            fused_score = round(0.4 * min(rules_score, llm_score) + 0.6 * max(rules_score, llm_score))
        elif score_diff >= 20:
            confidence_level = "MEDIUM"
            confidence_val = 0.78
            fused_score = round(0.45 * rules_score + 0.55 * llm_score)
        else:
            confidence_level = "HIGH"
            confidence_val = 0.94
            fused_score = round(0.45 * rules_score + 0.55 * llm_score)

        fused_score = max(0, min(100, fused_score))

        # Calibrate Verdict
        if fused_score >= 65:
            verdict = "LIKELY SCAM"
        elif fused_score >= 35:
            verdict = "SUSPICIOUS"
        else:
            verdict = "LOOKS GENUINE"

        # Deduplicate and combine red flags
        combined_flags = FusionEngine._merge_red_flags(rules_eval.red_flags, llm_eval.red_flags)
        
        # Actions: prefer LLM actions if present, else fallback
        actions = llm_eval.recommended_actions if llm_eval.recommended_actions else (
            FusionEngine._default_scam_actions() if verdict == "LIKELY SCAM" else (
                FusionEngine._default_suspicious_actions() if verdict == "SUSPICIOUS" else FusionEngine._default_genuine_actions()
            )
        )

        return AnalysisResponse(
            verdict=verdict,
            risk_score=fused_score,
            confidence=confidence_level,
            confidence_score=confidence_val,
            scam_type=llm_eval.scam_type or rules_eval.scam_type or "Unknown",
            language=language,
            plain_explanation=llm_eval.plain_explanation,
            what_it_really_means=llm_eval.what_it_really_means,
            red_flags=combined_flags,
            recommended_actions=actions,
            extracted_text=extracted_text,
            input_type=input_type,
            rules_score=rules_score,
            llm_score=llm_score,
            disagreement_warning=disagreement_warning,
            media_analysis=media_analysis
        )

    @staticmethod
    def _merge_red_flags(rule_flags: List[RedFlag], llm_flags: List[RedFlag]) -> List[RedFlag]:
        seen_spans = set()
        merged = []
        for rf in rule_flags + llm_flags:
            span_key = rf.text_span.strip().lower()
            if span_key and span_key not in seen_spans:
                seen_spans.add(span_key)
                merged.append(rf)
        return merged

    @staticmethod
    def _default_scam_actions() -> List[RecommendedAction]:
        return [
            RecommendedAction(
                step=1,
                title="Do Not Pay or Transfer Any Money",
                description="Immediately refuse any payment, 'verification deposit', or settlement. No Indian agency requires money to clear legal charges.",
                action_type="SAFETY"
            ),
            RecommendedAction(
                step=2,
                title="Do Not Share OTPs or Install Remote Apps",
                description="Never give any OTP, UPI PIN, or install AnyDesk/TeamViewer. If installed, immediately uninstall and disconnect from Wi-Fi.",
                action_type="SAFETY"
            ),
            RecommendedAction(
                step=3,
                title="Block and Report the Contact",
                description="Block the caller or sender on WhatsApp and mark as spam.",
                action_type="SAFETY"
            ),
            RecommendedAction(
                step=4,
                title="Dial 1930 / Report at cybercrime.gov.in",
                description="If you lost money or shared confidential details, call 1930 immediately within the golden hour to freeze fraudulent transactions.",
                action_type="REPORTING",
                link="https://cybercrime.gov.in"
            )
        ]

    @staticmethod
    def _default_suspicious_actions() -> List[RecommendedAction]:
        return [
            RecommendedAction(
                step=1,
                title="Do Not Click Links or Download Attachments",
                description="Inspect URLs carefully. Avoid opening unverified APKs or shortened URLs.",
                action_type="SAFETY"
            ),
            RecommendedAction(
                step=2,
                title="Verify Directly with the Official Organization",
                description="Call your bank or utility provider using the phone number printed on your physical card or official monthly bill.",
                action_type="VERIFICATION"
            )
        ]

    @staticmethod
    def _default_genuine_actions() -> List[RecommendedAction]:
        return [
            RecommendedAction(
                step=1,
                title="Normal Procedure",
                description="This appears to be a standard notification. No urgent payment or credential entry is demanded.",
                action_type="VERIFICATION"
            ),
            RecommendedAction(
                step=2,
                title="Keep for Records",
                description="Maintain acknowledgment or reference numbers for your tax or financial records.",
                action_type="VERIFICATION"
            )
        ]

