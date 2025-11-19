from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["attachments"])

UPLOAD_DIR = "./attachments"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-attachment")
async def upload_attachment(file: UploadFile = File(...)):
    """Upload attachment for email (PDF, DOC, IMG, etc.)"""
    try:
        # Validate file type - allow PDF, DOC, JPG, PNG only
        allowed_extensions = ['.pdf', '.doc', '.jpg', '.jpeg', '.png']
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(status_code=400, detail="File type not supported")
        
        # Generate unique filename
        file_id = uuid.uuid4().hex[:8]
        filename = f"{file_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"Attachment uploaded: {filename}")
        
        return {
            "message": "File uploaded successfully",
            "filename": filename,
            "file_path": file_path,
            "size": len(content)
        }
        
    except Exception as e:
        logger.error(f"Error uploading attachment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/attachments")
async def list_attachments():
    """List all uploaded attachments"""
    try:
        files = []
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                    file_path = os.path.join(UPLOAD_DIR, filename)
                    file_size = os.path.getsize(file_path)
                    files.append({
                        "filename": filename,
                        "file_path": file_path,
                        "size": file_size
                    })
        
        return {"attachments": files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing attachments: {str(e)}")