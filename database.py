import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Allow both DB_URL (as documented) and DATABASE_URL for backward compatibility
DB_URL = os.getenv("DB_URL") or os.getenv("DATABASE_URL") or "sqlite:///./rssgpt.db"

engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {},
    echo=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()