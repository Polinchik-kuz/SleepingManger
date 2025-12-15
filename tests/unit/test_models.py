"""
Unit-тесты для моделей SQLAlchemy (app/models/).
Тестируют создание объектов моделей и их атрибуты.
"""
import pytest
from datetime import datetime, timezone, timedelta

from app.models import User, SleepRecord, Goal, Reminder, Note


class TestUserModel:
    """Тесты для модели User."""
    
    def test_create_user(self, db_session):
        """Создание пользователя."""
        user = User(
            username="newuser",
            email="newuser@example.com",
            password="hashedpassword",
            age=28
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.age == 28
        assert user.created_at is not None
    
    def test_user_created_at_auto(self, db_session):
        """Автоматическое заполнение created_at."""
        before = datetime.now(timezone.utc)
        
        user = User(
            username="timeuser",
            email="timeuser@example.com",
            password="hashedpassword"
        )
        db_session.add(user)
        db_session.commit()
        
        after = datetime.now(timezone.utc)
        
        # Делаем created_at aware если он naive
        created = user.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        
        assert before <= created <= after
    
    def test_user_without_age(self, db_session):
        """Создание пользователя без возраста."""
        user = User(
            username="noageuser",
            email="noage@example.com",
            password="hashedpassword"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.age is None
    
    def test_user_relationships(self, db_session, test_user):
        """Проверка связей пользователя."""
        assert hasattr(test_user, 'sleep_records')
        assert hasattr(test_user, 'goals')
        assert hasattr(test_user, 'reminders')
    
    def test_user_cascade_delete_sleep_records(self, db_session, test_user, test_sleep_record):
        """Каскадное удаление записей о сне при удалении пользователя."""
        record_id = test_sleep_record.id
        
        db_session.delete(test_user)
        db_session.commit()
        
        deleted_record = db_session.query(SleepRecord).filter_by(id=record_id).first()
        assert deleted_record is None


class TestSleepRecordModel:
    """Тесты для модели SleepRecord."""
    
    def test_create_sleep_record(self, db_session, test_user):
        """Создание записи о сне."""
        sleep_start = datetime.now(timezone.utc) - timedelta(hours=8)
        sleep_end = datetime.now(timezone.utc)
        
        record = SleepRecord(
            user_id=test_user.id,
            sleep_start=sleep_start,
            sleep_end=sleep_end,
            duration=8.0,
            quality=7
        )
        db_session.add(record)
        db_session.commit()
        
        assert record.id is not None
        assert record.user_id == test_user.id
        assert record.duration == 8.0
        assert record.quality == 7
    
    def test_sleep_record_optional_fields(self, db_session, test_user):
        """Создание записи с опциональными полями."""
        sleep_start = datetime.now(timezone.utc) - timedelta(hours=7)
        sleep_end = datetime.now(timezone.utc)
        
        record = SleepRecord(
            user_id=test_user.id,
            sleep_start=sleep_start,
            sleep_end=sleep_end,
            duration=7.0,
            quality=6,
            deep_sleep=2.0,
            light_sleep=3.5,
            rem_sleep=1.5
        )
        db_session.add(record)
        db_session.commit()
        
        assert record.deep_sleep == 2.0
        assert record.light_sleep == 3.5
        assert record.rem_sleep == 1.5
    
    def test_sleep_record_user_relationship(self, db_session, test_sleep_record, test_user):
        """Проверка связи с пользователем."""
        assert test_sleep_record.user.id == test_user.id
        assert test_sleep_record.user.username == test_user.username
    
    def test_sleep_record_notes_relationship(self, db_session, test_sleep_record, test_note):
        """Проверка связи с заметками."""
        assert len(test_sleep_record.notes) == 1
        assert test_sleep_record.notes[0].content == test_note.content


class TestGoalModel:
    """Тесты для модели Goal."""
    
    def test_create_goal(self, db_session, test_user):
        """Создание цели."""
        goal = Goal(
            user_id=test_user.id,
            target_duration=8.0,
            target_quality=8,
            description="Спать 8 часов каждый день"
        )
        db_session.add(goal)
        db_session.commit()
        
        assert goal.id is not None
        assert goal.target_duration == 8.0
        assert goal.target_quality == 8
    
    def test_goal_without_description(self, db_session, test_user):
        """Создание цели без описания."""
        goal = Goal(
            user_id=test_user.id,
            target_duration=7.5,
            target_quality=7
        )
        db_session.add(goal)
        db_session.commit()
        
        assert goal.description is None
    
    def test_goal_user_relationship(self, db_session, test_goal, test_user):
        """Проверка связи с пользователем."""
        assert test_goal.user.id == test_user.id


class TestReminderModel:
    """Тесты для модели Reminder."""
    
    def test_create_reminder(self, db_session, test_user):
        """Создание напоминания."""
        reminder = Reminder(
            user_id=test_user.id,
            reminder_time="21:30",
            message="Готовимся ко сну",
            is_active=1
        )
        db_session.add(reminder)
        db_session.commit()
        
        assert reminder.id is not None
        assert reminder.reminder_time == "21:30"
        assert reminder.is_active == 1
    
    def test_reminder_default_is_active(self, db_session, test_user):
        """Значение по умолчанию для is_active."""
        reminder = Reminder(
            user_id=test_user.id,
            reminder_time="22:00"
        )
        db_session.add(reminder)
        db_session.commit()
        
        assert reminder.is_active == 1
    
    def test_reminder_user_relationship(self, db_session, test_reminder, test_user):
        """Проверка связи с пользователем."""
        assert test_reminder.user.id == test_user.id


class TestNoteModel:
    """Тесты для модели Note."""
    
    def test_create_note(self, db_session, test_sleep_record):
        """Создание заметки."""
        note = Note(
            sleep_record_id=test_sleep_record.id,
            content="Отличный сон!"
        )
        db_session.add(note)
        db_session.commit()
        
        assert note.id is not None
        assert note.content == "Отличный сон!"
    
    def test_note_sleep_record_relationship(self, db_session, test_note, test_sleep_record):
        """Проверка связи с записью о сне."""
        assert test_note.sleep_record.id == test_sleep_record.id
    
    def test_note_cascade_delete(self, db_session, test_sleep_record, test_note):
        """Каскадное удаление заметок при удалении записи о сне."""
        note_id = test_note.id
        
        db_session.delete(test_sleep_record)
        db_session.commit()
        
        deleted_note = db_session.query(Note).filter_by(id=note_id).first()
        assert deleted_note is None
