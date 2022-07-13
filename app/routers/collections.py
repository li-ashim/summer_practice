from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException

from app.dependencies import get_current_user
from app.models.authentication import UserTortoise
from app.models.models import (CollectionCreate, CollectionDBLong,
                               CollectionDBShort, CollectionPartialUpdate,
                               CollectionTortoise)
from app.utils.utils import pagination


async def get_collection_or_404(id: int) -> CollectionTortoise:
    """Get object from db or raise DoesNotExist exception."""
    return await CollectionTortoise.get(id=id)


async def check_collection_owner(
        user: UserTortoise = Depends(get_current_user),
        collection: CollectionTortoise = Depends(get_collection_or_404)):
    if collection.owner_id == user.id:
        return collection
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


router = APIRouter(
    prefix='/collections',
    tags=['collections']
)


@router.get('/')
async def read_collections(pagination: tuple[int, int] = Depends(pagination),
                           user: UserTortoise = Depends(get_current_user)) \
                     -> list[CollectionDBShort]:
    """Get list of collections."""
    skip, limit = pagination
    collections = await CollectionTortoise.filter(
        owner_id=user.id
    ).offset(skip).limit(limit)

    return [CollectionDBShort.from_orm(col) for col in collections]


@router.get('/{id}', response_model=CollectionDBLong)
async def read_collection(
    collection: CollectionTortoise =
    Depends(check_collection_owner)
) -> CollectionDBLong:
    """Get card with particular id."""
    await collection.fetch_related('cards')
    for card in collection.cards:
        await card.fetch_related('collections')
    return CollectionDBLong.from_orm(collection)


@router.post('/', status_code=status.HTTP_201_CREATED)
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


@router.put('/{id}')
async def update_collection(
    collection_update: CollectionPartialUpdate,
    collection: CollectionTortoise = Depends(check_collection_owner)
) -> CollectionDBShort:
    """Update existing collection."""
    collection.update_from_dict(collection_update.dict(exclude_unset=True))
    await collection.save()

    return CollectionDBShort.from_orm(collection)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
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
