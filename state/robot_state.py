import time, math, os, base64
from threading import Lock
from geographiclib.geodesic import Geodesic

def move_point_wgs84(lat, lon, ds, ang):
    g = Geodesic.WGS84.Direct(lat, lon, math.degrees(ang), ds)
    return g["lat2"], g["lon2"]

with open("images/1.png", "rb") as f:
    IMAGE_SIZE_BYTES = len(f.read())

IMAGE_FOLDER = "./images"
IMAGE_FILES = sorted(os.listdir(IMAGE_FOLDER))

class Robot:
    def __init__(self):
        self.latitude = 54.123
        self.longitude = 30.123
        self.rotation_angle = 0.0
        self.speed_mps = 0.0
        self.mode = "idle"
        self.move_remaining_m = 0.0
        self.last_update = time.time()
        self.img_index = 0
        self.image_base64 = self.load_image(self.img_index)
        self.lock = Lock()

    def load_image(self, index):
        if not IMAGE_FILES:
            return ""
        index = index % len(IMAGE_FILES)
        path = os.path.join(IMAGE_FOLDER, IMAGE_FILES[index])
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def update_position(self):
        now = time.time()
        dt = now - self.last_update
        self.last_update = now

        with self.lock:
            if self.speed_mps == 0:
                return

            ds = abs(self.speed_mps) * dt 

            # Логика "движение к цели"
            if self.mode == "moving":
                if ds >= self.move_remaining_m:
                    ds = self.move_remaining_m
                    self.mode = "idle"
                    self.speed_mps = 0
                    self.move_remaining_m = 0
                else:
                    self.move_remaining_m -= ds

            sign = 1 if self.speed_mps >= 0 else -1
            ds_signed = ds * sign

            # Угол движения (в градусах)
            ang_deg = self.rotation_angle

            # --- Точное вычисление новой GPS-точки ---
            result = Geodesic.WGS84.Direct(
                self.latitude,
                self.longitude,
                ang_deg,
                ds_signed
            )

            self.latitude = result["lat2"]
            self.longitude = result["lon2"]

            # --- Обновление картинки каждые 1 метр ---
            if not hasattr(self, "distance_accum"):
                self.distance_accum = 0.0

            self.distance_accum += abs(ds)   

            while self.distance_accum >= 1.0:   # шаг = 1м
                self.distance_accum -= 1.0
                self.img_index += 1
                self.image_base64 = self.load_image(self.img_index)

