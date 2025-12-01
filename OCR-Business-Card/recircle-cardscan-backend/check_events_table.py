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
    
    # Check if events table exists
    cursor.execute("SHOW TABLES LIKE 'events'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        print("Events table exists!")
        
        # Check events table structure
        cursor.execute("DESCRIBE events")
        columns = cursor.fetchall()
        print("\nEvents table structure:")
        for col in columns:
            print(f"  {col['Field']} - {col['Type']}")
        
        # Check if there's any data in events table
        cursor.execute("SELECT COUNT(*) as count FROM events")
        count = cursor.fetchone()
        print(f"\nTotal records in events table: {count['count']}")
        
        # Show sample data
        cursor.execute("SELECT * FROM events LIMIT 5")
        events = cursor.fetchall()
        print("\nSample events data:")
        for event in events:
            print(f"  Batch ID: {event.get('batch_id', 'N/A')}")
            print(f"  Name: {event.get('name', 'N/A')}")
            print(f"  Team: {event.get('team', 'N/A')}")
            print(f"  Event: {event.get('event', 'N/A')}")
            print("  ---")
    else:
        print("Events table does NOT exist!")
        print("This is likely the cause of the 500 error.")
        
        # Show all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\nAvailable tables:")
        for table in tables:
            print(f"  - {list(table.values())[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")