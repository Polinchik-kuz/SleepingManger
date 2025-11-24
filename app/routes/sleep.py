from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, SleepRecord, Note
from app.schemas import sleep as sleep_schemas
from app.auth import get_current_user
from typing import List

router = APIRouter()

@router.post("/sleep", response_model=sleep_schemas.SleepRecordResponse, status_code=status.HTTP_201_CREATED)
def create_sleep_record(
    sleep_data: sleep_schemas.SleepRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    duration = (sleep_data.sleep_end - sleep_data.sleep_start).total_seconds() / 3600
    
    new_record = SleepRecord(
        user_id=current_user.id,
        sleep_start=sleep_data.sleep_start,
        sleep_end=sleep_data.sleep_end,
        duration=duration,
        quality=sleep_data.quality,
        deep_sleep=sleep_data.deep_sleep,
        light_sleep=sleep_data.light_sleep,
        rem_sleep=sleep_data.rem_sleep
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

@router.get("/sleep/{record_id}", response_model=sleep_schemas.SleepRecordResponse)
def get_sleep_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(SleepRecord).filter(
        SleepRecord.id == record_id,
        SleepRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return record

@router.put("/sleep/{record_id}", response_model=sleep_schemas.SleepRecordResponse)
def update_sleep_record(
    record_id: int,
    sleep_update: sleep_schemas.SleepRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(SleepRecord).filter(
        SleepRecord.id == record_id,
        SleepRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    
    if sleep_update.sleep_start is not None:
        record.sleep_start = sleep_update.sleep_start
    if sleep_update.sleep_end is not None:
        record.sleep_end = sleep_update.sleep_end
    if sleep_update.quality is not None:
        record.quality = sleep_update.quality
    if sleep_update.deep_sleep is not None:
        record.deep_sleep = sleep_update.deep_sleep
    if sleep_update.light_sleep is not None:
        record.light_sleep = sleep_update.light_sleep
    if sleep_update.rem_sleep is not None:
        record.rem_sleep = sleep_update.rem_sleep
    
    if sleep_update.sleep_start is not None or sleep_update.sleep_end is not None:
        record.duration = (record.sleep_end - record.sleep_start).total_seconds() / 3600
    
    db.commit()
    db.refresh(record)
    return record

@router.delete("/sleep/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sleep_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(SleepRecord).filter(
        SleepRecord.id == record_id,
        SleepRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    
    db.delete(record)
    db.commit()
    return None

@router.post("/sleep/{record_id}/note", response_model=sleep_schemas.NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    record_id: int,
    note_data: sleep_schemas.NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(SleepRecord).filter(
        SleepRecord.id == record_id,
        SleepRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Запись о сне не найдена")
    
    new_note = Note(
        sleep_record_id=record_id,
        content=note_data.content
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

@router.get("/sleep", response_model=List[sleep_schemas.SleepRecordResponse])
def get_sleep_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    records = db.query(SleepRecord).filter(
        SleepRecord.user_id == current_user.id
    ).order_by(SleepRecord.sleep_date.desc()).all()
    
    return records
