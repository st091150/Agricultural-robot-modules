import os
import numpy as np
from PIL import Image
import torch
import segmentation_models_pytorch as smp
import albumentations as A
from albumentations.pytorch import ToTensorV2
import csv

# ================================
# PATHS 
# ================================
IMG_DIR = r"E:\wheat_segmentation_experiments\validation\img"
MASK_DIR = r"E:\wheat_segmentation_experiments\validation\mask"
MODEL_PATH = "wheat_unet_best.pth"

SAVE_CSV = r"E:\wheat_segmentation_experiments\metrics_results.csv"

# ================================
# Load model
# ================================
device = "cuda" if torch.cuda.is_available() else "cpu"

model = smp.Unet(
    encoder_name="resnet34",
    encoder_weights=None,
    in_channels=3,
    classes=1
)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.to(device)
model.eval()

# ================================
# Transforms (same as validation)
# ================================
transform = A.Compose([
    A.Resize(350, 350),
    A.Normalize(mean=(0.485, 0.456, 0.406),
                std=(0.229, 0.224, 0.225)),
    ToTensorV2()
])

# ================================
# Metric functions
# ================================
def compute_metrics(pred, gt):
    pred = pred.flatten()
    gt = gt.flatten()

    intersection = (pred * gt).sum()
    union = pred.sum() + gt.sum() - intersection

    dice = (2 * intersection) / (pred.sum() + gt.sum() + 1e-7)
    iou = intersection / (union + 1e-7)

    TP = ((pred == 1) & (gt == 1)).sum()
    FP = ((pred == 1) & (gt == 0)).sum()
    FN = ((pred == 0) & (gt == 1)).sum()

    precision = TP / (TP + FP + 1e-7)
    recall = TP / (TP + FN + 1e-7)

    return dice.item(), iou.item(), precision.item(), recall.item()

# ================================
# Loop over dataset
# ================================
results = []
dice_scores = []
iou_scores = []
precisions = []
recalls = []

print("Computing metrics over dataset...")

for name in os.listdir(IMG_DIR):
    if not name.endswith(".png"):
        continue

    img_path = os.path.join(IMG_DIR, name)
    mask_path = os.path.join(MASK_DIR, name)

    # Load image & mask
    img = Image.open(img_path).convert("RGB")
    mask_gt = Image.open(mask_path).convert("L")

    img_np = np.array(img)
    mask_np = np.array(mask_gt)
    mask_np = (mask_np > 0).astype(np.uint8)

    # Transform image
    aug = transform(image=img_np)
    x = aug["image"].unsqueeze(0).to(device)

    # Predict
    with torch.no_grad():
        logits = model(x)
        probs = torch.sigmoid(logits)[0, 0].cpu().numpy()

    # Resize prediction to original size
    probs = Image.fromarray((probs * 255).astype(np.uint8)).resize(img.size)
    pred_mask = (np.array(probs) > 128).astype(np.uint8)

    # Compute metrics
    dice, iou, precision, recall = compute_metrics(pred_mask, mask_np)

    dice_scores.append(dice)
    iou_scores.append(iou)
    precisions.append(precision)
    recalls.append(recall)

    results.append([name, dice, iou, precision, recall])

    print(f"{name}: Dice={dice:.4f}, IoU={iou:.4f}")

# ================================
# Output overall metrics
# ================================
avg_dice = np.mean(dice_scores)
avg_iou = np.mean(iou_scores)
avg_precision = np.mean(precisions)
avg_recall = np.mean(recalls)

print("\n========== FINAL METRICS ==========")
print(f"Average Dice:      {avg_dice:.4f}")
print(f"Average IoU:       {avg_iou:.4f}")
print(f"Average Precision: {avg_precision:.4f}")
print(f"Average Recall:    {avg_recall:.4f}")
print("===================================\n")

# ================================
# Save CSV
# ================================
with open(SAVE_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["image", "dice", "iou", "precision", "recall"])
    writer.writerows(results)

print("Metrics saved to:", SAVE_CSV)
