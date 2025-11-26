from pydantic import BaseModel
from typing import Optional, Dict

class CommandModel(BaseModel):
    cmd: str
    data: Optional[Dict] = None
