"""
Интеграционные тесты для API endpoints напоминаний (app/routes/reminder.py).
"""
import pytest
from fastapi import status


class TestCreateReminder:
    """Тесты создания напоминаний."""
    
    def test_create_reminder_success(self, client, auth_headers):
        """Успешное создание напоминания."""
        response = client.post(
            "/api/reminders",
            headers=auth_headers,
            json={
                "reminder_time": "22:00",
                "message": "Пора спать!"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["reminder_time"] == "22:00"
        assert data["message"] == "Пора спать!"
        assert data["is_active"] == 1
    
    def test_create_reminder_without_message(self, client, auth_headers):
        """Создание напоминания без сообщения."""
        response = client.post(
            "/api/reminders",
            headers=auth_headers,
            json={
                "reminder_time": "21:30"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["message"] is None
        assert data["is_active"] == 1
    
    def test_create_reminder_unauthorized(self, client):
        """Создание напоминания без авторизации."""
        response = client.post(
            "/api/reminders",
            json={
                "reminder_time": "22:00",
                "message": "Пора спать!"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_reminder_empty_time(self, client, auth_headers):
        """Создание напоминания с пустым временем."""
        response = client.post(
            "/api/reminders",
            headers=auth_headers,
            json={
                "reminder_time": "",
                "message": "Пора спать!"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_multiple_reminders(self, client, auth_headers):
        """Создание нескольких напоминаний."""
        # Первое напоминание
        response1 = client.post(
            "/api/reminders",
            headers=auth_headers,
            json={"reminder_time": "21:00"}
        )
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Второе напоминание
        response2 = client.post(
            "/api/reminders",
            headers=auth_headers,
            json={"reminder_time": "22:00"}
        )
        assert response2.status_code == status.HTTP_201_CREATED
        
        # Проверяем, что это разные напоминания
        assert response1.json()["id"] != response2.json()["id"]


class TestUpdateReminder:
    """Тесты обновления напоминаний."""
    
    def test_update_reminder_time(self, client, auth_headers, test_reminder):
        """Обновление времени напоминания."""
        response = client.put(
            f"/api/reminders/{test_reminder.id}",
            headers=auth_headers,
            json={"reminder_time": "23:00"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["reminder_time"] == "23:00"
    
    def test_update_reminder_message(self, client, auth_headers, test_reminder):
        """Обновление сообщения напоминания."""
        response = client.put(
            f"/api/reminders/{test_reminder.id}",
            headers=auth_headers,
            json={"message": "Новое сообщение"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Новое сообщение"
    
    def test_update_reminder_deactivate(self, client, auth_headers, test_reminder):
        """Деактивация напоминания."""
        response = client.put(
            f"/api/reminders/{test_reminder.id}",
            headers=auth_headers,
            json={"is_active": 0}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_active"] == 0
    
    def test_update_reminder_activate(self, client, auth_headers, db_session, test_user):
        """Активация напоминания."""
        from app.models import Reminder
        
        # Создаем неактивное напоминание
        reminder = Reminder(
            user_id=test_user.id,
            reminder_time="20:00",
            is_active=0
        )
        db_session.add(reminder)
        db_session.commit()
        db_session.refresh(reminder)
        
        response = client.put(
            f"/api/reminders/{reminder.id}",
            headers=auth_headers,
            json={"is_active": 1}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_active"] == 1
    
    def test_update_reminder_all_fields(self, client, auth_headers, test_reminder):
        """Обновление всех полей напоминания."""
        response = client.put(
            f"/api/reminders/{test_reminder.id}",
            headers=auth_headers,
            json={
                "reminder_time": "19:30",
                "message": "Готовимся ко сну заранее",
                "is_active": 1
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["reminder_time"] == "19:30"
        assert data["message"] == "Готовимся ко сну заранее"
        assert data["is_active"] == 1
    
    def test_update_nonexistent_reminder(self, client, auth_headers):
        """Обновление несуществующего напоминания."""
        response = client.put(
            "/api/reminders/99999",
            headers=auth_headers,
            json={"reminder_time": "23:00"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_reminder_unauthorized(self, client, test_reminder):
        """Обновление напоминания без авторизации."""
        response = client.put(
            f"/api/reminders/{test_reminder.id}",
            json={"reminder_time": "23:00"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_reminder_invalid_is_active(self, client, auth_headers, test_reminder):
        """Обновление с невалидным значением is_active."""
        response = client.put(
            f"/api/reminders/{test_reminder.id}",
            headers=auth_headers,
            json={"is_active": 5}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_other_user_reminder(self, client, test_reminder, test_user2):
        """Обновление напоминания другого пользователя."""
        from app.auth import create_access_token
        token = create_access_token(data={"sub": test_user2.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.put(
            f"/api/reminders/{test_reminder.id}",
            headers=headers,
            json={"reminder_time": "23:00"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteReminder:
    """Тесты удаления напоминаний."""
    
    def test_delete_reminder_success(self, client, auth_headers, test_reminder):
        """Успешное удаление (деактивация) напоминания."""
        response = client.delete(
            f"/api/reminders/{test_reminder.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_delete_nonexistent_reminder(self, client, auth_headers):
        """Удаление несуществующего напоминания."""
        response = client.delete("/api/reminders/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_reminder_unauthorized(self, client, test_reminder):
        """Удаление напоминания без авторизации."""
        response = client.delete(f"/api/reminders/{test_reminder.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_other_user_reminder(self, client, test_reminder, test_user2):
        """Удаление напоминания другого пользователя."""
        from app.auth import create_access_token
        token = create_access_token(data={"sub": test_user2.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete(
            f"/api/reminders/{test_reminder.id}",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
