from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from tortoise.exceptions import DoesNotExist, IntegrityError

from app.models.authentication import (AccessToken, AccessTokenTortoise, User,
                                       UserCreate, UserDB, UserTortoise)
from app.utils.passwords import get_password_hash, verify_password

router = APIRouter(
    tags=['authentication']
)


async def authenticate(email: str, password: str) -> UserDB | None:
    """Return user if authenticated, None otherwise."""
    try:
        user = await UserTortoise.get(email=email)
    except DoesNotExist:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return UserDB.from_orm(user)


async def create_access_token(user: UserDB) -> AccessToken:
    """Create access token for authenticated user."""
    access_token = AccessToken(user_id=user.id)
    access_token_tortoise = await AccessTokenTortoise.create(
        **access_token.dict()
    )
    return AccessToken.from_orm(access_token_tortoise)


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate) -> User:
    """Register user with email and password."""
    hashed_password = get_password_hash(user.password)

    try:
        user_tortoise = await UserTortoise.create(
            **user.dict(),
            hashed_password=hashed_password
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with given email already exists"
        )
    else:
        return User.from_orm(user_tortoise)


@router.post('/token')
async def create_token(form_data: OAuth2PasswordRequestForm =
                       Depends(OAuth2PasswordRequestForm)):
    """Create token if user authenticated, 401 otherwise."""
    email = form_data.username
    password = form_data.password
    user = await authenticate(email, password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    token = await create_access_token(user)

    return {'access_token': token.access_token,
            'token_type': 'bearer'}
