import os
import urllib.request
import json
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

from app.services.language_service import (
    resolve_language, language_name, SUPPORTED_LANGUAGES,
)

router = APIRouter()

KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
KIMI_URL = "https://api.moonshot.ai/v1/chat/completions"

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    avatar: str = "Atlas"  # 'Atlas' | 'Nova' | 'Spark'
    message: str
    history: Optional[List[ChatMessage]] = []
    language: str = "auto"  # 'auto' | 'en' | 'hi' | 'ta'

AVATAR_PERSONAS = {
    "Atlas": "You are Atlas, a Senior IT Architect assistant in TicketIQ. You speak with calm technical authority, cite KB articles when applicable, and guide analysts through incident diagnostics.",
    "Nova": "You are Nova, an enthusiastic AI Operations Guide in TicketIQ. You help users navigate the TicketIQ Command Center, explain confidence meters, refusal gates, and PII shields.",
    "Spark": "You are Spark, a snappy, energetic IT Triage specialist. You provide concise, quick tips, keyboard shortcuts, and immediate troubleshooting actions."
}

# Localized fallback replies for when the Kimi API is unreachable.
FALLBACK_STRINGS = {
    "hi": {
        "greeting": "नमस्ते! मैं {avatar} हूँ, आपका TicketIQ सहायक। मैं टिकट निदान, ज्ञान-आधार लेख (KB-01 से KB-12), विश्वास मीट्रिक और टिकट अनुमोदन में सहायता कर सकता हूँ।",
        "lockout": "[{avatar}]: अकाउंट लॉकआउट के लिए KB-01 देखें। 5 विफल प्रयासों के बाद लॉकआउट नीति लागू होती है। चरण: 1) एडमिन कंसोल > Users में उपयोगकर्ता आईडी खोजें। 2) Unlock Account पर क्लिक करें। 3) यदि आवश्यक हो तो उपयोगकर्ता से पासवर्ड रीसेट करवाएँ। 1 घंटे में दोहराए जाने पर सुरक्षा टीम को अग्रेषित करें।",
        "sso": "[{avatar}]: SSO लॉगिन लूप या समाप्त टोकन के लिए KB-03 देखें। सेशन कुकीज़ साफ़ करें, आइडेंटिटी प्रोवाइडर का क्लॉक स्कू जांचें, फिर दोबारा साइन इन करें।",
        "batch": "[{avatar}]: रात के बैच जॉब की विफलता के लिए KB-06 देखें। फेल हुआ चरण जर्नल से जांचें और उसके बाद ही फिर से चलाएँ।",
        "refusal": "[{avatar}]: TicketIQ एक सबूत-आधारित निर्णय द्वार (Evidence Decision Gate) उपयोग करता है। यदि समानता स्कोर सीमा से नीचे है, तो सिस्टम NO_RELIABLE_MATCH देता है — यानी बिना सबूत कोई समाधान नहीं गढ़ा जाता।",
        "generic": "[{avatar}]: मैं आपका TicketIQ सहायक हूँ। घटना निदान, ज्ञान-आधार लेख (KB-01 से KB-12), विश्वास मीट्रिक, या टिकट अनुमोदन के बारे में पूछें।",
    },
    "ta": {
        "greeting": "வணக்கம்! நான் {avatar}, உங்கள் TicketIQ உதவியாளர். டிக்கெட் நோயறிதல், அறிவுத் தள கட்டுரைகள் (KB-01 முதல் KB-12), நம்பிக்கை அளவீடுகள் மற்றும் டிக்கெட் ஒப்புதலில் உதவ முடியும்.",
        "lockout": "[{avatar}]: கணக்கு பூட்டுதலுக்கு KB-01 ஐப் பார்க்கவும். 5 தோல்வி முயற்சிகளுக்குப் பிறகு பூட்டுதல் கொள்கை செயல்படுகிறது. படிகள்: 1) நிர்வாக கன்சோல் > Users-இல் பயனர் ஐடியைத் தேடவும். 2) Unlock Account-ஐக் கிளிக் செய்யவும். 3) தேவைப்பட்டால் கடவுச்சொல்லை மீட்டமைக்கச் சொல்லவும். ஒரு மணி நேரத்திற்குள் மீண்டும் நடந்தால் பாதுகாப்பு குழுவிற்கு முன்னேற்றவும்.",
        "sso": "[{avatar}]: SSO உள்நுழைவு சுழற்சி அல்லது காலாவதியான டோக்கனுக்கு KB-03 ஐப் பார்க்கவும். செஷன் குக்கீகளை அழித்து, ஐடென்டிட்டி ப்ரொவைடர் க்ளாக்கைச் சரிபார்த்து, மீண்டும் உள்நுழையவும்.",
        "batch": "[{avatar}]: இரவு பேட்ச் ஜாப் தோல்விக்கு KB-06 ஐப் பார்க்கவும். தோல்வியுற்ற படியை ஜர்னலில் சரிபார்த்து, அதன்பிறகே மீண்டும் இயக்கவும்.",
        "refusal": "[{avatar}]: TicketIQ ஆதார-அடிப்படையிலான முடிவு கதவை (Evidence Decision Gate) பயன்படுத்துகிறது. ஒற்றுமை மதிப்பெண் வரம்பிற்குக் கீழே இருந்தால் NO_RELIABLE_MATCH வழங்கப்படும் — ஆதாரமின்றி எந்த தீர்வும் கற்பனையாக்கப்படாது.",
        "generic": "[{avatar}]: நான் உங்கள் TicketIQ உதவியாளர். சம்பவ நோயறிதல், அறிவுத் தள கட்டுரைகள் (KB-01 முதல் KB-12), நம்பிக்கை அளவீடுகள் அல்லது டிக்கெட் ஒப்புதல் பற்றி கேளுங்கள்.",
    },
}

