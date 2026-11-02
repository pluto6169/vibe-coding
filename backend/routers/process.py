from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from routers.upload import job_store
from services.file_processor import process_file
from services.language_detector import detect_language
from services.text_corrector import process_text
from services.metadata_extractor import extract_metadata
from services.dublin_core import generate_dublin_core_json, generate_dublin_core_xml
from services.marc21 import generate_marc21_json, generate_marc21_mrk
from models.schemas import ExtractedText, DublinCoreRecord, Marc21Record

router = APIRouter()

class TextUpdate(BaseModel):
    text: str

class MetadataUpdate(BaseModel):
    title: str = None
    authors: list = None
    abstract: str = None
    keywords: list = None
    date: str = None
    publisher: str = None

@router.post("/{job_id}")
def process_document(job_id: str):
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job = job_store[job_id]
    file_path = job["file_path"]
    filename = job["filename"]
    
    try:
        # Extract text
        job["status"] = "extracting_text"
        job["progress"] = 20
        extracted = process_file(file_path, filename)
        raw_text = extracted["text"]
        
        # Clean text
        job["status"] = "cleaning_text"
        job["progress"] = 40
        clean_res = process_text(raw_text)
        text = clean_res["corrected_text"]
        
        # Detect lang & Verify English (Requirement #2)
        job["status"] = "detecting_language"
        job["progress"] = 50
        lang_res = detect_language(text)
        
        if not lang_res.get("is_english", False):
            job["status"] = "rejected"
            job["progress"] = 0
            reason = f"Document language detected as '{lang_res.get('language_code', 'unknown')}'. Only English articles are supported."
            job["error"] = reason
            raise HTTPException(
                status_code=400, 
                detail=f"File rejected: {reason}"
            )
            
        ext_text = ExtractedText(
            job_id=job_id,
            text=text,
            ocr_used=extracted["ocr_used"],
            confidence=extracted.get("confidence", 1.0),
            language=lang_res["language_code"]
        )
        job["extracted_text"] = ext_text
        
        # Extract metadata
        job["status"] = "extracting_metadata"
        job["progress"] = 70
        metadata = extract_metadata(text, extracted.get("properties"))
        metadata.language = lang_res["language_code"]
        job["metadata"] = metadata
        
        # Generate records
        job["status"] = "generating_records"
        job["progress"] = 90
        
        file_info = {"format": extracted.get("file_type")}
        dc_json = generate_dublin_core_json(metadata, file_info)
        dc_record = DublinCoreRecord(**dc_json)
        job["dublin_core"] = dc_record
        job["dublin_core_xml"] = generate_dublin_core_xml(metadata, file_info)
        
        m21_json = generate_marc21_json(metadata)
        m21_mrk = generate_marc21_mrk(metadata)
        m21_record = Marc21Record(fields=m21_json, mrk_text=m21_mrk)
        job["marc21"] = m21_record
        
        job["status"] = "completed"
        job["progress"] = 100
        
        return {
            "status": "success",
            "job_id": job_id,
            "filename": filename,
            "file_type": extracted.get("file_type", ""),
            "extracted_text": text,
            "ocr_used": extracted["ocr_used"],
            "confidence": extracted.get("confidence", 100.0),
            "language": lang_res["language_code"],
            "metadata": metadata.dict(),
            "dublin_core": dc_record.dict(),
            "dublin_core_xml": job["dublin_core_xml"],
            "marc21": m21_record.dict(),
            "marc21_mrk": m21_mrk
        }
        
    except HTTPException:
        raise
    except Exception as e:
        job["status"] = "failed"
        job["error"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{job_id}/text")
def update_text(job_id: str, update: TextUpdate):
    if job_id not in job_store or "extracted_text" not in job_store[job_id]:
        raise HTTPException(status_code=404, detail="Job or text not found")
        
    job = job_store[job_id]
    job["extracted_text"].text = update.text
    
    # Re-extract metadata with updated text
    metadata = extract_metadata(update.text)
    job["metadata"] = metadata
    
    # Re-generate records
    file_info = {"format": job["extracted_text"].language}
    job["dublin_core_xml"] = generate_dublin_core_xml(metadata, file_info)
    m21_json = generate_marc21_json(metadata)
    m21_mrk = generate_marc21_mrk(metadata)
    job["marc21"] = Marc21Record(fields=m21_json, mrk_text=m21_mrk)
    
    return {
        "status": "success",
        "job_id": job_id,
        "filename": job["filename"],
        "extracted_text": update.text,
        "ocr_used": job["extracted_text"].ocr_used,
        "confidence": job["extracted_text"].confidence,
        "language": job["extracted_text"].language,
        "metadata": metadata.dict(),
        "dublin_core_xml": job["dublin_core_xml"],
        "marc21_mrk": m21_mrk
    }

@router.get("/{job_id}/metadata")
def get_metadata(job_id: str):
    if job_id not in job_store or "metadata" not in job_store[job_id]:
        raise HTTPException(status_code=404, detail="Metadata not found")
    return job_store[job_id]["metadata"]

@router.put("/{job_id}/metadata")
def update_metadata(job_id: str, update: MetadataUpdate):
    if job_id not in job_store or "metadata" not in job_store[job_id]:
        raise HTTPException(status_code=404, detail="Metadata not found")
        
    job = job_store[job_id]
    meta = job["metadata"]
    
    for k, v in update.dict(exclude_unset=True).items():
        if v is not None:
            setattr(meta, k, v)
        
    # Re-generate
    file_info = {"format": ""}
    job["dublin_core_xml"] = generate_dublin_core_xml(meta, file_info)
    m21_json = generate_marc21_json(meta)
    m21_mrk = generate_marc21_mrk(meta)
    job["marc21"] = Marc21Record(fields=m21_json, mrk_text=m21_mrk)
    
    return {
        "status": "success",
        "job_id": job_id,
        "filename": job["filename"],
        "metadata": meta.dict(),
        "dublin_core_xml": job["dublin_core_xml"],
        "marc21_mrk": m21_mrk
    }
