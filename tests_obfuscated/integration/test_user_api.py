"""
Интеграционные тесты для API endpoints пользователей (app/routes/user.py).
"""
import pytest
from fastapi import status


class TestUserRegistration:
    """Тесты регистрации пользователя."""
    
    def test_register_user_success(self, client):
        """Успешная регистрация нового пользователя."""
        response = client.post(
            "/api/users/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123",
                "age": 25
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["age"] == 25
        assert "id" in data
        assert "password" not in data
    
    def test_register_user_without_age(self, client):
        """Регистрация без указания возраста."""
        response = client.post(
            "/api/users/register",
            json={
                "username": "noageuser",
                "email": "noage@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["age"] is None
    
    def test_register_user_duplicate_username(self, client, test_user):
        """Регистрация с уже существующим именем пользователя."""
        response = client.post(
            "/api/users/register",
            json={
                "username": test_user.username,
                "email": "other@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "уже существует" in response.json()["detail"]
    
    def test_register_user_duplicate_email(self, client, test_user):
        """Регистрация с уже существующим email."""
        response = client.post(
            "/api/users/register",
            json={
                "username": "uniqueuser",
                "email": test_user.email,
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "Email уже используется" in response.json()["detail"]
    
    def test_register_user_invalid_email(self, client):
        """Регистрация с невалидным email."""
        response = client.post(
            "/api/users/register",
            json={
                "username": "testuser",
                "email": "invalid-email",
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_user_short_password(self, client):
        """Регистрация со слишком коротким паролем."""
        response = client.post(
            "/api/users/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "12345"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_user_short_username(self, client):
        """Регистрация со слишком коротким именем пользователя."""
        response = client.post(
            "/api/users/register",
            json={
                "username": "ab",
                "email": "test@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """Тесты входа в систему."""
    
    def test_login_success(self, client, test_user):
        """Успешный вход."""
        response = client.post(
            "/api/users/login",
            json={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, test_user):
        """Вход с неверным паролем."""
        response = client.post(
            "/api/users/login",
            json={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Неверное имя пользователя или пароль" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client):
        """Вход несуществующего пользователя."""
        response = client.post(
            "/api/users/login",
            json={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_empty_credentials(self, client):
        """Вход с пустыми данными."""
        response = client.post(
            "/api/users/login",
            json={
                "username": "",
                "password": ""
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserProfile:
    """Тесты работы с профилем пользователя."""
    
    def test_get_profile_success(self, client, test_user, auth_headers):
        """Успешное получение профиля."""
        response = client.get("/api/users/profile", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
    
    def test_get_profile_unauthorized(self, client):
        """Получение профиля без авторизации."""
        response = client.get("/api/users/profile")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_profile_invalid_token(self, client):
        """Получение профиля с невалидным токеном."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/users/profile", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_profile_email(self, client, test_user, auth_headers):
        """Обновление email профиля."""
        response = client.put(
            "/api/users/profile",
            headers=auth_headers,
            json={"email": "newemail@example.com"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "newemail@example.com"
    
    def test_update_profile_age(self, client, test_user, auth_headers):
        """Обновление возраста."""
        response = client.put(
            "/api/users/profile",
            headers=auth_headers,
            json={"age": 30}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["age"] == 30
    
    def test_update_profile_duplicate_email(self, client, test_user, test_user2, auth_headers):
        """Обновление email на уже занятый."""
        response = client.put(
            "/api/users/profile",
            headers=auth_headers,
            json={"email": test_user2.email}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email уже используется" in response.json()["detail"]
    
    def test_update_profile_invalid_age(self, client, test_user, auth_headers):
        """Обновление с невалидным возрастом."""
        response = client.put(
            "/api/users/profile",
            headers=auth_headers,
            json={"age": 0}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_delete_profile(self, client, test_user, auth_headers):
        """Удаление профиля."""
        response = client.delete("/api/users/profile", headers=auth_headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Проверяем, что пользователь удален
        response = client.get("/api/users/profile", headers=auth_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_profile_unauthorized(self, client):
        """Удаление профиля без авторизации."""
        response = client.delete("/api/users/profile")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRootEndpoint:
    """Тесты корневого endpoint."""
    
    def test_root_endpoint(self, client):
        """Проверка корневого endpoint."""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "docs" in data
        assert "version" in data
