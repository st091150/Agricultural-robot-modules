from fastapi import APIRouter
from schemas.collect import CollectResponse
from schemas.command import CommandRequest, CommandResponse
from schemas.specification import RobotSpecification
from config.robot_spec import ROBOT_SPEC, ROBOT_DATA
from dataclasses import asdict

router = APIRouter(prefix="/robot")


# Получение спецификации робота
@router.get("/specification", response_model=RobotSpecification)
def get_spec():
    return ROBOT_SPEC


# Получение данных от робота
@router.get("/collect")
def get_collect_data():
    response = CollectResponse(data=ROBOT_DATA)
    return asdict(response)


current_command = None


# Отправка команды роботу
@router.post("/command", response_model=CommandResponse)
def post_command(request: CommandRequest):
    global current_command

    # Если команды нет, возвращаем "none"
    if current_command is None:
        return CommandResponse(command="none")

    cmd = current_command
    current_command = None
    return CommandResponse(command=cmd)
