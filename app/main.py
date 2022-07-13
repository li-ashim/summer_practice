from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from app.config import config
from app.routers import authentication, cards, collections

app = FastAPI(
    title='REST API for flashcard service'
)


app.include_router(cards.router)
app.include_router(collections.router)
app.include_router(authentication.router)


TORTOISE_ORM = {
    'connections': {'default': config.sqlite_host},
    'apps': {
        'models': {
            'models': [
                'app.models.models',
                'app.models.authentication',
                'aerich.models'
            ],
            'default_connection': 'default',
        },
    },
}

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)
