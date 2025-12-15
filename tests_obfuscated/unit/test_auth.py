"""
Unit-тесты для модуля аутентификации (app/auth.py).
Тестируют функции хеширования паролей, создания и проверки токенов.
"""
import pytest
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError

from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)


class TestPasswordHashing:
    """Тесты для функций хеширования паролей."""
    
    def test_get_password_hash_returns_string(self):
        """Функция хеширования должна возвращать строку."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_get_password_hash_different_from_plain(self):
        """Хеш должен отличаться от исходного пароля."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
    
    def test_get_password_hash_unique_salts(self):
        """Каждый хеш должен быть уникальным (разные соли)."""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
    
    def test_verify_password_correct(self):
        """Проверка корректного пароля должна возвращать True."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Проверка некорректного пароля должна возвращать False."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty_string(self):
        """Проверка пустого пароля против хеша."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password("", hashed) is False
    
    def test_hash_empty_password(self):
        """Хеширование пустого пароля должно работать."""
        password = ""
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_hash_special_characters(self):
        """Хеширование пароля со спецсимволами."""
        password = "p@$$w0rd!@#$%^&*()"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_hash_unicode_password(self):
        """Хеширование пароля с Unicode символами."""
        password = "пароль123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True


class TestAccessToken:
    """Тесты для функций создания и проверки JWT токенов."""
    
    def test_create_access_token_returns_string(self):
        """Функция должна возвращать строку токена."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_contains_username(self):
        """Токен должен содержать имя пользователя."""
        username = "testuser"
        token = create_access_token(data={"sub": username})
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload.get("sub") == username
    
    def test_create_access_token_has_expiration(self):
        """Токен должен иметь время истечения."""
        token = create_access_token(data={"sub": "testuser"})
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload
    
    def test_create_access_token_expiration_time(self):
        """Время истечения должно быть в будущем (около 60 минут)."""
        before = datetime.now(timezone.utc)
        token = create_access_token(data={"sub": "testuser"})
        after = datetime.now(timezone.utc)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        
        # Проверяем, что истекает примерно через 60 минут
        expected_min = before + timedelta(minutes=59)
        expected_max = after + timedelta(minutes=61)
        
        assert expected_min <= exp_time <= expected_max
    
    def test_token_decode_invalid_signature(self):
        """Токен с неверной подписью не должен декодироваться."""
        token = create_access_token(data={"sub": "testuser"})
        
        with pytest.raises(JWTError):
            jwt.decode(token, "wrong_secret_key", algorithms=[ALGORITHM])
    
    def test_token_decode_invalid_algorithm(self):
        """Токен с неверным алгоритмом не должен декодироваться."""
        token = create_access_token(data={"sub": "testuser"})
        
        with pytest.raises(JWTError):
            jwt.decode(token, SECRET_KEY, algorithms=["HS384"])
    
    def test_create_token_with_additional_data(self):
        """Токен с дополнительными данными должен содержать их."""
        data = {"sub": "testuser", "role": "admin", "extra": "value"}
        token = create_access_token(data=data)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload.get("sub") == "testuser"
        assert payload.get("role") == "admin"
        assert payload.get("extra") == "value"
    
    def test_original_data_not_modified(self):
        """Исходный словарь данных не должен изменяться."""
        data = {"sub": "testuser"}
        original_data = data.copy()
        
        create_access_token(data=data)
        
        assert data == original_data
        assert "exp" not in data
