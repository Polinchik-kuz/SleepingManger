"""
Unit-тесты для Pydantic схем (app/schemas/).
Тестируют валидацию данных на уровне схем.
"""
import pytest
from pydantic import ValidationError
from datetime import datetime, timezone, timedelta

from app.schemas.user import UserCreate, UserUpdate, LoginRequest, UserResponse
from app.schemas.sleep import SleepRecordCreate, SleepRecordUpdate, NoteCreate
from app.schemas.goal import GoalCreate, GoalUpdate
from app.schemas.reminder import ReminderCreate, ReminderUpdate


class TestUserSchemas:
    """Тесты для схем пользователя."""
    
    def test_user_create_valid(self):
        """Валидные данные для создания пользователя."""
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123",
            age=25
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.age == 25
    
    def test_user_create_without_age(self):
        """Создание пользователя без возраста (опционально)."""
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        assert user.age is None
    
    def test_user_create_username_too_short(self):
        """Имя пользователя слишком короткое."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="ab",
                email="test@example.com",
                password="password123"
            )
        assert "min_length" in str(exc_info.value).lower() or "string_too_short" in str(exc_info.value).lower()
    
    def test_user_create_username_too_long(self):
        """Имя пользователя слишком длинное."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="a" * 51,
                email="test@example.com",
                password="password123"
            )
        assert "max_length" in str(exc_info.value).lower() or "string_too_long" in str(exc_info.value).lower()
    
    def test_user_create_invalid_email(self):
        """Невалидный email."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="invalid-email",
                password="password123"
            )
        assert "email" in str(exc_info.value).lower()
    
    def test_user_create_password_too_short(self):
        """Пароль слишком короткий."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="12345"
            )
        assert "min_length" in str(exc_info.value).lower() or "string_too_short" in str(exc_info.value).lower()
    
    def test_user_create_invalid_age(self):
        """Невалидный возраст (отрицательный)."""
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="password123",
                age=0
            )
    
    def test_user_create_age_too_high(self):
        """Возраст слишком большой."""
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="password123",
                age=151
            )
    
    def test_user_update_partial(self):
        """Частичное обновление пользователя."""
        update = UserUpdate(email="new@example.com")
        assert update.email == "new@example.com"
        assert update.age is None
    
    def test_user_update_only_age(self):
        """Обновление только возраста."""
        update = UserUpdate(age=30)
        assert update.age == 30
        assert update.email is None
    
    def test_login_request_valid(self):
        """Валидный запрос на вход."""
        login = LoginRequest(username="testuser", password="password123")
        assert login.username == "testuser"
        assert login.password == "password123"


class TestSleepSchemas:
    """Тесты для схем записей о сне."""
    
    def test_sleep_record_create_valid(self):
        """Валидные данные для создания записи о сне."""
        sleep_start = datetime.now(timezone.utc) - timedelta(hours=8)
        sleep_end = datetime.now(timezone.utc)
        
        record = SleepRecordCreate(
            sleep_start=sleep_start,
            sleep_end=sleep_end,
            quality=7,
            deep_sleep=2.0,
            light_sleep=4.0,
            rem_sleep=2.0
        )
        assert record.quality == 7
        assert record.deep_sleep == 2.0
    
    def test_sleep_record_create_minimal(self):
        """Создание записи с минимальными данными."""
        sleep_start = datetime.now(timezone.utc) - timedelta(hours=8)
        sleep_end = datetime.now(timezone.utc)
        
        record = SleepRecordCreate(
            sleep_start=sleep_start,
            sleep_end=sleep_end,
            quality=5
        )
        assert record.deep_sleep is None
        assert record.light_sleep is None
        assert record.rem_sleep is None
    
    def test_sleep_record_create_invalid_quality_low(self):
        """Качество сна ниже допустимого."""
        sleep_start = datetime.now(timezone.utc) - timedelta(hours=8)
        sleep_end = datetime.now(timezone.utc)
        
        with pytest.raises(ValidationError):
            SleepRecordCreate(
                sleep_start=sleep_start,
                sleep_end=sleep_end,
                quality=0
            )
    
    def test_sleep_record_create_invalid_quality_high(self):
        """Качество сна выше допустимого."""
        sleep_start = datetime.now(timezone.utc) - timedelta(hours=8)
        sleep_end = datetime.now(timezone.utc)
        
        with pytest.raises(ValidationError):
            SleepRecordCreate(
                sleep_start=sleep_start,
                sleep_end=sleep_end,
                quality=11
            )
    
    def test_sleep_record_create_end_before_start(self):
        """Время окончания раньше времени начала."""
        sleep_start = datetime.now(timezone.utc)
        sleep_end = datetime.now(timezone.utc) - timedelta(hours=8)
        
        with pytest.raises(ValidationError) as exc_info:
            SleepRecordCreate(
                sleep_start=sleep_start,
                sleep_end=sleep_end,
                quality=7
            )
        assert "sleep_end должно быть больше sleep_start" in str(exc_info.value)
    
    def test_sleep_record_create_negative_deep_sleep(self):
        """Отрицательное значение глубокого сна."""
        sleep_start = datetime.now(timezone.utc) - timedelta(hours=8)
        sleep_end = datetime.now(timezone.utc)
        
        with pytest.raises(ValidationError):
            SleepRecordCreate(
                sleep_start=sleep_start,
                sleep_end=sleep_end,
                quality=7,
                deep_sleep=-1.0
            )
    
    def test_sleep_record_update_partial(self):
        """Частичное обновление записи о сне."""
        update = SleepRecordUpdate(quality=8)
        assert update.quality == 8
        assert update.sleep_start is None
    
    def test_note_create_valid(self):
        """Валидная заметка."""
        note = NoteCreate(content="Хорошо выспался")
        assert note.content == "Хорошо выспался"
    
    def test_note_create_empty_content(self):
        """Пустая заметка не допускается."""
        with pytest.raises(ValidationError):
            NoteCreate(content="")
    
    def test_note_create_content_too_long(self):
        """Слишком длинная заметка."""
        with pytest.raises(ValidationError):
            NoteCreate(content="a" * 1001)


