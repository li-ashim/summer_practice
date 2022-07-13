from fastapi import APIRouter, Depends, Response, status

from app.models.models import (CollectionCreate, CollectionDBLong,
                               CollectionDBShort, CollectionPartialUpdate,
                               CollectionTortoise)
from app.utils.utils import pagination


async def get_collection_or_404(id: int) -> CollectionTortoise:
    """Get object from db or raise DoesNotExist exception."""
    return await CollectionTortoise.get(id=id)


router = APIRouter(
    prefix='/collections',
    tags=['collections']
)


@router.get('/')
async def read_collections(pagination: tuple[int, int] = Depends(pagination)) \
                     -> list[CollectionDBShort]:
    """Get list of collections."""
    skip, limit = pagination
    collections = await CollectionTortoise.all().offset(skip).limit(limit)

    return [CollectionDBShort.from_orm(col) for col in collections]


@router.get('/{id}', response_model=CollectionDBLong)
async def read_collection(collection: CollectionTortoise =
                          Depends(get_collection_or_404)) -> CollectionDBLong:
    """Get card with particular id."""
    await collection.fetch_related('cards')
    for card in collection.cards:
        await card.fetch_related('collections')
    return CollectionDBLong.from_orm(collection)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def save_collection(collection: CollectionCreate) -> CollectionDBShort:
    """Create collection."""
    collection_tortoise = await CollectionTortoise.create(**collection.dict())
    return CollectionDBShort.from_orm(collection_tortoise)


@router.put('/{id}')
async def update_collection(
        collection_update: CollectionPartialUpdate,
        collection: CollectionTortoise = Depends(get_collection_or_404)
        ) -> CollectionDBShort:
    """Update existing collection."""
    collection.update_from_dict(collection_update.dict(exclude_unset=True))
    await collection.save()

    return CollectionDBShort.from_orm(collection)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(collection: CollectionTortoise =
                            Depends(get_collection_or_404)):
    """Delete collection."""
    await collection.fetch_related('cards')
    for card in collection.cards:
        await collection.cards.remove(card)
    await collection.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
