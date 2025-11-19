import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from typing import List, Dict, Optional
import logging
from datetime import datetime
import uuid
import os

logger = logging.getLogger(__name__)

class EmailQueue:
    def __init__(self):
        self.queue = []
        self.processing = False
    
    def add_batch(self, emails: List[Dict]):
        """Add a batch of emails to queue"""
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        for email in emails:
            email_item = {
                "id": f"email_{uuid.uuid4().hex[:8]}",
                "batch_id": batch_id,
                "to_email": email["to_email"],
                "to_name": email["to_name"],
                "subject": email["subject"],
                "body": email["body"],
                "attachment_path": email.get("attachment_path"),
                "signature_path": email.get("signature_path"),
                "status": "queued",
                "created_at": datetime.now(),
                "attempts": 0
            }
            self.queue.append(email_item)
        
        return batch_id, len(emails)
    
    def get_next_email(self):
        """Get next email from queue"""
        for email in self.queue:
            if email["status"] == "queued":
                return email
        return None
    
    def mark_sent(self, email_id: str):
        """Mark email as sent"""
        for email in self.queue:
            if email["id"] == email_id:
                email["status"] = "sent"
                email["sent_at"] = datetime.now()
                break
    
    def mark_failed(self, email_id: str, error: str):
        """Mark email as failed"""
        for email in self.queue:
            if email["id"] == email_id:
                email["status"] = "failed"
                email["error"] = error
                email["attempts"] += 1
                break
    
    def get_queue_status(self):
        """Get queue statistics"""
        total = len(self.queue)
        queued = len([e for e in self.queue if e["status"] == "queued"])
        sent = len([e for e in self.queue if e["status"] == "sent"])
        failed = len([e for e in self.queue if e["status"] == "failed"])
        
        return {
            "total": total,
            "queued": queued,
            "sent": sent,
            "failed": failed,
            "processing": self.processing
        }

# Global email queue
email_queue = EmailQueue()

class SMTPEmailService:
    def __init__(self):
        import os
        from dotenv import load_dotenv
        load_dotenv("../../.env")
        
        # SMTP Configuration from environment
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME', 'your_email@gmail.com')
        self.smtp_password = os.getenv('SMTP_PASSWORD', 'your_app_password')
        self.from_email = os.getenv('FROM_EMAIL', 'your_email@gmail.com')
        self.from_name = os.getenv('FROM_NAME', 'ReCircle Team')
        
        # Log SMTP configuration (without password)
        logger.info(f"🔧 SMTP CONFIG - Server: {self.smtp_server}:{self.smtp_port}, Username: {self.smtp_username}, From: {self.from_email}")
    
    def send_single_email(self, to_email: str, to_name: str, subject: str, body: str, attachment_path: Optional[str] = None, signature_path: Optional[str] = None):
        """Send a single email via SMTP with optional attachment and inline signature"""
        try:
            # Validate SMTP credentials
            if self.smtp_username == 'your_email@gmail.com' or self.smtp_password == 'your_app_password':
                logger.error("❌ SMTP CREDENTIALS NOT CONFIGURED - Please update .env file with real email credentials")
                return False, "SMTP credentials not configured"
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email  # Use only the email address, not name format
            msg['Subject'] = subject
            
            # Personalize body with recipient name
            personalized_body = body.replace("[Recipient Name]", to_name).replace("Hello [Recipient Name]", f"Hello {to_name}")
            
            # Convert plain text to HTML format
            html_body = personalized_body.replace('\n', '<br>').replace('•', '&bull;')
            
            # Add signature inline if provided
            if signature_path and os.path.exists(signature_path):
                html_body += "<br><br><img src='cid:signature' style='max-width:300px;'>"
                msg.attach(MIMEText(html_body, 'html'))
                
                # Attach signature as inline image
                with open(signature_path, 'rb') as f:
                    img_data = f.read()
                    image = MIMEImage(img_data)
                    image.add_header('Content-ID', '<signature>')
                    image.add_header('Content-Disposition', 'inline')
                    msg.attach(image)
            else:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Add attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(attachment_path)}'
                    )
                    msg.attach(part)
            
            logger.info(f"🔗 CONNECTING TO SMTP SERVER {self.smtp_server}:{self.smtp_port}")
            
            # Connect and send
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            logger.info(f"🔐 AUTHENTICATING WITH {self.smtp_username}")
            server.login(self.smtp_username, self.smtp_password)
            
            text = msg.as_string()
            server.sendmail(self.from_email, to_email, text)
            server.quit()
            
            logger.info(f"✉️ EMAIL SENT SUCCESSFULLY to {to_email} (Name: {to_name})")
            return True, "Email sent successfully"
            
        except Exception as e:
            logger.error(f"❌ EMAIL SEND FAILED to {to_email}: {str(e)}")
            return False, str(e)
    
    async def process_queue(self):
        """Process email queue one by one"""
        if email_queue.processing:
            return {"message": "Queue is already being processed"}
        
        email_queue.processing = True
        processed = 0
        
        try:
            while True:
                email_item = email_queue.get_next_email()
                if not email_item:
                    break
                
                logger.info(f"📧 PROCESSING EMAIL {email_item['id']} to {email_item['to_email']} (Name: {email_item['to_name']})")
                
                # Send email
                success, message = self.send_single_email(
                    email_item["to_email"],
                    email_item["to_name"],
                    email_item["subject"],
                    email_item["body"],
                    email_item.get("attachment_path"),
                    email_item.get("signature_path")
                )
                
                if success:
                    email_queue.mark_sent(email_item["id"])
                    processed += 1
                else:
                    email_queue.mark_failed(email_item["id"], message)
                
                # Small delay between emails to avoid spam detection
                await asyncio.sleep(2)
                
        except Exception as e:
            logger.error(f"Error processing queue: {str(e)}")
        finally:
            email_queue.processing = False
        
        logger.info(f"✅ EMAIL QUEUE PROCESSING COMPLETED - {processed} emails sent successfully!")
        return {
            "message": f"Queue processing completed. {processed} emails sent.",
            "processed": processed,
            "status": email_queue.get_queue_status()
        }

# Global email service
email_service = SMTPEmailService()