import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("Environment variables:")
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD')}")
print(f"DB_NAME: {os.getenv('DB_NAME')}")

# Test with direct env vars
import pymysql

try:
    connection = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'NewPassword123!'),
        database=os.getenv('DB_NAME', 'business_card_ocr')
    )
    print("✅ Connection successful with env vars!")
    connection.close()
except Exception as e:
    print(f"❌ Error with env vars: {e}")