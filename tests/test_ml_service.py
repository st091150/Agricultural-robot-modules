import asyncio
import base64
import io
import pytest
import httpx
from PIL import Image


def tiny_png_base64():
    img = Image.new("RGB", (2, 2), (255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


@pytest.fixture(scope="session")
def base_url():
    return "http://127.0.0.1:8000"


@pytest.mark.asyncio
async def test_detect_ok(base_url):
    payload = {"image": tiny_png_base64(), "metadata": {"request_id": "detect-001"}}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        r = await client.post(f"{base_url}/detect/", json=payload)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_fertilizer_ok(base_url):
    payload = {"field_id": 1, "soil_data": {"request_id": "fert-001"}}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        r = await client.post(f"{base_url}/fertilizer/", json=payload)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_missing_image_field(base_url):
    payload = {"metadata": {"note": "missing image"}}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        r = await client.post(f"{base_url}/detect/", json=payload)
    assert r.status_code in (400, 415, 422)


@pytest.mark.asyncio
async def test_bad_base64(base_url):
    payload = {"image": "data:image/png;base64,THIS_IS_NOT_BASE64", "metadata": {}}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        r = await client.post(f"{base_url}/detect/", json=payload)
    assert r.status_code in (400, 415, 422, 500)


@pytest.mark.asyncio
async def test_parallel_mixed_endpoints(base_url):
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        async def call(i):
            ep = "/detect/" if i % 2 == 0 else "/fertilizer/"
            if ep == "/detect/":
                payload = {"image": tiny_png_base64(), "metadata": {"i": i, "ep": ep}}
            else:
                payload = {"field_id": i, "soil_data": {"i": i, "ep": ep}}
            r = await client.post(f"{base_url}{ep}", json=payload)
            return i, r.status_code

        N = 20
        results = await asyncio.gather(*[call(i) for i in range(N)])
        ok = [code for _, code in results if code == 200]
    assert len(ok) >= int(N * 0.9)


@pytest.mark.asyncio
@pytest.mark.load
async def test_detect_burst_100(base_url):
    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        async def call(i):
            payload = {"image": tiny_png_base64(), "metadata": {"i": i}}
            r = await client.post(f"{base_url}/detect/", json=payload)
            return r.status_code

        codes = await asyncio.gather(*[call(i) for i in range(100)])
    assert sum(1 for c in codes if c == 200) >= 90
