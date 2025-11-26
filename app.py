from fastapi import FastAPI
from schemas.schemas import CommandModel
from commands.robot_commands import handle_command
from state.robot_spec import get_spec
from state.robot_state_data import robot

app = FastAPI()

@app.post("/command")
def command_api(command: CommandModel):
    return handle_command(robot, command.cmd, command.data)

@app.get("/collect")
def state_api():
    return robot.get_state()

@app.get("/spec")
def spec_api():
    return get_spec()

@app.post("/stop")
def stop_robot():
    robot.stop()
    return {"status": "stopped"}
