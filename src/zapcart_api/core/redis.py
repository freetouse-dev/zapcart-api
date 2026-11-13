from datetime import datetime, timezone
import redis

from zapcart_api.core import settings

redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True,
    max_connections=20,
    protocol=2,
)

def blacklist_token(token: str, exp: int) -> None:
    now_ts = int(datetime.now(timezone.utc).timestamp())
    ttl = exp - now_ts
    if ttl > 0:
        redis_client.set(f"blacklist:{token}", "revoked", ex=ttl)

def is_token_blacklisted(token: str) -> bool:
    try:
        return bool(redis_client.exists(f"blacklist:{token}"))
    except Exception:
        return False