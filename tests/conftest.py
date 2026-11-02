import pytest_asyncio
from httpx import AsyncClient

from core.config import settings


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        base_url=f"http://127.0.0.0:{settings.port}"
    ) as test_client:
        yield test_client