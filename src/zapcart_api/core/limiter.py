from slowapi import Limiter
from slowapi.util import get_remote_address

from zapcart_api.core import settings

storage_uri = settings.redis_url
if "protocol=" not in storage_uri:
    storage_uri = f"{storage_uri}?protocol=2" if "?" not in storage_uri else f"{storage_uri}&protocol=2"

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=storage_uri,
    default_limits=["10/minute"],
)