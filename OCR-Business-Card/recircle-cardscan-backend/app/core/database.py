import mysql.connector
from mysql.connector import Error
from app.config import settings
import logging

logger = logging.getLogger(__name__)

def init_database():
    """Initialize database tables"""
    try:
        connection = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create business_cards table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS business_cards (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    file_path VARCHAR(500),
                    name VARCHAR(255),
                    phone VARCHAR(50),
                    email VARCHAR(255),
                    company VARCHAR(255),
                    designation VARCHAR(255),
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            # Create business_card_edits table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS business_card_edits (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    business_card_id INT,
                    field_name VARCHAR(100),
                    old_value TEXT,
                    new_value TEXT,
                    edited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (business_card_id) REFERENCES business_cards(id)
                )
            """)
            
            # Create processing_batches table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_batches (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    batch_id VARCHAR(100) UNIQUE,
                    status VARCHAR(50),
                    total_files INT,
                    processed_files INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            connection.commit()
            cursor.close()
            connection.close()
            
            logger.info("Database tables created successfully")
            return True
            
    except Error as e:
        logger.error(f"Error initializing database: {e}")
        return False