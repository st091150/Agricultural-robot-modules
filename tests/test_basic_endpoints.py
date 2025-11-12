import pytest, httpx, asyncio

BASE = "http://127.0.0.1:8000"

@pytest.mark.asyncio
async def test_detect_ok():
    async with httpx.AsyncClient(timeout=30) as client:
        payload = {"image": "test.jpg", "metadata": {"idx": 1}}
        r = await client.post(f"{BASE}/detect/", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert data["result"]["data"]["metadata"]["idx"] == 1

@pytest.mark.asyncio
async def test_fertilizer_ok():
    async with httpx.AsyncClient(timeout=30) as client:
        payload = {"field_id": 42, "soil_data": {"N": 10, "P": 5, "K": 8}}
        r = await client.post(f"{BASE}/fertilizer/", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert data["result"]["data"]["soil_data"]["N"] == 10
