from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class FileUploadResponse(BaseModel):
    job_id: str
    filename: str
    file_type: str
    status: str

class ProcessingStatus(BaseModel):
    job_id: str
    progress: int  # 0-100
    stage: str
    error: Optional[str] = None

class ExtractedText(BaseModel):
    job_id: str
    text: str
    ocr_used: bool
    confidence: float
    language: str

class MetadataField(BaseModel):
    value: str
    confidence: str = 'medium'
    source: str = 'nlp'

class ExtractedMetadata(BaseModel):
    title: Optional[str] = None
    authors: List[str] = []
    abstract: Optional[str] = None
    keywords: List[str] = []
    date: Optional[str] = None
    publisher: Optional[str] = None
    journal: Optional[str] = None
    language: Optional[str] = None
    document_type: Optional[str] = None
    doi: Optional[str] = None
    format_type: Optional[str] = None

class DublinCoreRecord(BaseModel):
    title: Optional[str] = None
    creator: List[str] = []
    subject: List[str] = []
    description: Optional[str] = None
    publisher: Optional[str] = None
    contributor: List[str] = []
    date: Optional[str] = None
    type: Optional[str] = None
    format: Optional[str] = None
    identifier: Optional[str] = None
    source: Optional[str] = None
    language: Optional[str] = None
    relation: List[str] = []
    coverage: Optional[str] = None
    rights: Optional[str] = None

class Marc21Record(BaseModel):
    fields: Dict[str, Any]
    mrk_text: str
    is_draft: bool = True

class ProcessingResult(BaseModel):
    job_id: str
    extracted_text: ExtractedText
    metadata: ExtractedMetadata
    dublin_core: DublinCoreRecord
    marc21: Marc21Record
