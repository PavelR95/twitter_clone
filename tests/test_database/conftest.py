import pytest_asyncio

from app.application.settings import settings
from app.application.models.core import SQLManager
from app.application.models.models import Users

_sql_manager = SQLManager(settings.DATABASE_URL_TEST)


@pytest_asyncio.fixture
async def sql_manager():
    """Подготавливает базу данных для тестирования
    генерирует менеджер SQL запросов

    Yields:
        SQLManager: менеджер SQL запросов
    """
    await _sql_manager.drop_all_table()
    await _sql_manager.initial_database()
    test_user = Users()
    test_user.name = "TestUser"
    test_user.api_key = "test"
    await _sql_manager.add(test_user)
    test_user_2 = Users()
    test_user_2.name = "TestUser2"
    test_user_2.api_key = "test2"
    await _sql_manager.add(test_user_2)
    yield _sql_manager
    await _sql_manager.close()
