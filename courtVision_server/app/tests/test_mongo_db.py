from pymongo import MongoClient
from app.core.config import settings 

def test_mongo_connection():
    try:
        # Establish MongoDB connection
        client = MongoClient(settings.mongo_database_url)
        
        # Try accessing a database (e.g., 'admin') to check the connection
        db = client.admin
        
        # Run a simple command to check the connection
        server_status = db.command("serverStatus")
        
        print("MongoDB connected successfully:", server_status["ok"] == 1.0)  # Should print: True
    except Exception as e:
        print("MongoDB connection failed:", e)
    finally:
        client.close()

if __name__ == "__main__":
    test_mongo_connection()
