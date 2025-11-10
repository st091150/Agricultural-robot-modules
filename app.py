import uuid
import json
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from redis.asyncio import Redis, from_url

from config.redis_settings import (
    REDIS_HOST,
    QUEUE_DETECT,
    QUEUE_FERTILIZER,
    CHANNEL_RESULTS,
)
from config.app_settings import REQUEST_TIMEOUT

from schemas.detect import DetectRequest, DetectResult
from schemas.fertilizer import FertilizerRequest, FertilizerResult

from workers.manager import start_all_workers, stop_all_workers
from utils import check_redis, clear_queues


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Старт приложения
    await check_redis()
    app.state.redis = await from_url(REDIS_HOST, decode_responses=True)

    # Очищаем очереди (если будем учитывать ошибки в RT с сервисом, можно убрать, чтоб не терять задачи)
    await clear_queues(app.state.redis)

    await start_all_workers(app.state.redis)

    yield

    # Завершение при остановке
    await stop_all_workers()
    await app.state.redis.close()


app = FastAPI(lifespan=lifespan)


async def wait_for_result(task_id: str, timeout: int, redis: Redis):
    pubsub = redis.pubsub()
    await pubsub.subscribe(CHANNEL_RESULTS)
    try:
        while timeout > 0:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1
            )
            if message and message["data"] == task_id:
                data = await redis.get(task_id)
                return json.loads(data)
            timeout -= 1
        # По истечении времени проверяем хранилище
        data = await redis.get(task_id)
        if data:
            return json.loads(data)
        raise HTTPException(status_code=504, detail="Timeout waiting for result")
    finally:
        await pubsub.unsubscribe(CHANNEL_RESULTS)


@app.post("/detect/", response_model=DetectResult)
async def detect(request: DetectRequest):
    redis = app.state.redis

    task_id = str(uuid.uuid4())

    task = {"task_id": task_id, "type": "detect", "data": request.model_dump()}

    await redis.rpush(QUEUE_DETECT, json.dumps(task))
    result = await wait_for_result(task_id, REQUEST_TIMEOUT, redis)
    return {"task_id": task_id, "result": result}


@app.post("/fertilizer/", response_model=FertilizerResult)
async def fertilizer(request: FertilizerRequest):
    redis = app.state.redis

    task_id = str(uuid.uuid4())

    task = {"task_id": task_id, "type": "fertilizer", "data": request.model_dump()}

    await redis.rpush(QUEUE_FERTILIZER, json.dumps(task))
    result = await wait_for_result(task_id, REQUEST_TIMEOUT, redis)
    return {"task_id": task_id, "result": result}