class TestGoalSchemas:
    """Тесты для схем целей."""
    
    def test_goal_create_valid(self):
        """Валидные данные для создания цели."""
        goal = GoalCreate(
            target_duration=8.0,
            target_quality=8,
            description="Спать 8 часов"
        )
        assert goal.target_duration == 8.0
        assert goal.target_quality == 8
    
    def test_goal_create_without_description(self):
        """Создание цели без описания."""
        goal = GoalCreate(
            target_duration=7.5,
            target_quality=7
        )
        assert goal.description is None
    
    def test_goal_create_invalid_duration_negative(self):
        """Отрицательная продолжительность."""
        with pytest.raises(ValidationError):
            GoalCreate(
                target_duration=-1.0,
                target_quality=8
            )
    
    def test_goal_create_invalid_duration_too_high(self):
        """Продолжительность больше 24 часов."""
        with pytest.raises(ValidationError):
            GoalCreate(
                target_duration=25.0,
                target_quality=8
            )
    
    def test_goal_create_invalid_quality_low(self):
        """Качество ниже допустимого."""
        with pytest.raises(ValidationError):
            GoalCreate(
                target_duration=8.0,
                target_quality=0
            )
    
    def test_goal_create_invalid_quality_high(self):
        """Качество выше допустимого."""
        with pytest.raises(ValidationError):
            GoalCreate(
                target_duration=8.0,
                target_quality=11
            )
    
    def test_goal_update_partial(self):
        """Частичное обновление цели."""
        update = GoalUpdate(target_quality=9)
        assert update.target_quality == 9
        assert update.target_duration is None
    
    def test_goal_create_description_too_long(self):
        """Слишком длинное описание."""
        with pytest.raises(ValidationError):
            GoalCreate(
                target_duration=8.0,
                target_quality=8,
                description="a" * 501
            )


class TestReminderSchemas:
    """Тесты для схем напоминаний."""
    
    def test_reminder_create_valid(self):
        """Валидные данные для создания напоминания."""
        reminder = ReminderCreate(
            reminder_time="22:00",
            message="Пора спать!"
        )
        assert reminder.reminder_time == "22:00"
        assert reminder.message == "Пора спать!"
    
    def test_reminder_create_without_message(self):
        """Создание напоминания без сообщения."""
        reminder = ReminderCreate(reminder_time="22:30")
        assert reminder.message is None
    
    def test_reminder_create_empty_time(self):
        """Пустое время напоминания."""
        with pytest.raises(ValidationError):
            ReminderCreate(reminder_time="")
    
    def test_reminder_create_time_too_long(self):
        """Слишком длинное время напоминания."""
        with pytest.raises(ValidationError):
            ReminderCreate(reminder_time="12345678901")
    
    def test_reminder_update_partial(self):
        """Частичное обновление напоминания."""
        update = ReminderUpdate(is_active=0)
        assert update.is_active == 0
        assert update.reminder_time is None
    
    def test_reminder_update_invalid_is_active(self):
        """Недопустимое значение is_active."""
        with pytest.raises(ValidationError):
            ReminderUpdate(is_active=2)
    
    def test_reminder_create_message_too_long(self):
        """Слишком длинное сообщение."""
        with pytest.raises(ValidationError):
            ReminderCreate(
                reminder_time="22:00",
                message="a" * 201
            )
