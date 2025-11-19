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
    
    # Test connection
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    print("✅ Database connection successful!")
    
    # Check tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"📋 Tables found: {[table[0] for table in tables]}")
    
    # Check business_cards data
    cursor.execute("SELECT COUNT(*) FROM business_cards")
    count = cursor.fetchone()[0]
    print(f"📊 Business cards count: {count}")
    
    if count > 0:
        cursor.execute("SELECT name, email FROM business_cards LIMIT 3")
        samples = cursor.fetchall()
        print("📝 Sample data:")
        for sample in samples:
            print(f"   Name: {sample[0]}, Email: {sample[1]}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")