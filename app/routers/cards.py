from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException

from app.dependencies import get_current_user
from app.models.authentication import UserTortoise
from app.models.models import (CardCreate, CardDB, CardPartialUpdate,
                               CardTortoise, CollectionTortoise)
from app.utils.utils import pagination


async def get_card_or_404(id: int) -> CardTortoise:
    """Get object from db or raise DoesNotExist exception."""
    return await CardTortoise.get(id=id)


async def check_card_owner(user: UserTortoise = Depends(get_current_user),
                           card: CardTortoise = Depends(get_card_or_404)):
    if card.owner_id == user.id:
        return card
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


router = APIRouter(
    prefix='/cards',
    tags=['cards']
)


@router.get('/', summary='Get all your cards.')
async def read_cards(pagination: tuple[int, int] = Depends(pagination),
                     user: UserTortoise = Depends(get_current_user)) \
                     -> list[CardDB]:
    """Get all cards of user."""
    skip, limit = pagination
    cards = await CardTortoise.filter(
        owner_id=user.id
    ).offset(skip).limit(limit)

    for card in cards:
        await card.fetch_related('collections')
    return [CardDB.from_orm(card) for card in cards]


@router.get('/{id}', summary='Get particular card.')
async def read_card(card: CardTortoise = Depends(check_card_owner)) -> CardDB:
    """Get card with particular id."""
    await card.fetch_related('collections')
    return CardDB.from_orm(card)


@router.post('/', status_code=status.HTTP_201_CREATED,
             summary='Create card.')
async def save_card(card: CardCreate,
                    user: UserTortoise = Depends(get_current_user)) -> CardDB:
    """Create card."""
    card_tortoise = await CardTortoise.create(
        owner=user,
        **card.dict(exclude={'collections', })
    )

    if card.collections:
        collections: filter[CollectionTortoise] = filter(
            None,
            [await CollectionTortoise.get_or_none(id=col.id, owner_id=user.id)
             for col in card.collections]
        )

        await card_tortoise.collections.add(*collections)

    await card_tortoise.fetch_related('collections')
    return CardDB.from_orm(card_tortoise)


@router.put('/{id}', summary='Update card.')
async def update_card(
        card_update: CardPartialUpdate,
        card: CardTortoise = Depends(check_card_owner)) -> CardDB:
    """Update existing card."""
    card.update_from_dict(card_update.dict(exclude={'collections', },
                                           exclude_unset=True))
    await card.save()

    if card_update.collections:
        await card.fetch_related('collections')
        card_old_collections = set(card.collections)
        card_new_collections = set(filter(  # type: ignore
            None,
            [
                await CollectionTortoise.get_or_none(id=col.id)
                for col in card_update.collections
            ]
        ))
        collections_to_add = card_new_collections - card_old_collections
        collections_to_remove = card_old_collections - card_new_collections
        if collections_to_add:
            await card.collections.add(*collections_to_add)
        if collections_to_remove:
            await card.collections.remove(*collections_to_remove)

    await card.fetch_related('collections')
    return CardDB.from_orm(card)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT,
               summary='Delete card.')
async def delete_card(card: CardTortoise = Depends(check_card_owner)):
    """Delete card."""
    await card.fetch_related('collections')
    for collection in card.collections:
        await card.collections.remove(collection)
    await card.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
