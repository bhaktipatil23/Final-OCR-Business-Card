import mysql.connector

try:
    connection = mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='NewPassword123!'
    )
    cursor = connection.cursor()
    cursor.execute('CREATE DATABASE IF NOT EXISTS business_card_ocr')
    cursor.execute('USE business_card_ocr')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS business_cards (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            name VARCHAR(255),
            phone VARCHAR(50),
            email VARCHAR(255),
            company VARCHAR(255),
            designation VARCHAR(255),
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    connection.commit()
    print('Database setup successful!')
    cursor.close()
    connection.close()
except Exception as e:
    print(f'Error: {e}')