from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Reminder
from app.schemas import reminder as reminder_schemas
from app.auth import get_current_user

router = APIRouter()

@router.post("/reminders", response_model=reminder_schemas.ReminderResponse, status_code=status.HTTP_201_CREATED, responses={401: {"description": "Не аутентифицирован"}})
def create_reminder(
    reminder_data: reminder_schemas.ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_reminder = Reminder(
        user_id=current_user.id,
        reminder_time=reminder_data.reminder_time,
        message=reminder_data.message,
        is_active=1
    )
    db.add(new_reminder)
    db.commit()
    db.refresh(new_reminder)
    return new_reminder

@router.put("/reminders/{reminder_id}", response_model=reminder_schemas.ReminderResponse, responses={401: {"description": "Не аутентифицирован"}, 404: {"description": "Напоминание не найдено"}})
def update_reminder(
    reminder_id: int,
    reminder_update: reminder_schemas.ReminderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()
    
    if not reminder:
        raise HTTPException(status_code=404, detail="Напоминание не найдено")
    
    if reminder_update.reminder_time is not None:
        reminder.reminder_time = reminder_update.reminder_time
    if reminder_update.message is not None:
        reminder.message = reminder_update.message
    if reminder_update.is_active is not None:
        reminder.is_active = reminder_update.is_active
    
    db.commit()
    db.refresh(reminder)
    return reminder

@router.delete("/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT, responses={401: {"description": "Не аутентифицирован"}, 404: {"description": "Напоминание не найдено"}})
def delete_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()
    
    if not reminder:
        raise HTTPException(status_code=404, detail="Напоминание не найдено")
    
    reminder.is_active = 0
    db.commit()
    return None
