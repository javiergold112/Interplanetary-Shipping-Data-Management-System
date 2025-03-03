import redis

from config import RedisConfig

redis_con = redis.from_url(
    url=f"redis://{RedisConfig.REDIS_HOST}:{RedisConfig.REDIS_PORT}",
    decode_responses=True,
)