from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create a database engine
engine = create_engine(settings.postgres_database_url)

# Create an inspector object to check for tables
inspector = inspect(engine)

# Table name you want to check
table_name = "teams"  # Replace with your table name

# Check if the table exists
if table_name in inspector.get_table_names():
    print(f"The table {table_name} exists.")
else:
    print(f"The table {table_name} has been deleted or does not exist.")

