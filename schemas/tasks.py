from typing import Literal
from dataclasses import dataclass


@dataclass
class Task:
    task_id: str  # Номер задачи
    type: Literal["detect", "fertilizer"]  # Стат. проверка на type
    data: dict
