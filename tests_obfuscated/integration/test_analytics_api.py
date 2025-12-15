"""
Интеграционные тесты для API endpoints аналитики (app/routes/analytics.py).
"""
import pytest
from fastapi import status


class TestStatistics:
    """Тесты статистики."""
    
    def test_get_statistics_no_data(self, client, auth_headers):
        """Получение статистики без данных."""
        response = client.get("/api/statistics", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_records"] == 0
        assert "message" in data
    
    def test_get_statistics_with_data(self, client, auth_headers, multiple_sleep_records):
        """Получение статистики с данными."""
        response = client.get("/api/statistics", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_records"] == 5
        assert "average_duration" in data
        assert "average_quality" in data
        assert "max_duration" in data
        assert "min_duration" in data
    
    def test_get_statistics_calculations(self, client, auth_headers, multiple_sleep_records):
        """Проверка правильности вычислений статистики."""
        response = client.get("/api/statistics", headers=auth_headers)
        
        data = response.json()
        
        # Записи имеют duration: 6.0, 6.5, 7.0, 7.5, 8.0
        expected_avg_duration = (6.0 + 6.5 + 7.0 + 7.5 + 8.0) / 5
        assert data["average_duration"] == pytest.approx(expected_avg_duration, rel=0.01)
        assert data["max_duration"] == 8.0
        assert data["min_duration"] == 6.0
        
        # Записи имеют quality: 5, 6, 7, 8, 9
        expected_avg_quality = (5 + 6 + 7 + 8 + 9) / 5
        assert data["average_quality"] == pytest.approx(expected_avg_quality, rel=0.01)
    
    def test_get_statistics_unauthorized(self, client):
        """Получение статистики без авторизации."""
        response = client.get("/api/statistics")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_statistics_single_record(self, client, auth_headers, test_sleep_record):
        """Статистика с одной записью."""
        response = client.get("/api/statistics", headers=auth_headers)
        
        data = response.json()
        assert data["total_records"] == 1
        assert data["average_duration"] == test_sleep_record.duration
        assert data["average_quality"] == test_sleep_record.quality
        assert data["max_duration"] == test_sleep_record.duration
        assert data["min_duration"] == test_sleep_record.duration


class TestRecommendations:
    """Тесты рекомендаций."""
    
    def test_get_recommendations_no_data(self, client, auth_headers):
        """Получение рекомендаций без данных."""
        response = client.get("/api/recommendations", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "recommendations" in data
        assert len(data["recommendations"]) >= 1
        assert "Начните записывать свой сон" in data["recommendations"][0]
    
    def test_get_recommendations_with_data(self, client, auth_headers, multiple_sleep_records):
        """Получение рекомендаций с данными."""
        response = client.get("/api/recommendations", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "recommendations" in data
        assert "average_duration" in data
        assert "average_quality" in data
        assert len(data["recommendations"]) >= 1
    
    def test_get_recommendations_short_sleep(self, client, auth_headers, db_session, test_user):
        """Рекомендации при коротком сне."""
        from app.models import SleepRecord
        from datetime import datetime, timezone, timedelta
        
        # Создаем записи с коротким сном (< 7 часов)
        for i in range(3):
            sleep_start = datetime.now(timezone.utc) - timedelta(days=i, hours=5)
            sleep_end = datetime.now(timezone.utc) - timedelta(days=i)
            record = SleepRecord(
                user_id=test_user.id,
                sleep_start=sleep_start,
                sleep_end=sleep_end,
                duration=5.0,
                quality=6
            )
            db_session.add(record)
        db_session.commit()
        
        response = client.get("/api/recommendations", headers=auth_headers)
        
        data = response.json()
        # Проверяем, что есть рекомендация про 7-8 часов сна
        recommendations_text = " ".join(data["recommendations"])
        assert "7" in recommendations_text or "8" in recommendations_text
    
    def test_get_recommendations_long_sleep(self, client, auth_headers, db_session, test_user):
        """Рекомендации при слишком долгом сне."""
        from app.models import SleepRecord
        from datetime import datetime, timezone, timedelta
        
        # Создаем записи с долгим сном (> 9 часов)
        for i in range(3):
            sleep_start = datetime.now(timezone.utc) - timedelta(days=i, hours=10)
            sleep_end = datetime.now(timezone.utc) - timedelta(days=i)
            record = SleepRecord(
                user_id=test_user.id,
                sleep_start=sleep_start,
                sleep_end=sleep_end,
                duration=10.0,
                quality=7
            )
            db_session.add(record)
        db_session.commit()
        
        response = client.get("/api/recommendations", headers=auth_headers)
        
        data = response.json()
        # Проверяем, что есть рекомендация про сокращение сна
        recommendations_text = " ".join(data["recommendations"])
        assert "много" in recommendations_text.lower() or "сократить" in recommendations_text.lower()
    
    def test_get_recommendations_low_quality(self, client, auth_headers, db_session, test_user):
        """Рекомендации при низком качестве сна."""
        from app.models import SleepRecord
        from datetime import datetime, timezone, timedelta
        
        # Создаем записи с низким качеством сна (< 5)
        for i in range(3):
            sleep_start = datetime.now(timezone.utc) - timedelta(days=i, hours=8)
            sleep_end = datetime.now(timezone.utc) - timedelta(days=i)
            record = SleepRecord(
                user_id=test_user.id,
                sleep_start=sleep_start,
                sleep_end=sleep_end,
                duration=8.0,
                quality=3
            )
            db_session.add(record)
        db_session.commit()
        
        response = client.get("/api/recommendations", headers=auth_headers)
        
        data = response.json()
        # Проверяем, что есть рекомендации по улучшению качества
        recommendations_text = " ".join(data["recommendations"]).lower()
        assert "качество" in recommendations_text or "проветривать" in recommendations_text or "гаджет" in recommendations_text
    
    def test_get_recommendations_unauthorized(self, client):
        """Получение рекомендаций без авторизации."""
        response = client.get("/api/recommendations")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_recommendations_good_sleep(self, client, auth_headers, db_session, test_user):
        """Рекомендации при хорошем сне."""
        from app.models import SleepRecord
        from datetime import datetime, timezone, timedelta
        
        # Создаем записи с хорошим сном
        for i in range(3):
            sleep_start = datetime.now(timezone.utc) - timedelta(days=i, hours=8)
            sleep_end = datetime.now(timezone.utc) - timedelta(days=i)
            record = SleepRecord(
                user_id=test_user.id,
                sleep_start=sleep_start,
                sleep_end=sleep_end,
                duration=8.0,
                quality=9
            )
            db_session.add(record)
        db_session.commit()
        
        response = client.get("/api/recommendations", headers=auth_headers)
        
        data = response.json()
        # Проверяем, что есть положительные отзывы
        recommendations_text = " ".join(data["recommendations"]).lower()
        assert "отлично" in recommendations_text or "продолжайте" in recommendations_text


class TestUserIsolation:
    """Тесты изоляции данных между пользователями."""
    
    def test_statistics_user_isolation(self, client, auth_headers, test_sleep_record, test_user2, db_session):
        """Статистика показывает только данные текущего пользователя."""
        from app.models import SleepRecord
        from datetime import datetime, timezone, timedelta
        
        # Создаем запись для второго пользователя
        sleep_start = datetime.now(timezone.utc) - timedelta(hours=6)
        sleep_end = datetime.now(timezone.utc)
        other_record = SleepRecord(
            user_id=test_user2.id,
            sleep_start=sleep_start,
            sleep_end=sleep_end,
            duration=6.0,
            quality=5
        )
        db_session.add(other_record)
        db_session.commit()
        
        # Проверяем статистику первого пользователя
        response = client.get("/api/statistics", headers=auth_headers)
        data = response.json()
        
        # Должна быть только одна запись (test_sleep_record)
        assert data["total_records"] == 1
        assert data["average_duration"] == test_sleep_record.duration
    
    def test_recommendations_user_isolation(self, client, auth_headers, test_sleep_record, test_user2, db_session):
        """Рекомендации основаны только на данных текущего пользователя."""
        from app.auth import create_access_token
        from app.models import SleepRecord
        from datetime import datetime, timezone, timedelta
        
        # Создаем записи для второго пользователя с плохим качеством
        for i in range(3):
            sleep_start = datetime.now(timezone.utc) - timedelta(days=i, hours=4)
            sleep_end = datetime.now(timezone.utc) - timedelta(days=i)
            record = SleepRecord(
                user_id=test_user2.id,
                sleep_start=sleep_start,
                sleep_end=sleep_end,
                duration=4.0,
                quality=2
            )
            db_session.add(record)
        db_session.commit()
        
        # Получаем рекомендации для второго пользователя
        token = create_access_token(data={"sub": test_user2.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/recommendations", headers=headers)
        data = response.json()
        
        # Рекомендации должны отражать плохой сон второго пользователя
        assert data["average_duration"] == pytest.approx(4.0, rel=0.1)
        assert data["average_quality"] == pytest.approx(2.0, rel=0.1)
