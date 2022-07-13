from fastapi import Query
from tortoise.exceptions import NoValuesFetched
from tortoise.fields.relational import ManyToManyRelation


async def pagination(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=0),
) -> tuple[int, int]:
    """Handle pagination."""
    capped_limit = min(100, limit)
    return (skip, capped_limit)


def get_list_from_queryset(cls, val: ManyToManyRelation) -> list:
    """Return list of objects from queryset."""
    try:
        return list(val)
    except NoValuesFetched:
        return []