def _localized_fallback(avatar: str, message: str, lang: str) -> str | None:
    """Return a localized domain fallback for hi/ta, or None to use English."""
    table = FALLBACK_STRINGS.get(lang)
    if not table:
        return None
    msg = message.lower()
    if any(k in msg for k in ("locked", "lockout", "login", "password", "लॉग", "पासवर्ड", "खाता", "உள்நுழை", "கடவுச்", "கணக்கு")):
        return table["lockout"].format(avatar=avatar)
    if "sso" in msg or "token" in msg or "loop" in msg or "சுழற்சி" in msg:
        return table["sso"].format(avatar=avatar)
    if "batch" in msg or "job" in msg or "बैच" in msg or "பேட்ச்" in msg:
        return table["batch"].format(avatar=avatar)
    if "refus" in msg or "no match" in msg or "why" in msg or "क्यों" in msg or "ஏன்" in msg:
        return table["refusal"].format(avatar=avatar)
    return table["generic"].format(avatar=avatar)

def get_fallback_response(avatar: str, message: str) -> str:
    msg_lower = message.lower()

    if "locked" in msg_lower or "lockout" in msg_lower or "failed login" in msg_lower:
        return (f"[{avatar}]: For account lockout, check KB-01. "
                "The lockout policy triggers after 5 failed attempts. "
                "Steps: 1) Open admin console > Users and search the user ID. 2) Click Unlock Account. "
                "3) Ask the user to reset the password if forgotten. "
                "Escalate to the Security team if lockouts repeat within 1 hour.")

    if "password reset" in msg_lower or "reset email" in msg_lower:
        return (f"[{avatar}]: For a password-reset email that never arrives, refer to KB-02. "
                "Check spam/junk folders, verify the user's directory mail attribute, "
                "then trigger a manual reset token from the identity console.")

    if "sso" in msg_lower or "login loop" in msg_lower or "token" in msg_lower:
        return (f"[{avatar}]: For an SSO login loop or expired token, refer to KB-03. "
                "Clear the session cookies, confirm the identity provider clock skew, and retry sign-in.")

    if "slow" in msg_lower or "cpu" in msg_lower or "performance" in msg_lower:
        return (f"[{avatar}]: For slow report pages (KB-04) or high CPU on the application server (KB-05), "
                "start with the latency metrics dashboard, identify the slow query or hot process, "
                "and compare against the baseline documented in the runbook.")

    if "batch" in msg_lower or "job failed" in msg_lower or "scheduler" in msg_lower:
        return (f"[{avatar}]: For a failed nightly batch job, refer to KB-06 (job failure) or KB-07 (job hang). "
                "Re-run only after checking the job log for the failing step; never restart a hung job without capturing its thread dump.")

    if "api" in msg_lower or "503" in msg_lower or "timeout" in msg_lower or "interface" in msg_lower:
        return (f"[{avatar}]: For partner API 503/timeout errors, refer to KB-08; for rejected interface files, KB-09. "
                "Confirm endpoint health and payload format against the partner specification before retrying.")

    if "duplicate" in msg_lower or "missing data" in msg_lower or "export" in msg_lower or "dashboard" in msg_lower:
        return (f"[{avatar}]: For data issues, see KB-10 (duplicate records after load), KB-11 (missing dashboard data), "
                "or KB-12 (blank PDF export). Validate the source extract before re-running the pipeline.")

    if "decision" in msg_lower or "refusal" in msg_lower or "no match" in msg_lower or "why" in msg_lower:
        return (f"[{avatar}]: TicketIQ uses an Evidence Decision Gate. If the retrieval similarity score is below the "
                "configured threshold, the system outputs NO_RELIABLE_MATCH. "
                "This prevents AI hallucinations and ensures all advice is 100% grounded in approved runbooks!")

    if "clerk" in msg_lower or "sign in" in msg_lower or "auth" in msg_lower:
        return (f"[{avatar}]: Authentication is powered by Clerk! You can use the Sign In / Profile button in the top navigation bar to manage your analyst session.")

    return (f"[{avatar}]: I am your TicketIQ agentic copilot. I can help you understand incident diagnoses, "
            "inspect grounded Knowledge Base articles (KB-01 to KB-12: Access, Performance, Batch, Interface, and Data runbooks), "
            "explain confidence metrics, or guide you through ticket approvals. "
            "Try asking: 'How do I resolve an account lockout?' or 'Explain the refusal gate'.")

