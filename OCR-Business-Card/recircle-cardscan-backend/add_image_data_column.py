import mysql.connector
from app.config import DATABASE_CONFIG

def add_image_data_column():
    """Add image_data column to business_cards table"""
    try:
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = connection.cursor()
        
        # Add image_data column
        cursor.execute("ALTER TABLE business_cards ADD COLUMN image_data TEXT")
        connection.commit()
        
        print("Successfully added image_data column to business_cards table")
        
    except mysql.connector.Error as error:
        if "Duplicate column name" in str(error):
            print("Column image_data already exists")
        else:
            print(f"Error: {error}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    add_image_data_column()