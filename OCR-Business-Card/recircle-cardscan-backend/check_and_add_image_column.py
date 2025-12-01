import mysql.connector
from app.config import settings

def check_and_add_image_column():
    try:
        connection = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        
        cursor = connection.cursor()
        
        # Check if image_data column exists
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'business_cards' 
            AND COLUMN_NAME = 'image_data'
        """, (settings.DB_NAME,))
        
        result = cursor.fetchone()
        
        if not result:
            print("Adding image_data column...")
            cursor.execute("ALTER TABLE business_cards ADD COLUMN image_data LONGTEXT COMMENT 'Base64 encoded image data'")
            connection.commit()
            print("image_data column added successfully!")
        else:
            print("image_data column already exists.")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_and_add_image_column()