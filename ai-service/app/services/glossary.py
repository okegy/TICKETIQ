"""
Bilingual IT-term glossary — the cross-lingual retrieval "bridge".

The knowledge base and the trained dataset are English. When a ticket
arrives in Hindi or Tamil, matched glossary terms contribute their English
equivalents to the search query so TF-IDF retrieval still works.

Deterministic substring matching, longest term first; every bridge is
traceable (matched_terms is returned for UI transparency).
"""

from typing import Dict, List

# Hindi (Devanagari) and Tamil → English IT equivalents.
_GLOSSARY: Dict[str, Dict[str, str]] = {
    "hi": {
        "लॉगिन": "login log in",
        "लॉग इन": "login log in",
        "लॉगआउट": "logout",
        "पासवर्ड": "password",
        "पासवर्ड रीसेट": "password reset",
        "रीसेट": "reset",
        "खाता": "account",
        "अकाउंट": "account",
        "लॉक": "locked lockout",
        "लॉकड": "locked",
        "अनलॉक": "unlock",
        "ईमेल": "email",
        "मेल": "email mail",
        "सर्वर": "server",
        "नेटवर्क": "network",
        "वाईफाई": "wifi wireless",
        "इंटरनेट": "internet",
        "वीपीएन": "vpn",
        "प्रिंटर": "printer",
        "सॉफ्टवेयर": "software",
        "हार्डवेयर": "hardware",
        "एप्लिकेशन": "application",
        "ऐप": "application app",
        "वेबसाइट": "website",
        "ब्राउज़र": "browser",
        "त्रुटि": "error",
        "एरर": "error",
        "समस्या": "problem issue",
        "धीमा": "slow performance",
        "लटका": "hang stuck",
        "बंद": "down unavailable",
        "चल नहीं": "not running failed",
        "काम नहीं कर": "not working",
        "उपयोगकर्ता": "user users",
        "डेटा": "data",
        "रिपोर्ट": "report",
        "डैशबोर्ड": "dashboard",
        "बैकअप": "backup",
        "अपडेट": "update",
        "इंस्टॉल": "install",
        "फाइल": "file",
        "फोल्डर": "folder",
    },
    "ta": {
        "உள்நுழைவு": "login log in",
        "வெளிநுழைவு": "logout",
        "கடவுச்சொல்": "password",
        "மீட்டமை": "reset",
        "கணக்கு": "account",
        "பூட்டு": "locked lockout",
        "பூட்டப்பட்ட": "locked",
        "திற": "unlock open",
        "மின்னஞ்சல்": "email",
        "சேவையகம்": "server",
        "வலையமைப்பு": "network",
        "இணையம்": "internet",
        "அச்சுப்பொறி": "printer",
        "மென்பொருள்": "software",
        "வன்பொருள்": "hardware",
        "பயன்பாடு": "application",
        "இணையதளம்": "website",
        "உலாவி": "browser",
        "பிழை": "error",
        "சிக்கல்": "problem issue",
        "மெதுவாக": "slow performance",
        "நின்றுவிட்டது": "hang stuck",
        "இயங்கவில்லை": "not working failed",
        "பயனர்": "user users",
        "தரவு": "data",
        "அறிக்கை": "report",
        "டாஷ்போர்டு": "dashboard",
        "காப்பு": "backup",
        "புதுப்பிப்பு": "update",
        "நிறுவு": "install",
        "கோப்பு": "file",
    },
}


def bridge_terms(text: str, lang: str) -> List[str]:
    """English equivalents for every glossary term found in *text*."""
    if lang not in _GLOSSARY or not text:
        return []
    table = _GLOSSARY[lang]
    hits: List[str] = []
    for term in sorted(table, key=len, reverse=True):
        if term in text and table[term] not in hits:
            hits.append(table[term])
    return hits


def build_search_query(redacted_text: str, lang: str) -> str:
    """English retrieval query for a ticket.

    For English tickets the redacted text is used as-is. For Hindi/Tamil,
    the script tokens would dilute the TF-IDF query vector norm against the
    English corpus, so retrieval runs on the glossary bridge terms ONLY
    (pure English query). Callers should keep the original text for display.
    """
    if lang == "en":
        return redacted_text
    return " ".join(bridge_terms(redacted_text, lang)).strip()
