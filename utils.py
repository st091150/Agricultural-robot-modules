from PIL import Image
import os
import base64

import os
from PIL import Image

def resize_images_in_folder(input_folder: str, output_folder: str, target_size: tuple[int, int] = (256, 256)):
    """
    Приводит все изображения в папке к единому размеру и сохраняет их в output_folder с последовательными именами,
    сохраняя исходное расширение.
    """
    os.makedirs(output_folder, exist_ok=True)

    processed_count = 0
    for idx, filename in enumerate(os.listdir(input_folder), 1):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue

        img_path = os.path.join(input_folder, filename)
        img = Image.open(img_path)

        img_resized = img.resize(target_size, Image.LANCZOS)

        ext = os.path.splitext(filename)[1]  # .png, .jpg, ...
        output_path = os.path.join(output_folder, f"{idx}{ext}")
        img_resized.save(output_path)
        processed_count += 1

    print(f"Обработано {processed_count} изображений. Все сохранены в {output_folder}")

def restore_image_from_base64_file(base64_file_path: str, output_file_path: str):
    """
    Читает Base64-строку из файла и восстанавливает исходное изображение.
    """
    with open(base64_file_path, "r") as f:
        img_base64_str = f.read().strip()

    img_bytes = base64.b64decode(img_base64_str)

    with open(output_file_path, "wb") as f:
        f.write(img_bytes)


