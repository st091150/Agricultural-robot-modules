from fastapi import HTTPException

def handle_command(robot, cmd, data=None):
    robot.update_position()
    data = data or {}
    cmd = cmd.lower()

    if cmd == "rotate":
        if "delta_angle" not in data:
            raise HTTPException(400, "rotate requires delta_angle")
        robot.rotation_angle = (robot.rotation_angle + data["delta_angle"]) % 360
        return {"status": "ok"}

    if cmd == "move":
        if "distance_m" not in data:
            raise HTTPException(400, "move requires distance_m")
        dist = float(data["distance_m"])
        robot.speed_mps = 1.0 if dist > 0 else -1.0
        robot.move_remaining_m = abs(dist)
        robot.mode = "moving"
        return {"status": "ok"}

    if cmd == "speed":
        if "speed_mps" not in data:
            raise HTTPException(400, "speed requires speed_mps")
        robot.speed_mps = float(data["speed_mps"])
        robot.mode = "speed" if robot.speed_mps != 0 else "idle"
        return {"status": "ok"}

    if cmd == "stop":
        robot.speed_mps = 0
        robot.mode = "idle"
        robot.move_remaining_m = 0
        return {"status": "ok"}

    raise HTTPException(400, f"Unknown command {cmd}")
