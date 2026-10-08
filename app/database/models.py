from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from app.database.database import Base

class EmailAnalysis(Base):
    __tablename__ = "email_analyses"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, index=True)
    email_content = Column(Text)
    category = Column(String, index=True)
    confidence = Column(Float)
    summary = Column(Text)
    generated_reply = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
