from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Goal
from app.schemas import goal as goal_schemas
from app.auth import get_current_user
from typing import List

router = APIRouter()

@router.post("/goals", response_model=goal_schemas.GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    goal_data: goal_schemas.GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_goal = Goal(
        user_id=current_user.id,
        target_duration=goal_data.target_duration,
        target_quality=goal_data.target_quality,
        description=goal_data.description
    )
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return new_goal

@router.get("/goals/{goal_id}", response_model=goal_schemas.GoalResponse)
def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Цель не найдена")
    return goal

@router.put("/goals/{goal_id}", response_model=goal_schemas.GoalResponse)
def update_goal(
    goal_id: int,
    goal_update: goal_schemas.GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Цель не найдена")
    
    if goal_update.target_duration is not None:
        goal.target_duration = goal_update.target_duration
    if goal_update.target_quality is not None:
        goal.target_quality = goal_update.target_quality
    if goal_update.description is not None:
        goal.description = goal_update.description
    
    db.commit()
    db.refresh(goal)
    return goal

@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Цель не найдена")
    
    db.delete(goal)
    db.commit()
    return None

@router.get("/goals", response_model=List[goal_schemas.GoalResponse])
def get_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    goals = db.query(Goal).filter(
        Goal.user_id == current_user.id
    ).order_by(Goal.created_at.desc()).all()
    
    return goals
