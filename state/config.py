import os

IMAGE_FOLDER = "./images"
IMAGE_FILES = sorted([f for f in os.listdir(IMAGE_FOLDER)
                      if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
IMAGE_STEP_M = 1.0  # каждый метр меняем изображение

if IMAGE_FILES:
    with open(os.path.join(IMAGE_FOLDER, IMAGE_FILES[0]), "rb") as f:
        IMAGE_SIZE_BYTES = len(f.read())
else:
    IMAGE_SIZE_BYTES = 0

START_LATITUDE = 53.90931
START_LONGITUDE = 27.55805
START_ANGLE = 0
START_SPEED = 1.0