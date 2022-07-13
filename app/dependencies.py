from typing import cast

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from tortoise import timezone
from tortoise.exceptions import DoesNotExist

from app.models.authentication import AccessTokenTortoise, UserTortoise


async def get_current_user(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl='/token'))
) -> UserTortoise:
    """Return user if authenticated, 401 otherwise."""
    try:
        access_token: AccessTokenTortoise = await AccessTokenTortoise.get(
            access_token=token, expiration__gte=timezone.now()
        ).prefetch_related('user')
        return cast(UserTortoise, access_token.user)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
