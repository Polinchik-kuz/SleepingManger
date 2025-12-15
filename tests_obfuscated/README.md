# Тесты для обфусцированного кода

Эта папка содержит тесты для обфусцированной версии проекта, расположенной в `dist/app/`.

## Структура

```
tests_obfuscated/
├── conftest.py           # Фикстуры и настройки pytest (с путем к dist/app)
├── unit/                 # Unit-тесты
│   ├── test_auth.py
│   ├── test_models.py
│   └── test_schemas.py
└── integration/          # Интеграционные тесты
    ├── test_user_api.py
    ├── test_sleep_api.py
    ├── test_goal_api.py
    ├── test_reminder_api.py
    └── test_analytics_api.py
```

## Запуск тестов

### Все тесты обфусцированного кода:
```powershell
pytest -c pytest_obfuscated.ini
```

### Только unit-тесты:
```powershell
pytest -c pytest_obfuscated.ini tests_obfuscated/unit/
```

### Только интеграционные тесты:
```powershell
pytest -c pytest_obfuscated.ini tests_obfuscated/integration/
```

### Конкретный файл:
```powershell
pytest -c pytest_obfuscated.ini tests_obfuscated/unit/test_auth.py
```

### С покрытием кода:
```powershell
pytest -c pytest_obfuscated.ini --cov=dist.app --cov-report=html
```

## Важные замечания

1. **Обфусцированный код должен существовать**: Убедитесь, что папка `dist/app/` содержит обфусцированный код
2. **Pyarmor runtime**: Runtime библиотеки должны быть в `dist/app/pyarmor_runtime_000000/`
3. **Виртуальное окружение**: Используйте то же виртуальное окружение `.venv`, что и для основного проекта
4. **Перед тестированием**: Рекомендуется сначала протестировать оригинальный код в `tests/`

## Отличия от обычных тестов

- `conftest.py` добавляет путь `dist/app/` в `sys.path`
- Все импорты остаются `from app.*`, но указывают на обфусцированный код
- Используется отдельный файл конфигурации `pytest_obfuscated.ini`

## Рекомендуемый workflow

1. Разработка и тестирование на оригинальном коде:
   ```powershell
   pytest
   ```

2. Обфускация после успешных тестов:
   ```powershell
   pyarmor gen --output dist app
   ```

3. Проверка обфусцированного кода:
   ```powershell
   pytest -c pytest_obfuscated.ini
   ```
