"""
Language detection for TicketIQ multilingual intake.

Deterministic Unicode-script analysis — no ML, fully explainable:
  - Devanagari (U+0900–U+097F) → Hindi  ("hi")
  - Tamil      (U+0B80–U+0BFF) → Tamil  ("ta")
  - otherwise                  → English ("en")

Latin-script Hindi/Tamil (romanised) is out of scope for detection and
falls back to English; the analyst can always force a language explicitly.
"""

from typing import Dict

SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "en": {"name": "English", "native": "English"},
    "hi": {"name": "Hindi", "native": "हिन्दी"},
    "ta": {"name": "Tamil", "native": "தமிழ்"},
}

_SCRIPT_RANGES = (
    (0x0900, 0x097F, "hi"),  # Devanagari
    (0x0B80, 0x0BFF, "ta"),  # Tamil
)


def detect_language(text: str) -> str:
    """Return the dominant supported language of *text* ('en' | 'hi' | 'ta')."""
    if not text:
        return "en"

    counts = {"hi": 0, "ta": 0}
    for ch in text:
        code = ord(ch)
        for low, high, lang in _SCRIPT_RANGES:
            if low <= code <= high:
                counts[lang] += 1
                break

    if counts["hi"] == 0 and counts["ta"] == 0:
        return "en"
    # Tamil script is unambiguous; Devanagari could technically be Marathi etc.
    # but within TicketIQ's supported set Devanagari ⇒ Hindi.
    return "ta" if counts["ta"] > counts["hi"] else "hi"


def resolve_language(requested: str, text: str) -> str:
    """Resolve the effective language: honour explicit requests, else auto-detect."""
    requested = (requested or "auto").lower()
    if requested in SUPPORTED_LANGUAGES:
        return requested
    return detect_language(text)


def language_name(code: str) -> str:
    return SUPPORTED_LANGUAGES.get(code, SUPPORTED_LANGUAGES["en"])["name"]


def language_native(code: str) -> str:
    return SUPPORTED_LANGUAGES.get(code, SUPPORTED_LANGUAGES["en"])["native"]
