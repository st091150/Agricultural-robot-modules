import asyncio
from redis.asyncio import Redis

from workers.validators import QueueName
from workers.worker import worker

from models.detect_model import predict as detect_predict
from models.fertilizer_model import predict as fertilizer_predict


_worker_tasks: list[asyncio.Task] = []


async def start_all_workers(redis: Redis):
    """
    Запускает все воркеры в фоновом режиме.
    """
    loop = asyncio.get_running_loop()

    # Создаём отдельные фоновые задачи
    detect_task = loop.create_task(worker(QueueName.DETECT, detect_predict, redis))
    fertilizer_task = loop.create_task(
        worker(QueueName.FERTILIZER, fertilizer_predict, redis)
    )

    _worker_tasks.extend([detect_task, fertilizer_task])

    print("🚀 Воркеры запущены:", [t.get_name() for t in _worker_tasks])


async def stop_all_workers():
    print("🛑 Остановка воркеров...")
    for task in _worker_tasks:
        task.cancel()
    try:
        await asyncio.wait_for(
            asyncio.gather(*_worker_tasks, return_exceptions=True), timeout=5
        )
    except asyncio.TimeoutError:
        print("⚠️ Воркеры не успели завершиться за 5 секунд")
    print("✅ Все воркеры остановлены.")
    _worker_tasks.clear()
