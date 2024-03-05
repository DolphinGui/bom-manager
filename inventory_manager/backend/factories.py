from .base import AccessKey
from .sheets import GoogleCreds


def cached() -> bool:
    return GoogleCreds.cached()


def get_key() -> AccessKey:
    return GoogleCreds()
