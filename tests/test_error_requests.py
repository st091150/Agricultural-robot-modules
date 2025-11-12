import pytest, httpx

BASE = "http://127.0.0.1:8000"

@pytest.mark.asyncio
async def test_detect_422_missing_image():
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f"{BASE}/detect/", json={})
        assert r.status_code == 422  
@pytest.mark.asyncio
async def test_fertilizer_422_missing_soil_data():
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f"{BASE}/fertilizer/", json={"field_id": 1})
        assert r.status_code == 422
