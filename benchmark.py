# benchmark.py — с выделением плохих примеров (IoU < 0.50)
import torch
import time
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from tqdm import tqdm
import pandas as pd

from config import *
from models.deeplab_mnv3 import build_model
from utils.augmentations import get_valid_augs

# Цвета для оверлея
COLOR_MAP = np.array([
    [0, 100, 0],   # 0 background
    [0, 255, 0],   # 1 crop
    [255, 0, 0],   # 2 weed
], dtype=np.uint8)

def make_overlay(orig_img: Image.Image, pred_np: np.ndarray, alpha=0.5):
    color = Image.fromarray(COLOR_MAP[pred_np])
    color = color.resize(orig_img.size, Image.NEAREST)
    return Image.blend(orig_img, color, alpha)

def per_image_iou(gt: np.ndarray, pred: np.ndarray, num_classes=3):
    ious = []
    for c in range(num_classes):
        gt_c = (gt == c)
        pred_c = (pred == c)
        inter = np.logical_and(gt_c, pred_c).sum()
        union = np.logical_or(gt_c, pred_c).sum()
        ious.append(inter / (union + 1e-8) if union > 0 else 1.0)
    return np.mean(ious)

def benchmark(model_weights: str = "/content/drive/MyDrive/Weed_Seg/weights/best_model.pth"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model(NUM_CLASSES).to(device)
    model.load_state_dict(torch.load(model_weights, map_location=device))
    model.eval()

    augs = get_valid_augs(INPUT_SIZE)

    with open(TEST_LIST) as f:
        names = [x.strip() for x in f if x.strip()]

    hist = np.zeros((NUM_CLASSES, NUM_CLASSES), dtype=np.float64)
    inference_times = []
    bad_cases = []  # список худших изображений

    print(f"Бенчмарк на {len(names)} изображениях + поиск плохих кейсов...\n")

    for name in tqdm(names, desc="Inference"):
        img_path = Path(IMAGES_DIR) / f"{name}.png"
        mask_path = Path(MASKS_DIR) / f"{name}.png"

        orig_img = Image.open(img_path).convert("RGB")
        w, h = orig_img.size

        img_np = np.array(orig_img)
        augmented = augs(image=img_np)
        tensor = augmented["image"].unsqueeze(0).to(device)

        start = time.time()
        with torch.no_grad():
            pred = model(tensor)["out"]
            pred = torch.argmax(pred, dim=1).cpu().numpy()[0]
        inference_times.append(time.time() - start)

        pred_pil = Image.fromarray(pred.astype(np.uint8))
        pred_resized = pred_pil.resize((w, h), Image.NEAREST)
        pred_np = np.array(pred_resized)
        pred_np = np.clip(pred_np, 0, NUM_CLASSES - 1)

        gt = np.array(Image.open(mask_path).convert("L")).astype(np.int64)
        gt = np.clip(gt, 0, NUM_CLASSES - 1)

        # Обновляем глобальную матрицу
        hist += np.bincount(
            NUM_CLASSES * gt.flatten() + pred_np.flatten(),
            minlength=NUM_CLASSES**2
        ).reshape(NUM_CLASSES, NUM_CLASSES)

        # Считаем IoU для текущего изображения
        img_iou = per_image_iou(gt, pred_np, NUM_CLASSES)

        # Если плохо — сохраняем как плохой кейс
        if img_iou < 0.50:
            bad_cases.append({
                "name": name,
                "iou": img_iou,
                "img_path": str(img_path)
            })

            # Сохраняем оверлей
            overlay = make_overlay(orig_img, pred_np, alpha=0.55)
            draw = ImageDraw.Draw(overlay)
            try:
                font = ImageFont.truetype("arial.ttf", 48)
            except:
                font = ImageFont.load_default()
            draw.text((20, 20), f"IoU = {img_iou:.3f}", fill=(255,255,255), font=font, stroke_width=3, stroke_fill=(0,0,0))

            bad_dir = Path("results/bad_cases")
            bad_dir.mkdir(parents=True, exist_ok=True)
            overlay.save(bad_dir / f"{name}_bad_iou_{img_iou:.3f}.png")

    # =============== Метрики ===============
    tp = np.diag(hist)
    union = hist.sum(1) + hist.sum(0) - tp
    iou = tp / (union + 1e-10)
    valid = union > 0
    miou = np.mean(iou[valid]) if valid.any() else 0.0
    pixel_acc = tp.sum() / hist.sum()
    fps = 1.0 / (np.mean(inference_times))

    class_names = ["Background", "Crop", "Weed"]

    # =============== Сохранение отчёта ===============
    out_dir = Path("/content/drive/MyDrive/Weed_Seg/results")
    out_dir.mkdir(exist_ok=True)

    with open(out_dir / "benchmark_report.txt", "w", encoding="utf-8") as f:
        f.write("WEED SEGMENTATION BENCHMARK + BAD CASES\n")
        f.write("="*60 + "\n")
        f.write(f"Модель: {Path(model_weights).name}\n")
        f.write(f"Тестовых изображений: {len(names)}\n")
        f.write(f"mIoU: {miou:.4f} | Pixel Acc: {pixel_acc:.4f} | FPS: {fps:.2f}\n\n")
        f.write("IoU по классам:\n")
        for i, name in enumerate(class_names):
            f.write(f"   {name:10} → {iou[i]:.4f}\n")
        f.write("\nПлохие кейсы (IoU < 0.50): {len(bad_cases)} из {len(names)}\n")
        for case in sorted(bad_cases, key=lambda x: x["iou"])[:20]:  # топ-20 худших
            f.write(f"   • {case['name']} → IoU = {case['iou']:.3f}\n")

    # JSON
    json_data = {
        "mIoU": float(miou),
        "Pixel_Accuracy": float(pixel_acc),
        "FPS": float(fps),
        "bad_cases_count": len(bad_cases),
        "bad_cases": [c["name"] for c in sorted(bad_cases, key=lambda x: x["iou"])[:50]]
    }
    with open(out_dir / "summary.json", "w") as f:
        json.dump(json_data, f, indent=2)

    print("\nБенчмарк завершён!")
    print(f"mIoU = {miou:.4f} | Плохих кейсов (IoU<0.5): {len(bad_cases)}/{len(names)}")
    print(f"Плохие примеры сохранены в results/bad_cases/")
    print(f"Отчёт → results/benchmark_report.txt")

if __name__ == "__main__":
    import sys
    weights = sys.argv[1] if len(sys.argv) > 1 else "weights/best_model.pth"
    benchmark(weights)