import uuid
import os
import shutil
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import FileUploadResponse, ProcessingStatus
from config import UPLOAD_DIR, ALLOWED_EXTENSIONS

router = APIRouter()
job_store = {}

@router.post("/upload", response_model=List[FileUploadResponse])
async def upload_files(files: List[UploadFile] = File(...)):
    responses = []
    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            continue
            
        job_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{job_id}{ext}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        job_store[job_id] = {
            "status": "uploaded",
            "progress": 0,
            "filename": file.filename,
            "file_path": str(file_path)
        }
        
        responses.append(FileUploadResponse(
            job_id=job_id,
            filename=file.filename,
            file_type=ext,
            status="uploaded"
        ))
    return responses

@router.get("/upload/{job_id}/status", response_model=ProcessingStatus)
def get_upload_status(job_id: str):
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")
    job = job_store[job_id]
    return ProcessingStatus(
        job_id=job_id,
        progress=job.get("progress", 0),
        stage=job.get("status", "unknown"),
        error=job.get("error")
    )
