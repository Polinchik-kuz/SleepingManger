from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class SleepRecord(Base):
    __tablename__ = "sleep_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    sleep_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    sleep_start = Column(DateTime)
    sleep_end = Column(DateTime)
    duration = Column(Float)
    quality = Column(Integer)
    deep_sleep = Column(Float, nullable=True)
    light_sleep = Column(Float, nullable=True)
    rem_sleep = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="sleep_records")
    notes = relationship("Note", back_populates="sleep_record", cascade="all, delete-orphan")
