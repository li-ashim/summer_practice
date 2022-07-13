import httpx
import pytest
from fastapi import status

from tests.conftest import test_card, test_collection_1

collection = {}


@pytest.mark.asyncio
async def test_save_collection(test_client: httpx.AsyncClient):
    response = await test_client.post('/collections/', json=test_collection_1)
    assert response.status_code == status.HTTP_201_CREATED
    collection.update(response.json())


@pytest.mark.asyncio
async def test_get_collections(test_client: httpx.AsyncClient):
    response = await test_client.get('/collections/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_collection_by_id(test_client: httpx.AsyncClient):
    response = await test_client.get(f'/collections/{collection["id"]}')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_collection(test_client: httpx.AsyncClient):
    new_description_data = {'description': 'new test description 1'}
    new_title_data = {'title': 'new test collection 1'}
    response = await test_client.put(
        f'/collections/{collection["id"]}',
        json=new_description_data
    )
    assert response.status_code == status.HTTP_200_OK

    response = await test_client.put(
        f'/collections/{collection["id"]}',
        json=new_title_data
    )
    assert response.status_code == status.HTTP_200_OK

    collection.update(response.json())


@pytest.mark.asyncio
async def test_delete_empty_collection(test_client: httpx.AsyncClient):
    response = await test_client.delete(f'/collections/{collection["id"]}')
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_nonempty_collection(test_client: httpx.AsyncClient):
    response = await test_client.post(
        '/collections/',
        json=test_collection_1
    )
    collection.update(response.json())
    collection_for_card = {
        'id': collection['id'],
        'title': collection['title']
    }
    test_card[  # type: ignore
        'collections'
    ].append(collection_for_card)
    await test_client.post('/cards/', json=test_card)

    response = await test_client.delete(f'/collections/{collection["id"]}')
    assert response.status_code == status.HTTP_204_NO_CONTENT
