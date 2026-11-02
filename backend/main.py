import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from config import UPLOAD_DIR, TESSERACT_CMD
from utils.logger import get_logger
from services.ocr_service import check_tesseract_installed
from routers import upload, process, export

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting MetaScholar API...")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    if not check_tesseract_installed():
        logger.warning(f"Tesseract OCR not found or not working. Make sure it is installed and TESSERACT_CMD is correct ({TESSERACT_CMD}).")
    else:
        logger.info("Tesseract OCR is available.")
        
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title='MetaScholar API', 
    description='Academic Article Metadata Extractor',
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(process.router, prefix="/api/process", tags=["Process"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])

# Mount frontend if exists
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists() and frontend_dist.is_dir():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if not full_path.startswith("api"):
            index_path = frontend_dist / "index.html"
            if index_path.exists():
                return FileResponse(index_path)
        return {"detail": "Not Found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
