import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'NewPassword123!'),
        database=os.getenv('DB_NAME', 'business_card_ocr')
    )
    cursor = conn.cursor(dictionary=True)
    
    # Test the exact search query that's failing
    search_term = "Bhakti,Tech"
    search_type = "name_team"
    
    print(f"Testing search: {search_type} with term: {search_term}")
    
    # Parse the search term
    terms = search_term.split(',')
    if len(terms) == 2 and terms[0].strip() and terms[1].strip():
        name_term, team_term = terms[0].strip(), terms[1].strip()
        print(f"Name term: '{name_term}', Team term: '{team_term}'")
        
        query = """
        SELECT 
            bc.name as card_name,
            bc.phone,
            bc.email,
            bc.company,
            bc.designation,
            bc.address,
            bc.image_data,
            e.name as form_name,
            e.event,
            e.team,
            e.batch_id
        FROM business_cards bc
        JOIN events e ON bc.batch_id = e.batch_id
        WHERE e.name LIKE %s AND e.team LIKE %s
        ORDER BY e.batch_id DESC
        """
        
        print(f"Executing query with parameters: %{name_term}% and %{team_term}%")
        cursor.execute(query, (f"%{name_term}%", f"%{team_term}%"))
        records = cursor.fetchall()
        
        print(f"Found {len(records)} records")
        for i, record in enumerate(records[:3]):  # Show first 3 records
            print(f"\nRecord {i+1}:")
            print(f"  Card Name: {record.get('card_name', 'N/A')}")
            print(f"  Form Name: {record.get('form_name', 'N/A')}")
            print(f"  Team: {record.get('team', 'N/A')}")
            print(f"  Event: {record.get('event', 'N/A')}")
            print(f"  Company: {record.get('company', 'N/A')}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()