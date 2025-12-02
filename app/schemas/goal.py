from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class GoalCreate(BaseModel):
    target_duration: float = Field(..., ge=0, le=24)
    target_quality: int = Field(..., ge=1, le=10)
    description: Optional[str] = Field(None, max_length=500)

class GoalUpdate(BaseModel):
    target_duration: Optional[float] = Field(None, ge=0, le=24)
    target_quality: Optional[int] = Field(None, ge=1, le=10)
    description: Optional[str] = Field(None, max_length=500)

class GoalResponse(BaseModel):
    id: int
    user_id: int
    target_duration: float
    target_quality: int
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
