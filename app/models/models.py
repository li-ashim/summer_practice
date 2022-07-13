from datetime import datetime

from pydantic import BaseModel, Field, validator
from tortoise import fields
from tortoise.models import Model

from app.utils.utils import get_list_from_queryset


class CollectionBase(BaseModel):
    """Base model for collection."""
    title: str
    description: str
    is_private: bool = Field(default=True)

    class Config:
        orm_mode = True


class CollectionCreate(CollectionBase):
    """Model for creation of collection."""
    pass


class CollectionDBShort(CollectionBase):
    """Model for short representation of entity in DB."""
    id: int


# The order of class declaration is mixed
# because of circular dependency of models

class CardBase(BaseModel):
    """Base card model."""
    title: str
    content: str
    collections: list[CollectionDBShort] | None

    _list_collections = validator(
        'collections',
        pre=True,
        allow_reuse=True
    )(get_list_from_queryset)

    class Config:
        orm_mode = True


class CardCreate(CardBase):
    """Model for card creation."""
    pass


class CardDB(CardBase):
    """Model for representation card entity in DB."""
    id: int
    creation: datetime
    last_update: datetime


class CardPartialUpdate(BaseModel):
    """Model for partial update."""
    title: str | None
    content: str | None
    collections: list[CollectionDBShort] | None

    _list_collections = validator(
        'collections',
        pre=True,
        allow_reuse=True
    )(get_list_from_queryset)

    class Config:
        orm_mode = True


class CardTortoise(Model):
    """ORM card model."""
    id = fields.IntField(pk=True, generated=True)
    title = fields.CharField(max_length=255, null=False)
    content = fields.TextField(null=False)
    collections: fields.ReverseRelation['CollectionTortoise']
    creation = fields.DatetimeField(null=False, auto_now_add=True)
    last_update = fields.DatetimeField(null=False, auto_now=True)

    class Meta:
        table = 'cards'


class CollectionDBLong(CollectionBase):
    """Model for verbose representation of DB entity."""
    id: int
    last_update: datetime = Field(default_factory=datetime.now)
    cards: list[CardDB]

    _list_cards = validator(
        'cards',
        pre=True,
        allow_reuse=True
    )(get_list_from_queryset)


class CollectionPartialUpdate(BaseModel):
    """Model for partial update of collection."""
    title: str | None = None
    description: str | None = None
    is_private: bool = True


class CollectionTortoise(Model):
    """ORM collection model."""
    id = fields.IntField(pk=True, generated=True)
    title = fields.CharField(max_length=255, null=False)
    description = fields.TextField(null=False)
    cards = fields.ManyToManyField(
        'models.CardTortoise',
        related_name='collections',
        on_delete=fields.SET_NULL
    )
    is_private = fields.BooleanField(default=True)
    last_update = fields.DatetimeField(null=False, auto_now=True)

    class Meta:
        table = 'collections'
