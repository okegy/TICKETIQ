from fastapi.testclient import TestClient
from app.main import app
from app.services.language_service import detect_language, resolve_language
from app.services.glossary import bridge_terms, build_search_query
from app.services.localization import localized

client = TestClient(app)


# ── Language detection ────────────────────────────────────────────

def test_detect_english():
    assert detect_language("User cannot log in, account locked after failed attempts") == "en"

def test_detect_hindi():
    assert detect_language("उपयोगकर्ता लॉगिन नहीं कर पा रहा, खाता लॉक हो गया है") == "hi"

def test_detect_tamil():
    assert detect_language("பயனர் உள்நுழைய முடியவில்லை, கணக்கு பூட்டப்பட்டது") == "ta"

def test_detect_empty_is_english():
    assert detect_language("") == "en"

def test_resolve_forced_language_wins():
    assert resolve_language("hi", "plain english text") == "hi"
    assert resolve_language("auto", "தமிழ் உரை") == "ta"


# ── Glossary bridge ───────────────────────────────────────────────

def test_glossary_bridges_hindi_terms():
    hits = bridge_terms("खाता लॉक हो गया, पासवर्ड रीसेट करें", "hi")
    assert any("account" in h for h in hits)
    assert any("password" in h for h in hits)

def test_glossary_bridges_tamil_terms():
    hits = bridge_terms("கணக்கு பூட்டப்பட்டது, கடவுச்சொல் மீட்டமைக்கவும்", "ta")
    assert any("account" in h for h in hits)
    assert any("password" in h for h in hits)

def test_bridge_query_english_is_unchanged():
    q = "account locked after failed logins"
    assert build_search_query(q, "en") == q

def test_bridge_query_appends_english_terms():
    q = build_search_query("खाता लॉक", "hi")
    assert "account" in q and "lockout" in q


# ── Localized strings ─────────────────────────────────────────────

def test_localized_tables_complete():
    for lang in ("en", "hi", "ta"):
        table = localized(lang)
        for key in ("draftAllowed", "noReliableMatch", "escalationSuggestion", "sanitizedNote"):
            assert table.get(key), f"{lang}.{key} missing"


# ── Analyze endpoint (multilingual) ───────────────────────────────

def test_analyze_hindi_returns_language_and_localized():
    payload = {
        "ticketId": "INC-HI-1",
        "ticketText": "उपयोगकर्ता लॉगिन नहीं कर पा रहा, खाता लॉक हो गया है। संपर्क: admin@corp.com",
        "confidenceThreshold": 0.1,
    }
    r = client.post("/ai/analyze-ticket", json=payload)
    assert r.status_code == 200
    d = r.json()
    assert d["language"]["code"] == "hi"
    assert d["language"]["native"] == "हिन्दी"
    assert d["localized"]["detectedLanguageLabel"]  # localized label present
    assert "[REDACTED_EMAIL]" in d["redactedText"]

def test_analyze_tamil_forced_language():
    payload = {
        "ticketId": "INC-TA-1",
        "ticketText": "கணக்கு பூட்டப்பட்டது, பயனர் உள்நுழைய முடியவில்லை",
        "language": "ta",
        "confidenceThreshold": 0.1,
    }
    r = client.post("/ai/analyze-ticket", json=payload)
    assert r.status_code == 200
    d = r.json()
    assert d["language"]["code"] == "ta"
    assert d["language"]["requested"] == "ta"

def test_analyze_english_still_works_and_has_dataset_signal():
    payload = {
        "ticketId": "INC-EN-1",
        "ticketText": "User cannot log in, account locked after too many failed login attempts",
        "confidenceThreshold": 0.1,
    }
    r = client.post("/ai/analyze-ticket", json=payload)
    assert r.status_code == 200
    d = r.json()
    assert d["decision"] == "DRAFT_ALLOWED"
    assert d["language"]["code"] == "en"
    assert "datasetSignal" in d
    assert d["datasetSignal"]["queue"], "dataset queue signal should be populated"


# ── Languages endpoint ────────────────────────────────────────────

def test_languages_endpoint():
    r = client.get("/ai/languages")
    assert r.status_code == 200
    codes = [l["code"] for l in r.json()["languages"]]
    assert codes == ["en", "hi", "ta"]
