import re
from spellchecker import SpellChecker
from utils.logger import get_logger

logger = get_logger(__name__)

spell = SpellChecker()
academic_terms = [
    'crispr', 'bioinformatics', 'dataset', 'nlp', 'cnn', 'lstm', 'svm', 
    'metadata', 'ontology', 'api', 'json', 'xml', 'marc21', 'dublincore'
]
spell.word_frequency.load_words(academic_terms)

def clean_ocr_artifacts(text: str) -> str:
    text = re.sub(r'-\n\s*', '', text)
    text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def correct_spelling(text: str) -> str:
    words = spell.split_words(text)
    misspelled = spell.unknown(words)
    
    corrections_made = 0
    corrected_text = text
    
    for word in misspelled:
        correction = spell.correction(word)
        if correction and correction != word:
            corrected_text = re.sub(r'\b' + re.escape(word) + r'\b', correction, corrected_text)
            corrections_made += 1
            
    return corrected_text, corrections_made

def normalize_text(text: str) -> str:
    import unicodedata
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    return text

def process_text(text: str) -> dict:
    cleaned = clean_ocr_artifacts(text)
    normalized = normalize_text(cleaned)
    # corrected, corrections = correct_spelling(normalized)  # Can be slow, maybe skip or optimize
    corrected = normalized
    corrections = 0
    
    return {
        "corrected_text": corrected,
        "corrections_made": corrections
    }
