import json
import asyncio
from typing import Any, Callable, Awaitable
from redis.asyncio import Redis

from config.redis_settings import RESULT_TTL
from workers.validators import QueueName, validate_queue_and_predict_fn

from models.detect_model import predict as detect_predict
from models.fertilizer_model import predict as fertilizer_predict


async def worker(
    queue_name: QueueName, predict_fn: Callable[[Any], Awaitable[Any]], redis: Redis
):
    """
    Асинхронный воркер обработки задач с использованием BLPOP.
    Обрабатывает задачи по мере поступления в очередь.
    """
    validate_queue_and_predict_fn(queue_name, predict_fn)

    print(f"🔧 Воркер {queue_name.value} запущен")

    try:
        while True:
            # BLPOP блокирует соединение до появления задачи или таймаута
            item = await redis.blpop(queue_name.value, timeout=5)
            if item is None:
                continue

            _, raw_task = item
            task = json.loads(raw_task)

            try:
                result = await predict_fn(task["data"])
                await redis.set(task["task_id"], json.dumps(result), ex=RESULT_TTL)
            except Exception as e:
                result = {"error": str(e)}
                await redis.set(task["task_id"], json.dumps(result), ex=RESULT_TTL)

    except asyncio.CancelledError:
        print(f"🛑 Воркер {queue_name.value} остановлен.")
        await redis.close()
        raise
    except Exception as e:
        print(f"Ошибка в воркере {queue_name.value}: {e}")
        await asyncio.sleep(1)  # короткая пауза при ошибке, чтобы не спамить
