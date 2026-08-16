import re
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None

def mask_pii(text: str) -> str:
    """Anonymizes text using Regex rules and spaCy NER."""
    if not text:
        return ""

    sanitized = text

    # 1. Regex Masking (Structured Data)
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    phone_pattern = r'\b(\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b'
    date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'

    sanitized = re.sub(email_pattern, '[EMAIL_REDACTED]', sanitized)
    sanitized = re.sub(phone_pattern, '[PHONE_REDACTED]', sanitized)
    sanitized = re.sub(date_pattern, '[DATE_REDACTED]', sanitized)

    # 2. spaCy NER Masking (Names, Organizations, Locations)
    if nlp:
        doc = nlp(sanitized)
        entities = sorted(doc.ents, key=lambda e: e.start_char, reverse=True)
        for ent in entities:
            if ent.label_ == "PERSON":
                sanitized = sanitized[:ent.start_char] + "[NAME_REDACTED]" + sanitized[ent.end_char:]
            elif ent.label_ == "ORG":
                sanitized = sanitized[:ent.start_char] + "[ORG_REDACTED]" + sanitized[ent.end_char:]
            elif ent.label_ in ["GPE", "LOC"]:
                sanitized = sanitized[:ent.start_char] + "[LOCATION_REDACTED]" + sanitized[ent.end_char:]

    return sanitized