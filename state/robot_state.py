import time, math, os, base64
from threading import Lock
from geographiclib.geodesic import Geodesic

IMAGE_FOLDER = "./images"
IMAGE_FILES = sorted([f for f in os.listdir(IMAGE_FOLDER)
                      if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
IMAGE_STEP_M = 1.0  # каждый метр меняем изображение

if IMAGE_FILES:
    with open(os.path.join(IMAGE_FOLDER, IMAGE_FILES[0]), "rb") as f:
        IMAGE_SIZE_BYTES = len(f.read())
else:
    IMAGE_SIZE_BYTES = 0


class Robot:
    def __init__(self, latitude=54.123, longitude=30.123, rotation_angle=0.0):
        self.latitude = latitude
        self.longitude = longitude
        self.rotation_angle = rotation_angle 

        self.speed_mps = 0.0
        self.mode = "idle"  
        self.move_remaining_m = 0.0

        self.img_index = 0
        self.image_base64 = self.load_image(self.img_index)

        self.lock = Lock()
        self.last_update = time.time()
        self.distance_accum = 0.0

    def load_image(self, index):
        if not IMAGE_FILES:
            return ""
        index = index % len(IMAGE_FILES)  # зацикливаем
        path = os.path.join(IMAGE_FOLDER, IMAGE_FILES[index])
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def update_position(self):
        """Обновление координат и смена изображения"""
        now = time.time()
        dt = now - self.last_update
        self.last_update = now

        with self.lock:
            if self.speed_mps == 0:
                return

            ds = abs(self.speed_mps) * dt

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

            result = Geodesic.WGS84.Direct(
                self.latitude,
                self.longitude,
                self.rotation_angle,
                ds_signed
            )
            self.latitude = result["lat2"]
            self.longitude = result["lon2"]

            self.distance_accum += abs(ds)
            while self.distance_accum >= IMAGE_STEP_M:
                self.distance_accum -= IMAGE_STEP_M
                self.img_index += 1
                self.image_base64 = self.load_image(self.img_index)

    def stop(self):
        """Останавливает робота"""
        with self.lock:
            self.speed_mps = 0
            self.mode = "idle"
            self.move_remaining_m = 0

    def rotate(self, delta_angle):
        """Поворот на угол в градусах"""
        with self.lock:
            self.rotation_angle = (self.rotation_angle + delta_angle) % 360

    def move(self, distance_m, speed_mps=1.0):
        """Задаем движение на distance_m метров с заданной скоростью"""
        with self.lock:
            self.move_remaining_m = abs(distance_m)
            self.speed_mps = speed_mps if distance_m >= 0 else -speed_mps
            self.mode = "moving" if distance_m != 0 else "idle"

    def get_state(self):
        """Возвращает текущие данные робота"""
        self.update_position()
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "rotation_angle": self.rotation_angle,
            "img_base64": self.image_base64,
        }
