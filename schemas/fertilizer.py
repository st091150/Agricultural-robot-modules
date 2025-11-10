from typing import Optional
from pydantic import BaseModel


class FertilizerRequest(BaseModel):
    field_id: Optional[int] = None  # Id поля (опционально)
    soil_data: dict  # Данные для модели


class FertilizerResult(BaseModel):
    task_id: str  # Id задачи
    result: dict  # Результат (авто конвертация в JSON через FastApi)
