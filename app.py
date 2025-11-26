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
    robot.update_position()
    with robot.lock:
        return {
            "latitude": robot.latitude,
            "longitude": robot.longitude,
            "rotation_angle": robot.rotation_angle,
            "img_base64": robot.image_base64,
        }

@app.get("/spec")
def spec_api():
    return get_spec()

@app.post("/stop")
def stop_robot():
    with robot.lock:
        robot.speed_mps = 0
        robot.mode = "idle"
        robot.move_remaining_m = 0
    return {"status": "stopped"}