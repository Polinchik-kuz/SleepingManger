from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re

class ReminderCreate(BaseModel):
    reminder_time: str = Field(..., min_length=1, max_length=10)
    message: Optional[str] = Field(None, max_length=200)
    
    @validator('reminder_time')
    def validate_reminder_time(cls, v):
        # Проверка формата HH:MM
        if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', v):
            raise ValueError('reminder_time должно быть в формате HH:MM (например, 09:30 или 23:45)')
        return v

class ReminderUpdate(BaseModel):
    reminder_time: Optional[str] = Field(None, min_length=1, max_length=10)
    message: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None
    
    @validator('reminder_time')
    def validate_reminder_time(cls, v):
        if v is not None:
            # Проверка формата HH:MM
            if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', v):
                raise ValueError('reminder_time должно быть в формате HH:MM (например, 09:30 или 23:45)')
        return v

class ReminderResponse(BaseModel):
    id: int
    user_id: int
    reminder_time: str
    is_active: bool
    message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
