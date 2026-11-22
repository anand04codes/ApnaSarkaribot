"""
Gemini AI Service for Multimodal & Multilingual Cyber Scam Analysis.
Uses google-genai SDK with structured Pydantic JSON schema output.
Grounded with Indian legal realities and official cyber security advisories (RAG-lite).
"""
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from app.config import settings
from app.models.schemas import LLMEvaluation, RedFlag, RecommendedAction

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).resolve().parent.parent / "data"
        self.data_dir = data_dir
        self.knowledge = self._load_knowledge()
        self.client = None
        self._init_client()

    def _load_knowledge(self) -> Dict[str, Any]:
        filepath = self.data_dir / "knowledge_base.json"
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _init_client(self):
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            try:
                from google import genai
                self.client = genai.Client(
                    api_key=settings.GEMINI_API_KEY,
                    http_options={"api_version": "v1beta"}
                )
                logger.info("Gemini AI Client initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini Client: {e}")
                self.client = None
        else:
            self.client = None

    def is_available(self) -> bool:
        return self.client is not None

    def _build_system_instruction(self, language: str = "en") -> str:
        golden_rules = "\n- ".join(self.knowledge.get("golden_rules", []))
        
        lang_prompt = {
            "en": "Respond in simple, clear, reassuring Indian English.",
            "hi": "सरल, बोलचाल की प्रामाणिक हिंदी में उत्तर दें (शब्दानुवाद न करें)। स्पष्ट और मददगार भाषा का उपयोग करें।",
            "mr": "सोप्या आणि स्पष्ट मराठी भाषेत उत्तर द्या (शाब्दिक भाषांतर करू नका).",
            "ta": "எளிய, தெளிவான தமிழ் மொழியில் பதிலளிக்கவும் (நேரடி மொழிபெயர்ப்பு வேண்டாம்).",
            "te": "సరళమైన, స్పష్టమైన తెలుగు భాషలో సమాధానం ఇవ్వండి.",
            "bn": "সহজ, স্বাভাবিক বাংলা ভাষায় উত্তর দিন।",
            "gu": "સરળ અને સ્પષ્ટ ગુજરાતી ભાષામાં જવાબ આપો.",
            "kn": "ಸರಳ ಮತ್ತು ಸ್ಪಷ್ಟವಾದ ಕನ್ನಡ ಭಾಷೆಯಲ್ಲಿ ಉತ್ತರಿಸಿ."
        }.get(language, "Respond in simple, clear English.")

        return f"""You are SarkariSach, an expert cyber forensic and citizen protection AI for Indian citizens.
Your job is to rigorously evaluate whether a submitted SMS, WhatsApp notice, court document, police warrant, courier alert, utility warning, voice message, or link is a SCAM or GENUINE.

GROUND TRUTH INDIAN LEGAL & ADMINISTRATIVE FACTS:
- {golden_rules}

CORE RULES:
1. Verdict must be strictly one of: 'LIKELY SCAM', 'SUSPICIOUS', or 'LOOKS GENUINE'.
2. Provide a risk_score from 0 (completely safe/genuine) to 100 (extreme scam/extortion).
3. If LIKELY SCAM:
   - Identify exact text spans that act as red flags with human-friendly reasons.
   - Explain plainly why it is fake.
   - Give concrete safety steps: Do not pay, do not share OTP, call 1930, report at cybercrime.gov.in.
4. If LOOKS GENUINE:
   - Explain 'what_it_really_means': what the citizen is actually receiving (e.g. IT refund, bank debit confirmation) and what routine steps (if any) they should follow.
   - risk_score should be <= 15.
5. If the notice claims 'Digital Arrest', 'video call interrogation', or asks for 'RBI verification security deposit', it is 100% a fraudulent scam (risk_score >= 95).
6. LANGUAGE: {lang_prompt} Ensure all explanations and action steps are written in the requested language ({language}).
"""

    async def analyze_content(
        self,
        text: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        image_mime: Optional[str] = None,
        audio_bytes: Optional[bytes] = None,
        audio_mime: Optional[str] = None,
        language: str = "en"
    ) -> Optional[LLMEvaluation]:
        """
        Analyze multimodal content via Gemini. Returns structured LLMEvaluation.
        Falls back to None if API key is not present or an error occurs.
        """
        if not self.is_available():
            logger.info("Gemini API key not configured or client offline; using rules engine fallback.")
            return None

        try:
            from google.genai import types

            contents = []
            if image_bytes and image_mime:
                contents.append(
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=image_mime
                    )
                )
                prompt_text = (
                    "Inspect this screenshot or document image. Carefully read all text, seal, stamp, "
                    "headers, logos, phone numbers, and formatting. Determine if it is a genuine Indian official notice or a forgery."
                )
                if text:
                    prompt_text += f"\n\nAccompanying text: {text}"
                contents.append(prompt_text)

            elif audio_bytes and audio_mime:
                contents.append(
                    types.Part.from_bytes(
                        data=audio_bytes,
                        mime_type=audio_mime
                    )
                )
                contents.append(
                    "Listen to this audio clip or voice note. Transcribe the spoken text, check if it exhibits "
                    "scam intimidation tactics (police/customs threats, digital arrest, fake urgency, OTP demands), "
                    "and analyze whether it appears to be a real human or an AI synthetic voice."
                )

            elif text:
                contents.append(f"Analyze the following suspicious message or notification:\n\n'''{text}'''")
            else:
                return None

            system_instruction = self._build_system_instruction(language=language)

            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=LLMEvaluation,
                    temperature=0.1
                )
            )

            if response and response.text:
                data = json.loads(response.text)
                return LLMEvaluation(**data)

            return None

        except Exception as e:
            logger.error(f"Gemini API invocation error: {e}", exc_info=True)
            return None
