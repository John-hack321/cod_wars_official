from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# For simplicity, we'll use a local SQLite database.
# In a production environment, this would be configured via settings.
SQLALCHEMY_DATABASE_URL = "postgresql://cod_admin:1423Okello,@localhost:5432/cod_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
