import pymysql
from app.config import settings

print("Testing API endpoints...")

try:
    # Test database connection with settings
    print(f"DB Host: {settings.DB_HOST}")
    print(f"DB User: {settings.DB_USER}")
    print(f"DB Name: {settings.DB_NAME}")
    
    connection = pymysql.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME
    )
    cursor = connection.cursor()
    
    # Test names query
    print("\n🔍 Testing names query...")
    cursor.execute("SELECT DISTINCT name FROM business_cards WHERE name IS NOT NULL AND name != '' ORDER BY name LIMIT 5")
    names = cursor.fetchall()
    print(f"Names found: {[row[0] for row in names]}")
    
    # Test contacts query
    print("\n🔍 Testing contacts query...")
    cursor.execute("""
        SELECT name, email, company, designation, phone, address 
        FROM business_cards 
        WHERE email IS NOT NULL AND email != ''
        ORDER BY name LIMIT 3
    """)
    contacts = cursor.fetchall()
    print(f"Contacts found: {len(contacts)}")
    for contact in contacts:
        print(f"  {contact[0]} - {contact[1]}")
    
    cursor.close()
    connection.close()
    print("✅ All queries successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()