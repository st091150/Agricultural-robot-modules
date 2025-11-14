import base64
import io

import pytest
import httpx
from PIL import Image

BASE = "http://127.0.0.1:8000"


def tiny_png_base64(color=(120, 180, 120)):
    """
    生成一张 64x64 的小 PNG 并转为 data:URI Base64 字符串。
    这样可以通过 _validate_base64_image 的验证。
    """
    img = Image.new("RGB", (64, 64), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


@pytest.mark.asyncio
async def test_detect_ok():
    async with httpx.AsyncClient(timeout=30) as client:
        payload = {"image": tiny_png_base64(), "metadata": {"idx": 1}}
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
