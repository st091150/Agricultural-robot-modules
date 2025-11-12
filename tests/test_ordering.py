import asyncio
import pytest
import httpx
import base64


def tiny_png_base64() -> str:
    png_bytes = (
        b'\x89PNG\r\n\x1a\n'
        b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
        b'\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01'
        b'\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return base64.b64encode(png_bytes).decode('utf-8')


@pytest.mark.asyncio
async def test_order_of_100_requests(base_url="http://127.0.0.1:8081"):
    async with httpx.AsyncClient(timeout=60) as client:
        async def call(i):
            payload = {"image": tiny_png_base64(), "metadata": {"i": i}}
            r = await client.post(f"{base_url}/detect/", json=payload)
            return i, r.status_code

        N = 100
        results = await asyncio.gather(*[call(i) for i in range(N)])
        ok = [i for i, code in results if code == 200]
        assert len(ok) == N

        order_ok = all(ok[i] < ok[i + 1] for i in range(len(ok) - 1))
        assert order_ok
