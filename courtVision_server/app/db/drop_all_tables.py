from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings

Base = declarative_base()

engine = create_engine(settings.postgres_database_url)

meta = MetaData()
meta.reflect(bind=engine)
meta.drop_all(bind=engine)

print("All tables dropped.")



