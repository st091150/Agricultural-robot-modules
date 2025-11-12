import sys
from config.redis_settings import REDIS_HOST
from redis.asyncio import Redis, from_url
from workers.validators import QueueName
import re
import base64
from fastapi import HTTPException

_DATAURL_RE = re.compile(r"^data:image/[^;]+;base64,", re.IGNORECASE)

def _validate_base64_image(s: str) -> None:
    b64 = _DATAURL_RE.sub("", (s or "").strip())
    try:
        base64.b64decode(b64, validate=True)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image")


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
