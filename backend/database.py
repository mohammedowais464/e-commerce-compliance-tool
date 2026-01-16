from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./scans.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ScanRecord(Base):
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    risk_score = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    # Storing complex objects as JSON strings for simplicity in this hackathon
    product_data = Column(JSON) 
    violations_data = Column(JSON)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
