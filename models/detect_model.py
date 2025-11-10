async def predict(data: dict) -> dict:
    # Пример: всегда возвращаем "детектировано"
    return {"objects": ["example_object"], "data": data}
