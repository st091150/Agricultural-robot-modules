import os
import re
import uuid
import json
import base64
import binascii
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
from schemas.fertilizer import FertilizerResult

from workers.manager import start_all_workers, stop_all_workers
from utils import check_redis, clear_queues, _validate_base64_image

_DATAURL_RE = re.compile(r"^data:image/[^;]+;base64,", re.IGNORECASE)


def _validate_base64_image(s: str) -> None:
    b64 = _DATAURL_RE.sub("", (s or "").strip())
    try:
        base64.b64decode(b64, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(status_code=422, detail="Invalid base64 image")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_redis()
    app.state.redis = await from_url(REDIS_HOST, decode_responses=True)
    await clear_queues(app.state.redis)
    await start_all_workers(app.state.redis)
    try:
        yield
    finally:
        await stop_all_workers()
        await app.state.redis.close()


app = FastAPI(lifespan=lifespan)

RESPONSE_TIMEOUT_SEC = float(os.getenv("RESPONSE_TIMEOUT_SEC", REQUEST_TIMEOUT))


async def wait_for_result(task_id: str, timeout: float, redis: Redis):
    pubsub = redis.pubsub()
    await pubsub.subscribe(CHANNEL_RESULTS)
    try:
        remaining = float(timeout)
        while remaining > 0:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            if message and message.get("data") == task_id:
                data = await redis.get(task_id)
                return json.loads(data) if data else None
            remaining -= 1.0
        data = await redis.get(task_id)
        if data:
            return json.loads(data)
        raise HTTPException(status_code=504, detail="Timeout waiting for result")
    finally:
        await pubsub.unsubscribe(CHANNEL_RESULTS)


@app.post("/detect/", response_model=DetectResult)
async def detect(request: DetectRequest):
    _validate_base64_image(request.image)
    redis = app.state.redis
    task_id = str(uuid.uuid4())
    task = {"task_id": task_id, "type": "detect", "data": request.model_dump()}
    await redis.rpush(QUEUE_DETECT, json.dumps(task))
    result = await wait_for_result(task_id, RESPONSE_TIMEOUT_SEC, redis)
    return {"task_id": task_id, "result": result}


@app.post("/fertilizer/", response_model=FertilizerResult)
async def fertilizer(request: DetectRequest):
    _validate_base64_image(request.image)
    redis = app.state.redis
    task_id = str(uuid.uuid4())
    task = {"task_id": task_id, "type": "fertilizer", "data": request.model_dump()}
    await redis.rpush(QUEUE_FERTILIZER, json.dumps(task))
    result = await wait_for_result(task_id, RESPONSE_TIMEOUT_SEC, redis)
    return {"task_id": task_id, "result": result}
