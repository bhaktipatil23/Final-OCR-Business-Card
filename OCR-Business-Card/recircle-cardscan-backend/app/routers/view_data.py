from fastapi import APIRouter, HTTPException, Query
import mysql.connector
from app.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/api/v1/saved-batches")
async def get_saved_batches():
    """Get all saved batches with filtering support"""
    try:
        connection = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # Get all saved batches with record counts from events table
        query = """
        SELECT 
            e.name,
            e.team,
            e.event,
            COUNT(bc.id) as total_records
        FROM events e
        LEFT JOIN business_cards bc ON e.batch_id = bc.batch_id
        GROUP BY e.batch_id, e.name, e.team, e.event
        ORDER BY e.batch_id DESC
        """
        
        cursor.execute(query)
        batches = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return {"batches": batches}
        
    except mysql.connector.Error as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error fetching saved batches: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/saved-data/{batch_id}")
async def get_batch_data(batch_id: str):
    """Get business card data for a specific batch"""
    try:
        connection = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # Get business cards for the batch
        query = """
        SELECT 
            name,
            phone,
            email,
            company,
            designation,
            address
        FROM business_cards
        WHERE batch_id = %s
        ORDER BY id
        """
        
        cursor.execute(query, (batch_id,))
        cards = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return {"data": cards, "total": len(cards)}
        
    except mysql.connector.Error as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error fetching batch data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/search-records")
async def search_records(search_type: str, search_term: str):
    """Search for records by form name, form name & team, or form name & event"""
    try:
        connection = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        
        cursor = connection.cursor(dictionary=True)
        
        if search_type == "name":
            # Search by form name (events.name)
            query = """
            SELECT 
                bc.name as card_name,
                bc.phone,
                bc.email,
                bc.company,
                bc.designation,
                bc.address,
                e.name as form_name,
                e.event,
                e.team,
                COALESCE(bc.image_data, '') as image_data
            FROM business_cards bc
            JOIN events e ON bc.batch_id = e.batch_id
            WHERE e.name LIKE %s
            ORDER BY e.batch_id DESC
            """
            cursor.execute(query, (f"%{search_term}%",))
            
        elif search_type == "name_team":
            # Search by form name and team
            terms = search_term.split(',')
            if len(terms) == 2 and terms[0].strip() and terms[1].strip():
                name_term, team_term = terms[0].strip(), terms[1].strip()
                query = """
                SELECT 
                    bc.name as card_name,
                    bc.phone,
                    bc.email,
                    bc.company,
                    bc.designation,
                    bc.address,
                    e.name as form_name,
                    e.event,
                    e.team,
                    COALESCE(bc.image_data, '') as image_data
                FROM business_cards bc
                JOIN events e ON bc.batch_id = e.batch_id
                WHERE e.name LIKE %s AND e.team LIKE %s
                ORDER BY e.batch_id DESC
                """
                cursor.execute(query, (f"%{name_term}%", f"%{team_term}%"))
            else:
                # If only one term, search in both name and team
                clean_term = search_term.replace(',', '').strip()
                query = """
                SELECT 
                    bc.name as card_name,
                    bc.phone,
                    bc.email,
                    bc.company,
                    bc.designation,
                    bc.address,
                    e.name as form_name,
                    e.event,
                    e.team,
                    COALESCE(bc.image_data, '') as image_data
                FROM business_cards bc
                JOIN events e ON bc.batch_id = e.batch_id
                WHERE (e.name LIKE %s OR e.team LIKE %s)
                ORDER BY e.batch_id DESC
                """
                cursor.execute(query, (f"%{clean_term}%", f"%{clean_term}%"))
            
        elif search_type == "name_event":
            # Search by form name and event
            terms = search_term.split(',')
            if len(terms) == 2 and terms[0].strip() and terms[1].strip():
                name_term, event_term = terms[0].strip(), terms[1].strip()
                query = """
                SELECT 
                    bc.name as card_name,
                    bc.phone,
                    bc.email,
                    bc.company,
                    bc.designation,
                    bc.address,
                    e.name as form_name,
                    e.event,
                    e.team,
                    COALESCE(bc.image_data, '') as image_data
                FROM business_cards bc
                JOIN events e ON bc.batch_id = e.batch_id
                WHERE e.name LIKE %s AND e.event LIKE %s
                ORDER BY e.batch_id DESC
                """
                cursor.execute(query, (f"%{name_term}%", f"%{event_term}%"))
            else:
                # If only one term, search in both name and event
                clean_term = search_term.replace(',', '').strip()
                query = """
                SELECT 
                    bc.name as card_name,
                    bc.phone,
                    bc.email,
                    bc.company,
                    bc.designation,
                    bc.address,
                    e.name as form_name,
                    e.event,
                    e.team,
                    COALESCE(bc.image_data, '') as image_data
                FROM business_cards bc
                JOIN events e ON bc.batch_id = e.batch_id
                WHERE (e.name LIKE %s OR e.event LIKE %s)
                ORDER BY e.batch_id DESC
                """
                cursor.execute(query, (f"%{clean_term}%", f"%{clean_term}%"))
            
        else:
            raise HTTPException(status_code=400, detail="Invalid search_type. Use 'name', 'name_team', or 'name_event'")
        
        records = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return {"records": records, "total": len(records), "search_type": search_type, "search_term": search_term}
        
    except mysql.connector.Error as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error searching records: {e}")
        raise HTTPException(status_code=500, detail=str(e))