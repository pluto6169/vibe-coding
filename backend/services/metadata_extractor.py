import spacy
import re
from models.schemas import ExtractedMetadata
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

def extract_metadata(text: str, file_metadata: dict = None) -> ExtractedMetadata:
    doc = nlp(text[:10000])  # Process first 10k chars for performance
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # 1. Title Extraction
    title = None
    header_skip_patterns = [r'^arxiv:', r'^doi:', r'^volume', r'^issn', r'^http', r'^\d+$', r'^page \d+']
    for line in lines[:15]:
        if any(re.search(pat, line.lower()) for pat in header_skip_patterns):
            continue
        line_clean = re.sub(r'^(?:title|article title|paper title)[\s\:]+', '', line, flags=re.IGNORECASE).strip()
        if len(line_clean) > 5 and len(line_clean) < 250:
            title = line_clean
            break
            
    # 2. Authors Extraction
    authors = []
    # Method A: spaCy PERSON entities from the first 3000 chars
    top_doc = nlp(text[:3000])
    stop_names = {'abstract', 'university', 'department', 'email', 'journal', 'vol', 'deep learning', 'machine learning', 'introduction', 'keywords'}
    for ent in top_doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text.strip()
            if len(name) > 3 and not re.search(r'\d', name) and name.lower() not in stop_names and name not in authors:
                if not any(stop in name.lower() for stop in stop_names):
                    authors.append(name)
                    
    # Method B: Regex for author line patterns like "Authors: John Doe and Jane Smith"
    if not authors:
        by_match = re.search(r'(?i)(?:by|authors?[:\s]+)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+(?:\s*(?:,|and|&)\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)*)', text[:2000])
        if by_match:
            raw_authors = re.split(r'\s*(?:,|and|&)\s*', by_match.group(1))
            for a in raw_authors:
                a_clean = a.strip()
                if len(a_clean) > 3 and a_clean.lower() not in stop_names and a_clean not in authors:
                    authors.append(a_clean)
                    
    # 3. Abstract Extraction
    abstract = None
    abs_match = re.search(r'(?i)\babstract\b[\s\:\-\—\.\n]+(.*?)(?=\b(?:keywords|key words|index terms|introduction|published|1\.|1\s+[A-Z])\b)', text, re.DOTALL)
    if abs_match:
        abstract = re.sub(r'\s+', ' ', abs_match.group(1)).strip()
    else:
        for para in text.split('\n\n')[:5]:
            p_clean = para.strip()
            if len(p_clean) > 150 and not p_clean.startswith('http'):
                abstract = p_clean[:800]
                break
                
    # 4. Keywords Extraction
    keywords = []
    kw_match = re.search(r'(?i)(?:keywords|key words|index terms)[\s\:\-\—]+(.*?)(?:\n|$|\b(?:published|doi|publisher|journal|introduction)\b)', text)
    if kw_match:
        kw_text = kw_match.group(1).strip()
        keywords = [k.strip().strip('.') for k in re.split(r'[,;•|]', kw_text) if len(k.strip()) > 1]
        
    # 5. Date/Year Extraction
    date = None
    # Look for publication date hints
    date_match = re.search(r'(?i)(?:published|received|accepted|date|year)[\s\:]+.*?(\b(?:19|20)\d{2}\b)', text[:4000])
    if date_match:
        date = date_match.group(1)
    else:
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', text[:3000])
        if year_match:
            date = year_match.group(1)
            
    # 6. Publisher/Journal Extraction
    publisher = None
    journal = None
    known_publishers = ['IEEE', 'ACM', 'Springer', 'Elsevier', 'Nature', 'Science', 'Wiley', 'Oxford University Press', 'Cambridge University Press', 'MDPI', 'PLOS', 'arXiv']
    for pub in known_publishers:
        if re.search(r'\b' + re.escape(pub) + r'\b', text[:3000], re.IGNORECASE):
            publisher = pub
            break
            
    for ent in top_doc.ents:
        if ent.label_ == "ORG" and 'journal' in ent.text.lower():
            journal = ent.text.strip()
            break
            
    # 7. Document Type
    doc_type = 'Article'
    text_lower = text[:5000].lower()
    if 'thesis' in text_lower or 'dissertation' in text_lower:
        doc_type = 'Thesis'
    elif 'report' in text_lower or 'tech report' in text_lower:
        doc_type = 'Report'
    elif 'conference' in text_lower or 'proceedings' in text_lower or 'symposium' in text_lower:
        doc_type = 'Conference Paper'
    elif 'review' in text_lower or 'survey' in text_lower:
        doc_type = 'Review Article'
        
    # 8. DOI Extraction
    doi = None
    doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+', text)
    if doi_match:
        doi = doi_match.group(0).rstrip('.')
        
    metadata = ExtractedMetadata(
        title=title or "Untitled Document",
        authors=authors,
        abstract=abstract,
        keywords=keywords,
        date=date,
        publisher=publisher,
        journal=journal,
        document_type=doc_type,
        doi=doi,
        language="en"
    )
    
    if file_metadata:
        metadata = merge_metadata(metadata, file_metadata)
        
    return metadata

def merge_metadata(nlp_meta: ExtractedMetadata, file_meta: dict) -> ExtractedMetadata:
    if file_meta.get("title") and not nlp_meta.title:
        nlp_meta.title = file_meta["title"]
    if file_meta.get("author") and not nlp_meta.authors:
        nlp_meta.authors = [file_meta["author"]]
    if file_meta.get("created") and not nlp_meta.date:
        nlp_meta.date = file_meta["created"]
    return nlp_meta
