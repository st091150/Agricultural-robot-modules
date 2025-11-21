# benchmark.py
import torch
import time
import json
import numpy as np
from PIL import Image
from pathlib import Path
from tqdm import tqdm
import pandas as pd

from config import *
from models.deeplab_mnv3 import build_model
from utils.augmentations import get_valid_augs


def benchmark(model_weights: str = "/content/drive/MyDrive/Weed_Seg/weights/best_model.pth"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    model = build_model(NUM_CLASSES).to(device)
    model.load_state_dict(torch.load(model_weights, map_location=device))
    model.eval()

    augs = get_valid_augs(INPUT_SIZE)

    with open(TEST_LIST) as f:
        names = [x.strip() for x in f if x.strip()]

    # Глобальная confusion matrix
    hist = np.zeros((NUM_CLASSES, NUM_CLASSES), dtype=np.float64)
    inference_times = []

    print(f"Бенчмарк на {len(names)} изображениях...\n")

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

        # Ресайз к оригинальному размеру
        pred_pil = Image.fromarray(pred.astype(np.uint8))
        pred_resized = pred_pil.resize((w, h), Image.NEAREST)
        pred_np = np.array(pred_resized)

        # GT
        gt = np.array(Image.open(mask_path).convert("L")).astype(np.int64)

        # Защита от мусорных классов после ресайза
        pred_np = np.clip(pred_np, 0, NUM_CLASSES - 1)
        gt = np.clip(gt, 0, NUM_CLASSES - 1)

        # Обновляем глобальную матрицу ошибок
        hist += np.bincount(
            NUM_CLASSES * gt.flatten() + pred_np.flatten(),
            minlength=NUM_CLASSES**2
        ).reshape(NUM_CLASSES, NUM_CLASSES)

    # =============== Метрики ===============
    tp = np.diag(hist)
    fp = hist.sum(axis=0) - tp
    fn = hist.sum(axis=1) - tp
    union = tp + fp + fn

    iou = tp / (union + 1e-10)
    valid = union > 0
    miou = np.mean(iou[valid]) if valid.any() else 0.0

    pixel_acc = tp.sum() / hist.sum()

    # F1 по классам
    precision = tp / (tp + fp + 1e-10)
    recall = tp / (tp + fn + 1e-10)
    f1 = 2 * precision * recall / (precision + recall + 1e-10)
    mean_f1 = np.mean(f1[valid]) if valid.any() else 0.0

    fps = 1.0 / (sum(inference_times) / len(inference_times))

    # =============== Сохранение результатов ===============
    out_dir = Path("/content/drive/MyDrive/Weed_Seg/results")
    out_dir.mkdir(exist_ok=True)

    class_names = ["Background", "Crop", "Weed"]

    # TXT отчёт
    with open(out_dir / "benchmark_report.txt", "w", encoding="utf-8") as f:
        f.write("═" * 60 + "\n")
        f.write("       WEED SEGMENTATION BENCHMARK REPORT\n")
        f.write("═" * 60 + "\n\n")
        f.write(f"Модель: {Path(model_weights).name}\n")
        f.write(f"Изображений: {len(names)}\n")
        f.write(f"Вход: {INPUT_SIZE}x{INPUT_SIZE}\n")
        f.write(f"FPS: {fps:.2f}\n\n")
        f.write(f"mIoU           : {miou:.4f}\n")
        f.write(f"Mean F1        : {mean_f1:.4f}\n")
        f.write(f"Pixel Accuracy : {pixel_acc:.4f}\n\n")
        f.write("IoU по классам:\n")
        for i in range(NUM_CLASSES):
            if valid[i]:
                f.write(f"   {class_names[i]:10} → {iou[i]:.4f}  (пикселей в GT: {int(hist.sum(1)[i]):,})\n")
            else:
                f.write(f"   {class_names[i]:10} →   —   (не встречался)\n")

    # JSON + CSV
    data = {
        "model": str(model_weights),
        "mIoU": float(miou),
        "mean_F1": float(mean_f1),
        "Pixel_Accuracy": float(pixel_acc),
        "FPS": float(fps),
        "per_class": {class_names[i]: {"IoU": float(iou[i]), "F1": float(f1[i])} for i in range(NUM_CLASSES)}
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(data, f, indent=2)

    pd.DataFrame({
        "Class": class_names + ["mIoU / mean F1"],
        "IoU": list(iou) + [miou],
        "F1": list(f1) + [mean_f1]
    }).to_csv(out_dir / "metrics.csv", index=False)

    print("\n" + "="*60)
    print(f"mIoU = {miou:.4f} | FPS = {fps:.2f}")
    print("Отчёт сохранён в results/")
    print("="*60)


if __name__ == "__main__":
    import sys
    weights = sys.argv[1] if len(sys.argv) > 1 else "weights/best_model.pth"
    benchmark(weights)