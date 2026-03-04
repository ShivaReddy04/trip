"""Sarvam AI service — Translation + Text-to-Speech for Indian languages."""

import os
import requests

SARVAM_BASE = "https://api.sarvam.ai"

SUPPORTED_LANGUAGES = {
    "en-IN": "English",
    "hi-IN": "Hindi",
    "te-IN": "Telugu",
    "ta-IN": "Tamil",
    "kn-IN": "Kannada",
    "ml-IN": "Malayalam",
    "mr-IN": "Marathi",
    "bn-IN": "Bengali",
    "gu-IN": "Gujarati",
    "pa-IN": "Punjabi",
    "od-IN": "Odia",
}


def _sarvam_key():
    return os.getenv("sarvam", "")


def _headers():
    return {
        "api-subscription-key": _sarvam_key(),
        "Content-Type": "application/json",
    }


# ---------------------------------------------------------------------------
# Translate text
# ---------------------------------------------------------------------------

def translate_text(text, target_lang, source_lang="en-IN"):
    """
    Translate text using Sarvam AI.
    Returns translated text or None on failure.
    """
    key = _sarvam_key()
    if not key:
        return None, "Sarvam API key not configured"

    if not text or not text.strip():
        return None, "No text to translate"

    if target_lang == source_lang:
        return text, None

    # Sarvam has a 2000 char limit per request — chunk if needed
    chunks = _chunk_text(text, 1900)
    translated_parts = []

    for chunk in chunks:
        try:
            resp = requests.post(
                f"{SARVAM_BASE}/translate",
                headers=_headers(),
                json={
                    "input": chunk,
                    "source_language_code": source_lang,
                    "target_language_code": target_lang,
                    "model": "mayura:v1",
                    "mode": "formal",
                    "enable_preprocessing": True,
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            translated = data.get("translated_text", "")
            if translated:
                translated_parts.append(translated)
            else:
                translated_parts.append(chunk)
        except requests.RequestException as e:
            print(f"[WARN] Sarvam translate failed: {e}")
            return None, f"Translation failed: {str(e)}"

    return " ".join(translated_parts), None


def _chunk_text(text, max_len):
    """Split text into chunks at sentence boundaries."""
    if len(text) <= max_len:
        return [text]
    chunks = []
    current = ""
    for sentence in text.replace(". ", ".|").split("|"):
        if len(current) + len(sentence) + 1 > max_len:
            if current:
                chunks.append(current.strip())
            current = sentence
        else:
            current += " " + sentence if current else sentence
    if current.strip():
        chunks.append(current.strip())
    return chunks or [text[:max_len]]


# ---------------------------------------------------------------------------
# Text-to-Speech
# ---------------------------------------------------------------------------

def text_to_speech(text, lang="hi-IN", speaker="anushka", pace=1.0):
    """
    Convert text to speech using Sarvam AI Bulbul v2.
    Returns base64 audio string or None on failure.
    """
    key = _sarvam_key()
    if not key:
        return None, "Sarvam API key not configured"

    if not text or not text.strip():
        return None, "No text to speak"

    # Trim to 1500 chars (Bulbul v2 limit)
    text = text[:1500]

    try:
        resp = requests.post(
            f"{SARVAM_BASE}/text-to-speech",
            headers=_headers(),
            json={
                "inputs": [text],
                "target_language_code": lang,
                "model": "bulbul:v2",
                "speaker": speaker,
                "pace": pace,
                "speech_sample_rate": 22050,
                "enable_preprocessing": True,
            },
            timeout=20,
        )
        if resp.status_code != 200:
            body = resp.text
            print(f"[WARN] Sarvam TTS error {resp.status_code}: {body}")
            return None, f"Text-to-speech failed ({resp.status_code}): {body}"
        data = resp.json()
        audios = data.get("audios", [])
        if audios and audios[0]:
            return audios[0], None
        return None, "No audio in response"
    except requests.RequestException as e:
        print(f"[WARN] Sarvam TTS failed: {e}")
        return None, f"Text-to-speech failed: {str(e)}"


def get_supported_languages():
    """Return dict of supported language codes and names."""
    return SUPPORTED_LANGUAGES
