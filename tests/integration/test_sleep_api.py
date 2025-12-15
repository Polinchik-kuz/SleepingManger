"""
Интеграционные тесты для API endpoints записей о сне (app/routes/sleep.py).
"""
import pytest
from fastapi import status
from datetime import datetime, timezone, timedelta


class TestCreateSleepRecord:
    """Тесты создания записей о сне."""
    
    def test_create_sleep_record_success(self, client, auth_headers):
        """Успешное создание записи о сне."""
        sleep_start = (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat()
        sleep_end = datetime.now(timezone.utc).isoformat()
        
        response = client.post(
            "/api/sleep",
            headers=auth_headers,
            json={
                "sleep_start": sleep_start,
                "sleep_end": sleep_end,
                "quality": 7,
                "deep_sleep": 2.5,
                "light_sleep": 4.0,
                "rem_sleep": 1.5
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["quality"] == 7
        assert data["deep_sleep"] == 2.5
        assert data["duration"] == pytest.approx(8.0, rel=0.1)
    
    def test_create_sleep_record_minimal(self, client, auth_headers):
        """Создание записи с минимальными данными."""
        sleep_start = (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
        sleep_end = datetime.now(timezone.utc).isoformat()
        
        response = client.post(
            "/api/sleep",
            headers=auth_headers,
            json={
                "sleep_start": sleep_start,
                "sleep_end": sleep_end,
                "quality": 5
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["deep_sleep"] is None
        assert data["light_sleep"] is None
        assert data["rem_sleep"] is None
    
    def test_create_sleep_record_unauthorized(self, client):
        """Создание записи без авторизации."""
        sleep_start = (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat()
        sleep_end = datetime.now(timezone.utc).isoformat()
        
        response = client.post(
            "/api/sleep",
            json={
                "sleep_start": sleep_start,
                "sleep_end": sleep_end,
                "quality": 7
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_sleep_record_invalid_quality(self, client, auth_headers):
        """Создание записи с невалидным качеством."""
        sleep_start = (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat()
        sleep_end = datetime.now(timezone.utc).isoformat()
        
        response = client.post(
            "/api/sleep",
            headers=auth_headers,
            json={
                "sleep_start": sleep_start,
                "sleep_end": sleep_end,
                "quality": 11  # Max is 10
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_sleep_record_end_before_start(self, client, auth_headers):
        """Создание записи с окончанием раньше начала."""
        sleep_start = datetime.now(timezone.utc).isoformat()
        sleep_end = (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat()
        
        response = client.post(
            "/api/sleep",
            headers=auth_headers,
            json={
                "sleep_start": sleep_start,
                "sleep_end": sleep_end,
                "quality": 7
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetSleepRecords:
    """Тесты получения записей о сне."""
    
    def test_get_all_sleep_records(self, client, auth_headers, test_sleep_record):
        """Получение всех записей о сне."""
        response = client.get("/api/sleep", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_all_sleep_records_empty(self, client, auth_headers):
        """Получение записей когда их нет."""
        response = client.get("/api/sleep", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []
    
    def test_get_single_sleep_record(self, client, auth_headers, test_sleep_record):
        """Получение одной записи о сне."""
        response = client.get(
            f"/api/sleep/{test_sleep_record.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_sleep_record.id
        assert data["quality"] == test_sleep_record.quality
    
    def test_get_nonexistent_sleep_record(self, client, auth_headers):
        """Получение несуществующей записи."""
        response = client.get("/api/sleep/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_sleep_record_unauthorized(self, client, test_sleep_record):
        """Получение записи без авторизации."""
        response = client.get(f"/api/sleep/{test_sleep_record.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_other_user_sleep_record(self, client, test_sleep_record, test_user2):
        """Получение записи другого пользователя."""
        from app.auth import create_access_token
        token = create_access_token(data={"sub": test_user2.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(
            f"/api/sleep/{test_sleep_record.id}",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateSleepRecord:
    """Тесты обновления записей о сне."""
    
    def test_update_sleep_record_quality(self, client, auth_headers, test_sleep_record):
        """Обновление качества сна."""
        response = client.put(
            f"/api/sleep/{test_sleep_record.id}",
            headers=auth_headers,
            json={"quality": 9}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["quality"] == 9
    
    def test_update_sleep_record_times(self, client, auth_headers, test_sleep_record):
        """Обновление времени сна."""
        new_start = (datetime.now(timezone.utc) - timedelta(hours=10)).isoformat()
        new_end = datetime.now(timezone.utc).isoformat()
        
        response = client.put(
            f"/api/sleep/{test_sleep_record.id}",
            headers=auth_headers,
            json={
                "sleep_start": new_start,
                "sleep_end": new_end
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["duration"] == pytest.approx(10.0, rel=0.1)
    
    def test_update_sleep_record_deep_sleep(self, client, auth_headers, test_sleep_record):
        """Обновление глубокого сна."""
        response = client.put(
            f"/api/sleep/{test_sleep_record.id}",
            headers=auth_headers,
            json={"deep_sleep": 3.0}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["deep_sleep"] == 3.0
    
    def test_update_nonexistent_sleep_record(self, client, auth_headers):
        """Обновление несуществующей записи."""
        response = client.put(
            "/api/sleep/99999",
            headers=auth_headers,
            json={"quality": 9}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_sleep_record_invalid_quality(self, client, auth_headers, test_sleep_record):
        """Обновление с невалидным качеством."""
        response = client.put(
            f"/api/sleep/{test_sleep_record.id}",
            headers=auth_headers,
            json={"quality": 0}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDeleteSleepRecord:
    """Тесты удаления записей о сне."""
    
    def test_delete_sleep_record_success(self, client, auth_headers, test_sleep_record):
        """Успешное удаление записи."""
        response = client.delete(
            f"/api/sleep/{test_sleep_record.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Проверяем, что запись удалена
        response = client.get(
            f"/api/sleep/{test_sleep_record.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_nonexistent_sleep_record(self, client, auth_headers):
        """Удаление несуществующей записи."""
        response = client.delete("/api/sleep/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_sleep_record_unauthorized(self, client, test_sleep_record):
        """Удаление записи без авторизации."""
        response = client.delete(f"/api/sleep/{test_sleep_record.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSleepNotes:
    """Тесты для заметок к записям о сне."""
    
    def test_create_note_success(self, client, auth_headers, test_sleep_record):
        """Успешное создание заметки."""
        response = client.post(
            f"/api/sleep/{test_sleep_record.id}/note",
            headers=auth_headers,
            json={"content": "Хорошо выспался!"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["content"] == "Хорошо выспался!"
        assert data["sleep_record_id"] == test_sleep_record.id
    
    def test_create_note_for_nonexistent_record(self, client, auth_headers):
        """Создание заметки для несуществующей записи."""
        response = client.post(
            "/api/sleep/99999/note",
            headers=auth_headers,
            json={"content": "Тестовая заметка"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_note_empty_content(self, client, auth_headers, test_sleep_record):
        """Создание заметки с пустым содержимым."""
        response = client.post(
            f"/api/sleep/{test_sleep_record.id}/note",
            headers=auth_headers,
            json={"content": ""}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_note_unauthorized(self, client, test_sleep_record):
        """Создание заметки без авторизации."""
        response = client.post(
            f"/api/sleep/{test_sleep_record.id}/note",
            json={"content": "Тестовая заметка"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
