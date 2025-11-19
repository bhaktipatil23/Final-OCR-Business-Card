import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='NewPassword123!',
        database='business_card_ocr'
    )
    cursor = connection.cursor()
    
    # Check events table structure
    cursor.execute("DESCRIBE events")
    events_columns = cursor.fetchall()
    print("📋 Events table structure:")
    for col in events_columns:
        print(f"   {col[0]} - {col[1]}")
    
    # Check sample events data
    cursor.execute("SELECT * FROM events LIMIT 3")
    events_data = cursor.fetchall()
    print("\n📝 Sample events data:")
    for event in events_data:
        print(f"   {event}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"❌ Error: {e}")