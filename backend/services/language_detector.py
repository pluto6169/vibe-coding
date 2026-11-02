from langdetect import detect_langs, DetectorFactory
from utils.logger import get_logger

logger = get_logger(__name__)
DetectorFactory.seed = 0

def detect_language(text: str) -> dict:
    sample_text = text[:1500]
    if not sample_text.strip():
        return {"language_code": "unknown", "language_name": "Unknown", "confidence": 0.0, "is_english": False}
        
    try:
        langs = detect_langs(sample_text)
        if langs:
            top_lang = langs[0]
            lang_code = top_lang.lang
            confidence = top_lang.prob
            return {
                "language_code": lang_code,
                "language_name": lang_code, # Map properly if needed
                "confidence": confidence,
                "is_english": lang_code == "en"
            }
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        
    return {"language_code": "unknown", "language_name": "Unknown", "confidence": 0.0, "is_english": False}
