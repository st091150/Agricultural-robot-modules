# infer.py
import argparse
import torch
from PIL import Image
import numpy as np
from pathlib import Path
from config import *
from models.deeplab_mnv3 import build_model
from utils.augmentations import get_valid_augs

# Цвета для визуализации
COLOR_MAP = np.array([
    [0, 100, 0],    # 0 background — тёмно-зелёный
    [0, 255, 0],    # 1 crop       — ярко-зелёный
    [255, 0, 0],    # 2 weed       — красный
], dtype=np.uint8)

def make_color_mask(pred_np):
    return Image.fromarray(COLOR_MAP[pred_np])

def make_overlay(orig_img, pred_np, alpha=0.45):
    color = Image.fromarray(COLOR_MAP[pred_np])
    color = color.resize(orig_img.size, Image.NEAREST)
    return Image.blend(orig_img, color, alpha)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", type=str, required=True)
    parser.add_argument("--save-dir", type=str, default="predictions")
    parser.add_argument("--overlay-alpha", type=float, default=0.45)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(NUM_CLASSES).to(device)
    model.load_state_dict(torch.load(args.weights, map_location=device))
    model.eval()

    save_dir = Path(args.save_dir)
    save_dir.mkdir(exist_ok=True)

    augs = get_valid_augs(INPUT_SIZE)

    with open(TEST_LIST) as f:
        names = [x.strip() for x in f if x.strip()]

    print(f"Инференс {len(names)} изображений...")

    for name in names:
        img_path = Path(IMAGES_DIR) / f"{name}.png"
        if not img_path.exists():
            print(f"Нет изображения: {img_path}")
            continue

        orig_img = Image.open(img_path).convert("RGB")
        w, h = orig_img.size

        img_np = np.array(orig_img)
        augmented = augs(image=img_np)
        tensor = augmented["image"].unsqueeze(0).to(device)

        with torch.no_grad():
            logits = model(tensor)["out"]
            pred = torch.argmax(logits, dim=1).cpu().numpy()[0]  # (512, 512)

        # Возвращаем к оригинальному размеру
        pred_pil = Image.fromarray(pred.astype(np.uint8))
        pred_resized = pred_pil.resize((w, h), Image.NEAREST)
        pred_np = np.array(pred_resized)  # финальный numpy-массив

        # 1. чистая ч\б маска
        pred_resized.save(save_dir / f"{name}.png")

        # 2. Цветная маска
        make_color_mask(pred_np).save(save_dir / f"{name}_color.png")

        # 3. Оверлей
        make_overlay(orig_img, pred_np, args.overlay_alpha).save(save_dir / f"{name}_overlay.png")

        print(f"✓ {name} — сохранено 3 файла (ч/б маска имеет уникальные значения: {np.unique(pred_np)})")

    print("Готово! Чистые маски для evaluate.py лежат как {name}.png")


if __name__ == "__main__":
    main()