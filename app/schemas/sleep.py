from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class SleepRecordCreate(BaseModel):
    sleep_start: datetime
    sleep_end: datetime
    quality: int = Field(..., ge=1, le=10)
    deep_sleep: Optional[float] = Field(None, ge=0)
    light_sleep: Optional[float] = Field(None, ge=0)
    rem_sleep: Optional[float] = Field(None, ge=0)
    
    @validator('sleep_end')
    def validate_sleep_end(cls, v, values):
        if 'sleep_start' in values and v <= values['sleep_start']:
            raise ValueError('sleep_end должно быть больше sleep_start')
        return v
    
    @validator('rem_sleep')
    def validate_sleep_phases(cls, v, values):
        if 'sleep_start' in values and 'sleep_end' in values:
            total_duration = (values['sleep_end'] - values['sleep_start']).total_seconds() / 3600
            
            deep = values.get('deep_sleep', 0) or 0
            light = values.get('light_sleep', 0) or 0
            rem = v or 0
            
            phases_sum = deep + light + rem
            
            if phases_sum > total_duration:
                raise ValueError(
                    f'Сумма фаз сна ({phases_sum:.2f} ч) не может превышать '
                    f'общую продолжительность сна ({total_duration:.2f} ч)'
                )
        return v

class SleepRecordUpdate(BaseModel):
    sleep_start: Optional[datetime] = None
    sleep_end: Optional[datetime] = None
    quality: Optional[int] = Field(None, ge=1, le=10)
    deep_sleep: Optional[float] = Field(None, ge=0)
    light_sleep: Optional[float] = Field(None, ge=0)
    rem_sleep: Optional[float] = Field(None, ge=0)
    
    @validator('rem_sleep')
    def validate_sleep_phases(cls, v, values):
        if values.get('sleep_start') and values.get('sleep_end'):
            total_duration = (values['sleep_end'] - values['sleep_start']).total_seconds() / 3600
            
            deep = values.get('deep_sleep', 0) or 0
            light = values.get('light_sleep', 0) or 0
            rem = v or 0
            
            phases_sum = deep + light + rem
            
            if phases_sum > total_duration:
                raise ValueError(
                    f'Сумма фаз сна ({phases_sum:.2f} ч) не может превышать '
                    f'общую продолжительность сна ({total_duration:.2f} ч)'
                )
        return v

class SleepRecordResponse(BaseModel):
    id: int
    user_id: int
    sleep_date: datetime
    sleep_start: datetime
    sleep_end: datetime
    duration: float
    quality: int
    deep_sleep: Optional[float]
    light_sleep: Optional[float]
    rem_sleep: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class NoteResponse(BaseModel):
    id: int
    sleep_record_id: int
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True
