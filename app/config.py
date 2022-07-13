import os
from functools import lru_cache

from pydantic import BaseSettings


class Config(BaseSettings):
    sqlite_host: str = os.environ['SQLITE_HOST']


@lru_cache()
def get_config():
    return Config()


config = get_config()
