from pydantic import BaseModel


class CommandRequest(BaseModel):
    command: str


class CommandResponse(BaseModel):
    status: str
