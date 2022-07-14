import asyncio

import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager

from app.main import app
from app.models.models import CardTortoise, CollectionTortoise

test_user_1 = {
    'email': 'user1@example.com',
    'name': 'user1',
    'password': 'pass1'
}

test_user_2 = {
    'email': 'user2@example.com',
    'name': 'user2',
    'password': 'pass2'
}

test_collection_1 = {
    'title': 'test collection 1',
    'description': 'test description 1',
    'is_private': True
}

test_collection_2 = {
    'title': 'test collection 2',
    'description': 'test description 2',
    'is_private': False
}

test_card = {
    'title': 'test card with collections',
    'content': 'test content',
    'collections': []
}


@pytest.fixture(scope='session')
def event_loop():
    """Create and get event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def test_client():
    """Get test client."""
    async with LifespanManager(app):
        async with httpx.AsyncClient(app=app,
                                     base_url='http://app.io') as test_client:
            yield test_client


@pytest_asyncio.fixture(scope='module', autouse=True)
async def clear_db():
    """Clear database."""
    yield
    collections = await CollectionTortoise.all()
    for collection in collections:
        await collection.cards.clear()
        await collection.delete()
    cards = await CardTortoise.all()
    for card in cards:
        await card.delete()
