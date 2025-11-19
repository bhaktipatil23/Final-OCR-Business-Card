from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/v1", tags=["email-filters"])

@router.get("/names")
async def get_all_names():
    """Get all unique names from events table (user-entered names)"""
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'NewPassword123!'),
            database=os.getenv('DB_NAME', 'business_card_ocr')
        )
        cursor = connection.cursor()
        
        cursor.execute("SELECT DISTINCT name FROM events WHERE name IS NOT NULL AND name != '' ORDER BY name")
        names = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        connection.close()
        
        return {"names": names}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching names: {str(e)}")

@router.get("/events/{name}")
async def get_events_by_name(name: str):
    """Get all events created by a specific user name"""
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'NewPassword123!'),
            database=os.getenv('DB_NAME', 'business_card_ocr')
        )
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT id, event, batch_id, team
            FROM events 
            WHERE name = %s
            ORDER BY id DESC
        """, (name,))
        
        events = []
        for row in cursor.fetchall():
            events.append({
                "batch_id": row[2],
                "event_name": row[1],
                "team": row[3],
                "event_id": row[0]
            })
        
        cursor.close()
        connection.close()
        
        return {"events": events}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")

@router.get("/contacts")
async def get_all_contacts():
    """Get all contacts with name and email"""
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'NewPassword123!'),
            database=os.getenv('DB_NAME', 'business_card_ocr')
        )
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT name, email, company, designation, phone, address 
            FROM business_cards 
            WHERE email IS NOT NULL AND email != ''
            ORDER BY name
        """)
        
        contacts = []
        for row in cursor.fetchall():
            contacts.append({
                "name": row[0] or "No Name",
                "email": row[1],
                "company": row[2] or "No Company",
                "designation": row[3] or "No Designation",
                "phone": row[4] or "No Phone",
                "address": row[5] or "No Address"
            })
        
        cursor.close()
        connection.close()
        
        return {"contacts": contacts}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching contacts: {str(e)}")

@router.get("/contacts/by-batch/{batch_id}")
async def get_contacts_by_batch(batch_id: str):
    """Get all contacts from a specific batch"""
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'NewPassword123!'),
            database=os.getenv('DB_NAME', 'business_card_ocr')
        )
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT name, email, company, designation, phone, address 
            FROM business_cards 
            WHERE batch_id = %s AND email IS NOT NULL AND email != ''
            ORDER BY id DESC
        """, (batch_id,))
        
        contacts = []
        for row in cursor.fetchall():
            contacts.append({
                "name": row[0] or "No Name",
                "email": row[1],
                "company": row[2] or "No Company", 
                "designation": row[3] or "No Designation",
                "phone": row[4] or "No Phone",
                "address": row[5] or "No Address"
            })
        
        cursor.close()
        connection.close()
        
        return {"contacts": contacts}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching contacts by batch: {str(e)}")