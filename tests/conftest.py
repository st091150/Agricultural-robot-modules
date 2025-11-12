import base64, io
from PIL import Image
import pytest

BASE_URL = "http://127.0.0.1:8000"

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

def tiny_png_base64(color=(120, 180, 120)):
    """生成一张 64x64 的小PNG并转为 data:URI Base64 字符串。"""
    img = Image.new("RGB", (64, 64), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"
