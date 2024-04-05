import asyncio

from redis.asyncio import Redis

from src.conf.config import settings


async def get_redis() -> Redis:
    """
    Method initiates redis instance.

    :return: Redis instance.
    :rtype: redis.asyncio.Redis.
    """
    return await Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
    )
