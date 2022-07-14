from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException

from app.dependencies import get_current_user
from app.models.authentication import UserTortoise
from app.models.models import (CollectionCreate, CollectionDBLong,
                               CollectionDBShort, CollectionPartialUpdate,
                               CollectionPublicLong, CollectionPublicShort,
                               CollectionTortoise)
from app.utils.utils import pagination


async def get_collection_or_404(id: int) -> CollectionTortoise:
    """Get object from db or raise DoesNotExist exception."""
    return await CollectionTortoise.get(id=id)


async def check_collection_owner(
        user: UserTortoise = Depends(get_current_user),
        collection: CollectionTortoise = Depends(get_collection_or_404)
):
    if collection.owner_id == user.id:
        return collection
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


router = APIRouter(
    prefix='/collections',
    tags=['collections']
)


@router.get('/public', summary='Get publicly available collections.')
async def read_public_collections(
    pagination: tuple[int, int] = Depends(pagination)
) -> list[CollectionPublicShort]:
    """Get list of public collections."""
    skip, limit = pagination
    collections = await CollectionTortoise.filter(
        is_private=False
    ).offset(skip).limit(limit)

    for col in collections:
        await col.fetch_related('owner')

    return [CollectionPublicShort.from_orm(col) for col in collections]


@router.get('/private', summary='Get collections that you own.')
async def read_private_collections(
    pagination: tuple[int, int] = Depends(pagination),
    user: UserTortoise = Depends(get_current_user)
) -> list[CollectionDBShort]:
    """Get list of collections which belong to you."""
    skip, limit = pagination
    collections = await CollectionTortoise.filter(
        owner_id=user.id
    ).offset(skip).limit(limit)

    return [CollectionDBShort.from_orm(col) for col in collections]


@router.get('/public/{id}', response_model=CollectionDBLong,
            summary='Get particular public collection.')
async def read_public_collection(
    collection: CollectionTortoise =
    Depends(get_collection_or_404)
) -> CollectionPublicLong:
    """Get public collection with all its cards."""
    await collection.fetch_related('cards')
    for card in collection.cards:
        await card.fetch_related('collections')
    await collection.fetch_related('owner')
    return CollectionPublicLong.from_orm(collection)


@router.get('/private/{id}', response_model=CollectionDBLong,
            summary='Get particular collection that you own.')
async def read_private_collection(
    collection: CollectionTortoise =
    Depends(check_collection_owner)
) -> CollectionDBLong:
    """Get private collection with all its cards."""
    await collection.fetch_related('cards')
    for card in collection.cards:
        await card.fetch_related('collections')
    return CollectionDBLong.from_orm(collection)


@router.post('/', status_code=status.HTTP_201_CREATED,
             summary='Create collection.')
async def save_collection(
    collection: CollectionCreate,
    user: UserTortoise = Depends(get_current_user)
) -> CollectionDBShort:
    """Create collection."""
    collection_tortoise = await CollectionTortoise.create(
        owner=user,
        **collection.dict()
    )
    return CollectionDBShort.from_orm(collection_tortoise)


@router.put('/{id}', summary='Update collection.')
async def update_collection(
    collection_update: CollectionPartialUpdate,
    collection: CollectionTortoise = Depends(check_collection_owner)
) -> CollectionDBShort:
    """Update existing collection."""
    collection.update_from_dict(collection_update.dict(exclude_unset=True))
    await collection.save()

    return CollectionDBShort.from_orm(collection)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT,
               summary='Delete collection.')
async def delete_collection(
    collection: CollectionTortoise =
    Depends(check_collection_owner)
):
    """Delete collection."""
    await collection.fetch_related('cards')
    for card in collection.cards:
        await collection.cards.remove(card)
    await collection.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
