from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_get_specification():
    """Проверяем эндпоинт /robot/specification"""
    response = client.get("/robot/specification")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data   
    assert isinstance(data["data"], list)


def test_get_collect():
    """Проверяем эндпоинт /robot/collect"""
    response = client.get("/robot/collect")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_robot_command_empty():
    """Если команд нет, робот должен вернуть 'none'"""
    payload = {"command": "move"}  
    response = client.post("/robot/command", json=payload)
    assert response.status_code == 200
    assert response.json()["command"] == "none"
