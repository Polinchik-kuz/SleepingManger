from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReminderCreate(BaseModel):
    reminder_time: str = Field(..., min_length=1, max_length=10)
    message: Optional[str] = Field(None, max_length=200)

class ReminderUpdate(BaseModel):
    reminder_time: Optional[str] = Field(None, min_length=1, max_length=10)
    message: Optional[str] = Field(None, max_length=200)
    is_active: Optional[int] = Field(None, ge=0, le=1)

class ReminderResponse(BaseModel):
    id: int
    user_id: int
    reminder_time: str
    is_active: int
    message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
