# first run `redis-server /usr/local/etc/redis.conf`
from typing import Tuple, Any
import aioredis


async def get_redis() -> Any:
    return await aioredis.create_redis('redis://localhost')


async def get_subscriber(name: str) -> Tuple[Any, Any]:
    redis = await get_redis()
    res = await redis.subscribe(name)
    subscriber = res[0]
    return redis, subscriber


async def redis_send(ch: str, text: str) -> None:
    redis = await get_redis()
    await redis.publish(ch, text)
