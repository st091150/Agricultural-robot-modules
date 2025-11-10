from typing import Optional
from pydantic import BaseModel


class DetectRequest(BaseModel):
    image: str  # ссылка на изображение или путь к файлу
    metadata: Optional[dict] = None  # Доп. данные


class DetectResult(BaseModel):
    task_id: str  # Id задачи
    result: dict  # Результат (авто конвертация в JSON через FastApi)
