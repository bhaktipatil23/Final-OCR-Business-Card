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
    
    # Check business_cards table structure
    cursor.execute("DESCRIBE business_cards")
    columns = cursor.fetchall()
    print("Business_cards table structure:")
    for col in columns:
        print(f"  {col['Field']} - {col['Type']}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")