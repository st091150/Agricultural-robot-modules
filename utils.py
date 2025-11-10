import sys
from config.redis_settings import REDIS_HOST
from redis.asyncio import Redis, from_url
from workers.validators import QueueName


async def clear_queues(redis: Redis):
    for queue in QueueName:
        await redis.delete(queue.value)
    print("🧹 Все очереди очищены")


async def check_redis():
    try:
        redis = await from_url(REDIS_HOST)
        pong = await redis.ping()
        if not pong:
            print("❌ Redis сервер не доступен")
            sys.exit(1)
        print("✅ Redis подключен")
        return redis
    except Exception as e:
        print(f"❌ Redis сервер не доступен: {e}")
        sys.exit(1)
