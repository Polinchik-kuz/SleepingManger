"""
Интеграционные тесты для API endpoints целей (app/routes/goal.py).
"""
import pytest
from fastapi import status


class TestCreateGoal:
    """Тесты создания целей."""
    
    def test_create_goal_success(self, client, auth_headers):
        """Успешное создание цели."""
        response = client.post(
            "/api/goals",
            headers=auth_headers,
            json={
                "target_duration": 8.0,
                "target_quality": 8,
                "description": "Спать не менее 8 часов"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["target_duration"] == 8.0
        assert data["target_quality"] == 8
        assert data["description"] == "Спать не менее 8 часов"
    
    def test_create_goal_without_description(self, client, auth_headers):
        """Создание цели без описания."""
        response = client.post(
            "/api/goals",
            headers=auth_headers,
            json={
                "target_duration": 7.5,
                "target_quality": 7
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["description"] is None
    
    def test_create_goal_unauthorized(self, client):
        """Создание цели без авторизации."""
        response = client.post(
            "/api/goals",
            json={
                "target_duration": 8.0,
                "target_quality": 8
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_goal_invalid_duration(self, client, auth_headers):
        """Создание цели с невалидной продолжительностью."""
        response = client.post(
            "/api/goals",
            headers=auth_headers,
            json={
                "target_duration": 25.0,  # Max is 24
                "target_quality": 8
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_goal_invalid_quality(self, client, auth_headers):
        """Создание цели с невалидным качеством."""
        response = client.post(
            "/api/goals",
            headers=auth_headers,
            json={
                "target_duration": 8.0,
                "target_quality": 11  # Max is 10
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_goal_negative_duration(self, client, auth_headers):
        """Создание цели с отрицательной продолжительностью."""
        response = client.post(
            "/api/goals",
            headers=auth_headers,
            json={
                "target_duration": -1.0,
                "target_quality": 8
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetGoals:
    """Тесты получения целей."""
    
    def test_get_all_goals(self, client, auth_headers, test_goal):
        """Получение всех целей."""
        response = client.get("/api/goals", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_all_goals_empty(self, client, auth_headers):
        """Получение целей когда их нет."""
        response = client.get("/api/goals", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []
    
    def test_get_single_goal(self, client, auth_headers, test_goal):
        """Получение одной цели."""
        response = client.get(
            f"/api/goals/{test_goal.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_goal.id
        assert data["target_duration"] == test_goal.target_duration
    
    def test_get_nonexistent_goal(self, client, auth_headers):
        """Получение несуществующей цели."""
        response = client.get("/api/goals/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_goal_unauthorized(self, client, test_goal):
        """Получение цели без авторизации."""
        response = client.get(f"/api/goals/{test_goal.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_other_user_goal(self, client, test_goal, test_user2):
        """Получение цели другого пользователя."""
        from app.auth import create_access_token
        token = create_access_token(data={"sub": test_user2.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/api/goals/{test_goal.id}", headers=headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateGoal:
    """Тесты обновления целей."""
    
    def test_update_goal_duration(self, client, auth_headers, test_goal):
        """Обновление продолжительности цели."""
        response = client.put(
            f"/api/goals/{test_goal.id}",
            headers=auth_headers,
            json={"target_duration": 9.0}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["target_duration"] == 9.0
    
    def test_update_goal_quality(self, client, auth_headers, test_goal):
        """Обновление качества цели."""
        response = client.put(
            f"/api/goals/{test_goal.id}",
            headers=auth_headers,
            json={"target_quality": 10}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["target_quality"] == 10
    
    def test_update_goal_description(self, client, auth_headers, test_goal):
        """Обновление описания цели."""
        response = client.put(
            f"/api/goals/{test_goal.id}",
            headers=auth_headers,
            json={"description": "Новое описание цели"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Новое описание цели"
    
    def test_update_goal_all_fields(self, client, auth_headers, test_goal):
        """Обновление всех полей цели."""
        response = client.put(
            f"/api/goals/{test_goal.id}",
            headers=auth_headers,
            json={
                "target_duration": 7.0,
                "target_quality": 9,
                "description": "Полностью обновленная цель"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["target_duration"] == 7.0
        assert data["target_quality"] == 9
        assert data["description"] == "Полностью обновленная цель"
    
    def test_update_nonexistent_goal(self, client, auth_headers):
        """Обновление несуществующей цели."""
        response = client.put(
            "/api/goals/99999",
            headers=auth_headers,
            json={"target_quality": 9}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_goal_invalid_duration(self, client, auth_headers, test_goal):
        """Обновление с невалидной продолжительностью."""
        response = client.put(
            f"/api/goals/{test_goal.id}",
            headers=auth_headers,
            json={"target_duration": -5.0}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDeleteGoal:
    """Тесты удаления целей."""
    
    def test_delete_goal_success(self, client, auth_headers, test_goal):
        """Успешное удаление цели."""
        response = client.delete(
            f"/api/goals/{test_goal.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Проверяем, что цель удалена
        response = client.get(
            f"/api/goals/{test_goal.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_nonexistent_goal(self, client, auth_headers):
        """Удаление несуществующей цели."""
        response = client.delete("/api/goals/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_goal_unauthorized(self, client, test_goal):
        """Удаление цели без авторизации."""
        response = client.delete(f"/api/goals/{test_goal.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
