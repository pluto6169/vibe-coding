import os
import fitz
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from config import TESSERACT_CMD
from utils.logger import get_logger

logger = get_logger(__name__)

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def check_tesseract_installed() -> bool:
    try:
        pytesseract.get_tesseract_version()
        return True
    except pytesseract.TesseractNotFoundError:
        return False
    except Exception:
        return False

def preprocess_image(image: Image.Image) -> Image.Image:
    # Convert to grayscale
    img = image.convert('L')
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)
    return img

def extract_text_from_image(image_path_or_pil) -> dict:
    if isinstance(image_path_or_pil, str):
        img = Image.open(image_path_or_pil)
    else:
        img = image_path_or_pil

    img = preprocess_image(img)
    
    try:
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        text = pytesseract.image_to_string(img)
        
        confidences = [int(conf) for conf in data['conf'] if conf != '-1']
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {"text": text, "confidence": avg_conf}
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return {"text": "", "confidence": 0.0}

def extract_text_from_pdf_pages(pdf_path: str, page_numbers: list) -> str:
    doc = fitz.open(pdf_path)
    full_text = []
    
    for page_num in page_numbers:
        page = doc[page_num]
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        res = extract_text_from_image(img)
        full_text.append(res["text"])
        
    return "\n\n".join(full_text)
