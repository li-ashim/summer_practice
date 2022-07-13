import httpx
import pytest
from fastapi import status

from tests.conftest import test_card, test_collection_1, test_collection_2

card = {}


@pytest.mark.asyncio
async def test_save_card_without_collections(test_client: httpx.AsyncClient):
    response = await test_client.post('/cards/', json=test_card)
    assert response.status_code == status.HTTP_201_CREATED
    card.update(response.json())


@pytest.mark.asyncio
async def test_get_cards(test_client: httpx.AsyncClient):
    response = await test_client.get('/cards/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_card_by_id(test_client: httpx.AsyncClient):
    response = await test_client.get(f'/cards/{card["id"]}')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_save_card_with_collections(test_client: httpx.AsyncClient):
    collections_to_add = []
    response = await test_client.post('/collections/', json=test_collection_1)
    collections_to_add.append(response.json())
    response = await test_client.post('/collections/', json=test_collection_2)
    collections_to_add.append(response.json())

    test_card['collections'] = collections_to_add  # type: ignore
    response = await test_client.post('/cards/', json=test_card)
    assert response.status_code == status.HTTP_201_CREATED
    assert len(response.json()['collections']) == 2
    card.update(response.json())


@pytest.mark.asyncio
async def test_update_collection(test_client: httpx.AsyncClient):
    test_card['collections'].pop()  # type: ignore
    response = await test_client.put(
        f'/cards/{card["id"]}',
        json=test_card
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['collections']) == 1
    card.update(response.json())


@pytest.mark.asyncio
async def test_delete_card_with_collections(test_client: httpx.AsyncClient):
    response = await test_client.delete(f'/cards/{card["id"]}')
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_card_without_collections(test_client: httpx.AsyncClient):
    test_card['collections'] = []
    response = await test_client.post(
        '/cards/',
        json=test_card
    )
    card.update(response.json())
    await test_client.post('/cards/', json=test_card)

    response = await test_client.delete(f'/cards/{card["id"]}')
    assert response.status_code == status.HTTP_204_NO_CONTENT
