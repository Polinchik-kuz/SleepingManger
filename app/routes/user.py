from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import user as user_schemas
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter()

@router.post("/register", response_model=user_schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь с таким именем уже существует")
    
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email уже используется")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        age=user.age
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=user_schemas.TokenResponse, responses={401: {"description": "Неверные учетные данные"}})
def login(login_data: user_schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", response_model=user_schemas.UserResponse, responses={401: {"description": "Не аутентифицирован"}})
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=user_schemas.UserResponse, responses={401: {"description": "Не аутентифицирован"}, 400: {"description": "Email уже используется"}})
def update_profile(
    user_update: user_schemas.UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_update.email is not None:
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email уже используется")
        current_user.email = user_update.email
    
    if user_update.age is not None:
        current_user.age = user_update.age
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.delete("/profile", status_code=status.HTTP_204_NO_CONTENT, responses={401: {"description": "Не аутентифицирован"}})
def delete_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.delete(current_user)
    db.commit()
    return None
