import robot_router


def test_get_spec_returns_specification():
    """Функция get_spec() должна возвращать данные ROBOT_SPEC"""
    spec = robot_router.get_spec()
    assert spec is not None
    assert hasattr(spec, "data")  


def test_collect_returns_data():
    """Проверяем что функция get_collect_data возвращает словарь"""
    data = robot_router.get_collect_data()
    assert isinstance(data, dict)
    assert "data" in data


def test_post_command_behavior():
    """
    Проверяем поведение post_command:
    1) пока current_command = None → возвращает 'none'
    2) когда задаём команду вручную → возвращает её и очищает
    """
    robot_router.current_command = None
    from schemas.command import CommandRequest

    req = CommandRequest(command="go")
    response = robot_router.post_command(req)
    assert response.command == "none"

    robot_router.current_command = "go"
    response = robot_router.post_command(req)
    assert response.command == "go"
    assert robot_router.current_command is None  
