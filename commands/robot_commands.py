from fastapi import HTTPException

def handle_command(robot, cmd: str, data: dict | None = None):
    """
    Обрабатывает команду для робота.
    cmd: строка команды ("rotate", "move", "speed", "stop")
    data: словарь с параметрами команды
    """
    data = data or {}
    cmd = cmd.lower()

    if cmd == "rotate":
        if "delta_angle" not in data:
            raise HTTPException(400, "rotate requires delta_angle")
        robot.rotate(data["delta_angle"])
        return {"status": "ok"}

    if cmd == "move":
        if "distance_m" not in data:
            raise HTTPException(400, "move requires distance_m")
        robot.move(data["distance_m"])
        return {"status": "ok"}

    if cmd == "speed":
        if "speed_mps" not in data:
            raise HTTPException(400, "speed requires speed_mps")
        robot.set_speed(data["speed_mps"])
        return {"status": "ok"}

    if cmd == "stop":
        robot.stop()
        return {"status": "ok"}

    raise HTTPException(400, f"Unknown command {cmd}")

