import os
import io
import fitz
from docx import Document
import puremagic
from pathlib import Path
from .ocr_service import extract_text_from_pdf_pages, extract_text_from_image

def detect_file_type(filename: str, content_bytes: bytes) -> str:
    try:
        ext = puremagic.from_string(content_bytes)
        return ext
    except puremagic.PureError:
        return os.path.splitext(filename)[1].lower()

def extract_text_from_pdf(file_path: str) -> dict:
    doc = fitz.open(file_path)
    text_content = []
    is_scanned = True
    
    for page in doc:
        page_text = page.get_text()
        if len(page_text.strip()) > 50:
            is_scanned = False
        text_content.append(page_text)
        
    full_text = "\n".join(text_content)
    
    if is_scanned:
        # Use OCR
        pages_to_ocr = list(range(len(doc)))
        ocr_result = extract_text_from_pdf_pages(file_path, pages_to_ocr)
        return {"text": ocr_result, "ocr_used": True, "properties": {}}
    
    return {"text": full_text, "ocr_used": False, "properties": {}}

def extract_text_from_docx(file_path: str) -> dict:
    doc = Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    props = doc.core_properties
    properties = {
        "author": props.author,
        "title": props.title,
        "created": str(props.created) if props.created else None
    }
    return {"text": text, "ocr_used": False, "properties": properties}

def extract_text_from_txt(file_path: str) -> dict:
    with open(file_path, "rb") as f:
        content = f.read()
    
    import chardet
    encoding = chardet.detect(content)['encoding'] or 'utf-8'
    text = content.decode(encoding, errors='replace')
    
    return {"text": text, "ocr_used": False, "properties": {}}

def process_file(file_path: str, filename: str) -> dict:
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == ".pdf":
        result = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        result = extract_text_from_docx(file_path)
    elif ext == ".txt":
        result = extract_text_from_txt(file_path)
    elif ext in [".png", ".jpg", ".jpeg"]:
        ocr_res = extract_text_from_image(file_path)
        result = {"text": ocr_res["text"], "ocr_used": True, "properties": {}}
    else:
        raise ValueError(f"Unsupported file type: {ext}")
        
    result["file_type"] = ext
    return result
