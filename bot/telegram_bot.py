"""
SarkariSach Telegram Bot: Multi-input Citizen Cyber Protection Assistant.
Users forward suspicious SMS, WhatsApp notices, photos, or voice notes;
bot replies with verified verdict, top red flags, safety action steps, and audio playback.
"""
import io
import os
import sys
import logging
from pathlib import Path

# Add backend to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

from app.config import settings
from app.core.rules_engine import IndianScamRulesEngine
from app.core.fusion import FusionEngine
from app.core.media_authenticity import MediaAuthenticityInspector
from app.services.gemini_service import GeminiService
from app.services.tts_service import TTSService
from app.services.complaint_generator import ComplaintGenerator

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

rules_engine = IndianScamRulesEngine()
gemini_service = GeminiService()

USER_LANGUAGES = {}  # In-memory user preferences: {user_id: "hi"}

LANG_MAP = {
    "lang_hi": "hi",
    "lang_en": "en",
    "lang_mr": "mr",
    "lang_ta": "ta",
    "lang_te": "te",
    "lang_bn": "bn",
    "lang_gu": "gu",
    "lang_kn": "kn"
}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "🛡️ *Welcome to SarkariSach Citizen Cyber Defense Bot!*\n\n"
        "Forward any suspicious message, court warrant, police notice, bank alert, "
        "screenshot, or voice note to this chat.\n\n"
        "We will instantly verify:\n"
        "1. Whether it is a *SCAM* or *GENUINE*\n"
        "2. Exact legal red flags detected\n"
        "3. Clear safety actions (Don't pay, Block, Report)\n"
        "4. Voice audio reply in your chosen language\n\n"
        "📞 *National Cyber Crime Helpline: 1930*\n"
        "🌐 *Official Portal: cybercrime.gov.in*\n\n"
        "Use /language to select your language or /help for guidance."
    )
    await update.message.reply_text(welcome_msg, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_msg = (
        "ℹ️ *How to use SarkariSach Bot:*\n\n"
        "• *Forward text messages*: Simply forward SMS or WhatsApp messages here.\n"
        "• *Send a Photo*: Send a photo/screenshot of an arrest warrant or fine notice.\n"
        "• *Send a Voice Note*: Record or forward suspicious extortion voice calls.\n"
        "• */language*: Change your preferred language (Hindi, Marathi, Tamil, etc.).\n\n"
        "⚠️ *Golden Rule*: No Indian law enforcement agency (CBI, ED, Police, Narcotics) "
        "ever conducts digital arrests or video-call interrogations."
    )
    await update.message.reply_text(help_msg, parse_mode="Markdown")


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("हिन्दी (Hindi)", callback_data="lang_hi"), InlineKeyboardButton("English", callback_data="lang_en")],
        [InlineKeyboardButton("मराठी (Marathi)", callback_data="lang_mr"), InlineKeyboardButton("தமிழ் (Tamil)", callback_data="lang_ta")],
        [InlineKeyboardButton("తెలుగు (Telugu)", callback_data="lang_te"), InlineKeyboardButton("বাংলা (Bengali)", callback_data="lang_bn")],
        [InlineKeyboardButton("ગુજરાતી (Gujarati)", callback_data="lang_gu"), InlineKeyboardButton("ಕನ್ನಡ (Kannada)", callback_data="lang_kn")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🌐 *Choose your preferred language / भाषा चुनें:*", reply_markup=reply_markup, parse_mode="Markdown")


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chosen_lang = LANG_MAP.get(query.data, "en")
    user_id = query.from_user.id
    USER_LANGUAGES[user_id] = chosen_lang
    await query.edit_message_text(f"✅ Language updated to: *{chosen_lang.upper()}*.\nYou can now forward suspicious messages.", parse_mode="Markdown")


def format_bot_reply(analysis, language="en") -> str:
    verdict_emoji = "🚨" if analysis.verdict == "LIKELY SCAM" else ("⚠️" if analysis.verdict == "SUSPICIOUS" else "✅")
    
    lines = [
        f"{verdict_emoji} *VERDICT: {analysis.verdict}*",
        f"📊 *Risk Score*: {analysis.risk_score} / 100",
        f"🎯 *Category*: {analysis.scam_type}",
        f"🔍 *Confidence*: {analysis.confidence} ({int(analysis.confidence_score * 100)}%)\n",
        f"📝 *Explanation*:\n{analysis.plain_explanation}\n"
    ]

    if analysis.red_flags:
        lines.append("🚩 *Top Red Flags Found:*")
        for idx, rf in enumerate(analysis.red_flags[:3], 1):
            lines.append(f"{idx}. \"_{rf.text_span}_\" — {rf.reason}")
        lines.append("")

    if analysis.recommended_actions:
        lines.append("🛡️ *What You Must Do:*")
        for act in analysis.recommended_actions[:3]:
            lines.append(f"• *{act.title}*: {act.description}")
        lines.append("")

    lines.append("📞 *Emergency*: Dial *1930* or file at cybercrime.gov.in")
    return "\n".join(lines)


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = USER_LANGUAGES.get(user_id, "hi")
    text = update.message.text

    status_msg = await update.message.reply_text("🔍 *Analyzing with SarkariSach cyber engine...*", parse_mode="Markdown")

    try:
        rules_eval = rules_engine.evaluate(text)
        llm_eval = await gemini_service.analyze_content(text=text, language=lang)
        analysis = FusionEngine.fuse(rules_eval=rules_eval, llm_eval=llm_eval, language=lang, input_type="text")

        reply_text = format_bot_reply(analysis, language=lang)
        await status_msg.edit_text(reply_text, parse_mode="Markdown")

        # Generate audio voice reply via TTS
        try:
            audio_bytes = TTSService.generate_speech(analysis.plain_explanation, language=lang)
            await update.message.reply_voice(voice=io.BytesIO(audio_bytes), caption="🔊 Spoken Explanation / आवाज में सुनें")
        except Exception as e:
            logger.warning(f"Voice note reply skipped: {e}")

    except Exception as e:
        logger.error(f"Error analyzing text: {e}", exc_info=True)
        await status_msg.edit_text("❌ An error occurred during verification. Please try again.")


async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = USER_LANGUAGES.get(user_id, "hi")

    status_msg = await update.message.reply_text("🔍 *Inspecting document image for forgery and seals...*", parse_mode="Markdown")

    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()

        # Forensic ELA analysis
        media_resp = MediaAuthenticityInspector.inspect_image(bytes(photo_bytes))
        rules_eval = rules_engine.evaluate("[Document Image Inspection]")
        llm_eval = await gemini_service.analyze_content(image_bytes=bytes(photo_bytes), image_mime="image/jpeg", language=lang)

        analysis = FusionEngine.fuse(
            rules_eval=rules_eval,
            llm_eval=llm_eval,
            language=lang,
            input_type="image",
            media_analysis=media_resp.model_dump()
        )

        reply_text = format_bot_reply(analysis, language=lang)
        if media_resp.has_manipulation_signs:
            reply_text += f"\n\n🔬 *Forensic Note*: {media_resp.analysis_notes}"

        await status_msg.edit_text(reply_text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error analyzing photo: {e}", exc_info=True)
        await status_msg.edit_text("❌ Could not analyze photo. Please try again.")


async def handle_audio_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = USER_LANGUAGES.get(user_id, "hi")
    media = update.message.voice or update.message.audio
    if not media:
        return

    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if media.file_size and media.file_size > max_size:
        await update.message.reply_text(
            f"Audio exceeds the {settings.MAX_FILE_SIZE_MB} MB upload limit."
        )
        return

    mime_type = media.mime_type or "audio/ogg"
    if not mime_type.startswith("audio/"):
        await update.message.reply_text("Please send an audio file or voice note.")
        return

    status_msg = await update.message.reply_text(
        "🔍 *Analyzing voice note with SarkariSach cyber engine...*",
        parse_mode="Markdown"
    )

    try:
        audio_file = await media.get_file()
        audio_bytes = bytes(await audio_file.download_as_bytearray())
        if len(audio_bytes) > max_size:
            await status_msg.edit_text(
                f"Audio exceeds the {settings.MAX_FILE_SIZE_MB} MB upload limit."
            )
            return

        filename = getattr(media, "file_name", None) or "voice.ogg"
        caption = update.message.caption or ""
        media_analysis = MediaAuthenticityInspector.inspect_audio(audio_bytes, filename)
        rules_eval = rules_engine.evaluate(caption or "[Voice Recording / Audio Notice]")
        llm_eval = await gemini_service.analyze_content(
            text=caption or None,
            audio_bytes=audio_bytes,
            audio_mime=mime_type,
            language=lang
        )
        analysis = FusionEngine.fuse(
            rules_eval=rules_eval,
            llm_eval=llm_eval,
            language=lang,
            input_type="audio",
            extracted_text=caption or "[Voice Recording / Audio Notice]",
            media_analysis=media_analysis.model_dump()
        )
        await status_msg.edit_text(
            format_bot_reply(analysis, language=lang),
            parse_mode="Markdown"
        )

        try:
            speech = TTSService.generate_speech(analysis.plain_explanation, language=lang)
            await update.message.reply_voice(
                voice=io.BytesIO(speech),
                caption="🔊 Spoken Explanation / आवाज में सुनें"
            )
        except Exception as e:
            logger.warning(f"Voice note reply skipped: {e}")

    except Exception as e:
        logger.error(f"Error analyzing voice note: {e}", exc_info=True)
        await status_msg.edit_text("❌ Could not analyze voice note. Please try again.")


def run_bot():
    token = settings.TELEGRAM_BOT_TOKEN
    if not token or token == "":
        print("TELEGRAM_BOT_TOKEN is not set in .env. Bot server is ready once a token is configured.")
        return

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(CallbackQueryHandler(language_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo_message))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_audio_message))

    print("SarkariSach Telegram Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    run_bot()
