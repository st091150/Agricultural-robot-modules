from enum import Enum
from typing import Callable, Any, Awaitable

from config.redis_settings import QUEUE_DETECT, QUEUE_FERTILIZER

from models.detect_model import predict as detect_predict
from models.fertilizer_model import predict as fertilizer_predict


class QueueName(str, Enum):
    DETECT = QUEUE_DETECT
    FERTILIZER = QUEUE_FERTILIZER


# Разрешённые связки "очередь → функция"
QUEUE_MODEL_MAP: dict[QueueName, Callable[[Any], Awaitable[Any]]] = {
    QueueName.DETECT: detect_predict,
    QueueName.FERTILIZER: fertilizer_predict,
}


def validate_queue_and_predict_fn(
    queue_name: QueueName, predict_fn: Callable[[Any], Awaitable[Any]]
) -> None:
    """
    Проверяет, что очередь и функция соответствуют разрешённой паре.
    Поднимает ValueError при несоответствии.
    """
    expected_fn = QUEUE_MODEL_MAP.get(queue_name)
    if expected_fn is None:
        raise ValueError(f"Неизвестное имя очереди: {queue_name}")
    if predict_fn is not expected_fn:
        raise ValueError(
            f"Для очереди '{queue_name.value}' нужно использовать функцию "
            f"'{expected_fn.__name__}', а не '{predict_fn.__name__}'"
        )
