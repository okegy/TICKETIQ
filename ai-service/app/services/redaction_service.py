import re

class RedactionService:
    @staticmethod
    def redact_text(text: str) -> str:
        if not text:
            return ""

        # 1. Email Redaction
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        redacted = re.sub(email_pattern, '[REDACTED_EMAIL]', text)

        # 2. IP Address Redaction (IPv4)
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        redacted = re.sub(ip_pattern, '[REDACTED_IP]', redacted)

        # 3. Phone Number Redaction (various formats)
        phone_pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        redacted = re.sub(phone_pattern, '[REDACTED_PHONE]', redacted)

        # 4. Bearer Tokens & API Keys
        token_pattern = r'(?i)(bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*|api[_-]?key[:=]\s*[a-zA-Z0-9_\-]+)'
        redacted = re.sub(token_pattern, '[REDACTED_TOKEN]', redacted)

        # 5. Passwords in text (e.g. password is XYZ)
        password_pattern = r'(?i)(password|passwd|pwd)\s*[:=]\s*\S+'
        redacted = re.sub(password_pattern, r'\1: [REDACTED_SECRET]', redacted)

        # 6. URLs & internal hostnames
        url_pattern = r'https?://[^\s]+'
        redacted = re.sub(url_pattern, '[REDACTED_URL]', redacted)

        return redacted
