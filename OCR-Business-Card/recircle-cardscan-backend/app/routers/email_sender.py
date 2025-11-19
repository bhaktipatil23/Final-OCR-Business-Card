from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from app.services.email_service import email_queue, email_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["email-sender"])

class EmailRecipient(BaseModel):
    email: str
    name: str

class EmailRequest(BaseModel):
    recipients: List[EmailRecipient]
    subject: str
    body: str
    attachment_path: Optional[str] = None
    signature_path: Optional[str] = None

@router.post("/send-emails")
async def send_emails(email_request: EmailRequest, background_tasks: BackgroundTasks):
    """Add emails to queue and start processing"""
    try:
        # Prepare emails for queue
        emails = []
        for recipient in email_request.recipients:
            emails.append({
                "to_email": recipient.email,
                "to_name": recipient.name,
                "subject": email_request.subject,
                "body": email_request.body,
                "attachment_path": email_request.attachment_path,
                "signature_path": email_request.signature_path
            })
        
        # Add to queue
        batch_id, count = email_queue.add_batch(emails)
        
        # Start processing in background
        background_tasks.add_task(email_service.process_queue)
        
        return {
            "message": f"Added {count} emails to queue",
            "batch_id": batch_id,
            "count": count,
            "status": "processing_started"
        }
        
    except Exception as e:
        logger.error(f"Error adding emails to queue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/queue-status")
async def get_queue_status():
    """Get current queue status"""
    try:
        status = email_queue.get_queue_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/queue-details")
async def get_queue_details():
    """Get detailed queue information"""
    try:
        return {
            "queue": email_queue.queue,
            "status": email_queue.get_queue_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/process-queue")
async def process_queue_manually():
    """Manually trigger queue processing"""
    try:
        result = await email_service.process_queue()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")