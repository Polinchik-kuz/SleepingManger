from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, SleepRecord
from app.auth import get_current_user

router = APIRouter()

@router.get("/statistics", responses={401: {"description": "Не аутентифицирован"}})
def get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    records = db.query(SleepRecord).filter(
        SleepRecord.user_id == current_user.id
    ).all()
    
    if not records:
        return {
            "message": "Нет данных для статистики",
            "total_records": 0
        }
    
    total_records = len(records)
    avg_duration = sum(r.duration for r in records) / total_records
    avg_quality = sum(r.quality for r in records) / total_records
    
    max_duration = max(r.duration for r in records)
    min_duration = min(r.duration for r in records)
    
    return {
        "total_records": total_records,
        "average_duration": round(avg_duration, 2),
        "average_quality": round(avg_quality, 2),
        "max_duration": round(max_duration, 2),
        "min_duration": round(min_duration, 2)
    }

@router.get("/recommendations", responses={401: {"description": "Не аутентифицирован"}})
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    records = db.query(SleepRecord).filter(
        SleepRecord.user_id == current_user.id
    ).all()
    
    if not records:
        return {
            "recommendations": ["Начните записывать свой сон для получения персональных рекомендаций"]
        }
    
    recommendations = []
    
    avg_duration = sum(r.duration for r in records) / len(records)
    avg_quality = sum(r.quality for r in records) / len(records)
    
    if avg_duration < 7:
        recommendations.append("Старайтесь спать не менее 7-8 часов в сутки")
    elif avg_duration > 9:
        recommendations.append("Возможно вы спите слишком много, попробуйте сократить время сна до 8 часов")
    else:
        recommendations.append("Отличная продолжительность сна, продолжайте в том же духе!")
    
    if avg_quality < 5:
        recommendations.append("Качество вашего сна низкое. Попробуйте проветривать комнату перед сном")
        recommendations.append("Избегайте использования гаджетов за час до сна")
    elif avg_quality < 7:
        recommendations.append("Качество сна среднее, можно улучшить. Соблюдайте режим сна")
    else:
        recommendations.append("Отличное качество сна!")
    
    recommendations.append("Старайтесь ложиться спать в одно и то же время каждый день")
    
    return {
        "average_duration": round(avg_duration, 2),
        "average_quality": round(avg_quality, 2),
        "recommendations": recommendations
    }