@router.post("/chat")
async def chat_with_assistant(req: ChatRequest):
    lang = resolve_language(req.language, req.message)
    lang_display = SUPPORTED_LANGUAGES[lang]["native"]
    persona = AVATAR_PERSONAS.get(req.avatar, AVATAR_PERSONAS["Atlas"])

    system_prompt = persona
    if lang != "en":
        system_prompt += (
            f" The analyst is writing in {language_name(lang)} ({lang_display}). "
            f"Always reply in {language_name(lang)} using its native script. "
            "Keep technical terms, error codes, and KB article IDs (e.g. KB-01) in English."
        )

    messages = [{"role": "system", "content": system_prompt}]
    for h in req.history[-4:]:
        messages.append({"role": h.role, "content": h.content})
    messages.append({"role": "user", "content": req.message})

    # Try Kimi / Moonshot API
    try:
        headers = {
            "Authorization": f"Bearer {KIMI_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "TicketIQ-Agent/1.0"
        }
        data = {
            "model": "moonshot-v1-8k",
            "messages": messages,
            "temperature": 0.4
        }
        req_obj = urllib.request.Request(KIMI_URL, data=json.dumps(data).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req_obj, timeout=6) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            reply = res_data["choices"][0]["message"]["content"]
            return {"reply": reply, "source": "kimi-moonshot", "avatar": req.avatar, "language": lang}
    except Exception as e:
        # Fallback to local TicketIQ Domain Assistant (English) or localized strings
        reply = _localized_fallback(req.avatar, req.message, lang)
        if reply is None:
            reply = get_fallback_response(req.avatar, req.message)
        return {
            "reply": reply,
            "source": "ticketiq-local-agent",
            "avatar": req.avatar,
            "language": lang,
            "note": "Kimi Moonshot unreachable or KIMI_API_KEY not configured; fallback domain agent active."
        }
