from datetime import datetime, timedelta

from pydantic import BaseModel, EmailStr, Field
from tortoise import fields, timezone
from tortoise.models import Model

from app.utils.passwords import generate_token


def get_expiration(duration_seconds: int = 86400) -> datetime:
    """Get expiration in 24 hours."""
    return timezone.now() + timedelta(seconds=duration_seconds)


class UserBase(BaseModel):
    email: EmailStr
    name: str

    class Config:
        orm_mode = True


class UserPublic(BaseModel):
    name: str

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int


class UserDB(User):
    hashed_password: str


class UserTortoise(Model):
    id = fields.IntField(pk=True, generated=True)
    email = fields.CharField(index=True, unique=True,
                             null=False, max_length=255)
    cards: fields.ReverseRelation
    collections: fields.ReverseRelation
    name = fields.CharField(max_length=80, null=False)
    hashed_password = fields.CharField(null=False, max_length=255)

    class Meta:
        table = 'users'


class AccessToken(BaseModel):
    user_id: int
    access_token: str = Field(default_factory=generate_token)
    expiration: datetime = Field(default_factory=get_expiration)

    class Config:
        orm_mode = True


class AccessTokenTortoise(Model):
    access_token = fields.CharField(pk=True,
                                    max_length=255)
    user = fields.ForeignKeyField('models.UserTortoise',
                                  null=False)
    expiration = fields.DatetimeField(null=False)

    class Meta:
        table = 'access_tokens'
