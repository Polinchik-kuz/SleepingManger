"""
Конфигурация pytest и общие фикстуры для тестов.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timezone, timedelta

from app.main import app
from app.database import Base, get_db
from app.auth import get_password_hash, create_access_token
from app.models import User, SleepRecord, Goal, Reminder, Note


# Создаем тестовую базу данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Создает новую сессию базы данных для каждого теста."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Создает тестовый клиент FastAPI."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Создает тестового пользователя."""
    hashed_password = get_password_hash("testpassword123")
    user = User(
        username="testuser",
        email="test@example.com",
        password=hashed_password,
        age=25
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user2(db_session):
    """Создает второго тестового пользователя."""
    hashed_password = get_password_hash("password456")
    user = User(
        username="testuser2",
        email="test2@example.com",
        password=hashed_password,
        age=30
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user):
    """Создает токен авторизации для тестового пользователя."""
    token = create_access_token(data={"sub": test_user.username})
    return token


@pytest.fixture
def auth_headers(auth_token):
    """Возвращает заголовки с токеном авторизации."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def test_sleep_record(db_session, test_user):
    """Создает тестовую запись о сне."""
    sleep_start = datetime.now(timezone.utc) - timedelta(hours=8)
    sleep_end = datetime.now(timezone.utc)
    
    record = SleepRecord(
        user_id=test_user.id,
        sleep_start=sleep_start,
        sleep_end=sleep_end,
        duration=8.0,
        quality=7,
        deep_sleep=2.5,
        light_sleep=4.0,
        rem_sleep=1.5
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)
    return record


@pytest.fixture
def multiple_sleep_records(db_session, test_user):
    """Создает несколько записей о сне для тестов аналитики."""
    records = []
    for i in range(5):
        sleep_start = datetime.now(timezone.utc) - timedelta(days=i, hours=8)
        sleep_end = datetime.now(timezone.utc) - timedelta(days=i)
        
        record = SleepRecord(
            user_id=test_user.id,
            sleep_start=sleep_start,
            sleep_end=sleep_end,
            duration=6.0 + i * 0.5,  # Разная продолжительность
            quality=5 + i,  # Разное качество
            deep_sleep=1.5 + i * 0.2,
            light_sleep=3.0 + i * 0.2,
            rem_sleep=1.0 + i * 0.1
        )
        db_session.add(record)
        records.append(record)
    
    db_session.commit()
    for record in records:
        db_session.refresh(record)
    return records


@pytest.fixture
def test_goal(db_session, test_user):
    """Создает тестовую цель."""
    goal = Goal(
        user_id=test_user.id,
        target_duration=8.0,
        target_quality=8,
        description="Спать не менее 8 часов с хорошим качеством"
    )
    db_session.add(goal)
    db_session.commit()
    db_session.refresh(goal)
    return goal


@pytest.fixture
def test_reminder(db_session, test_user):
    """Создает тестовое напоминание."""
    reminder = Reminder(
        user_id=test_user.id,
        reminder_time="22:00",
        message="Пора готовиться ко сну!",
        is_active=1
    )
    db_session.add(reminder)
    db_session.commit()
    db_session.refresh(reminder)
    return reminder


@pytest.fixture
def test_note(db_session, test_sleep_record):
    """Создает тестовую заметку к записи о сне."""
    note = Note(
        sleep_record_id=test_sleep_record.id,
        content="Сегодня спал хорошо, быстро заснул"
    )
    db_session.add(note)
    db_session.commit()
    db_session.refresh(note)
    return note
