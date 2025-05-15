from app.db.database import SessionLocal
from sqlalchemy import text
#from db.database import SessionLocal

def test_postgres_connection():
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1"))
        print("PostgreSQL connected successfully:", result.scalar())  # Should print: 1
    except Exception as e:
        print("PostgreSQL connection failed:", e)
    finally:
        db.close()

if __name__ == "__main__":
    test_postgres_connection()