import os
import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F
import segmentation_models_pytorch as smp

import albumentations as A
from albumentations.pytorch import ToTensorV2

# ================================
# Paths
# ================================
MODEL_PATH = "wheat_unet_best.pth"
IMG_DIR = r"E:\wheat_segmentation_experiments\validation\img"
SAVE_DIR = r"E:\wheat_segmentation_experiments\val_results"

os.makedirs(SAVE_DIR, exist_ok=True)

# ================================
# Model
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
# Preprocess (same as validation)
# ================================
val_transform = A.Compose([
    A.Resize(350, 350),
    A.Normalize(mean=(0.485, 0.456, 0.406),
                std=(0.229, 0.224, 0.225)),
    ToTensorV2()
])

# ================================
# Prediction loop
# ================================
print("Running inference on validation set...")

for name in os.listdir(IMG_DIR):
    if not name.endswith(".png"):
        continue

    img_path = os.path.join(IMG_DIR, name)
    img = Image.open(img_path).convert("RGB")
    img_np = np.array(img)

    # Transform
    aug = val_transform(image=img_np)
    x = aug["image"].unsqueeze(0).to(device)

    # Predict
    with torch.no_grad():
        logits = model(x)
        probs = torch.sigmoid(logits)[0, 0].cpu().numpy()

    # Resize back to original size
    probs = (probs * 255).astype(np.uint8)
    pred_mask = Image.fromarray(probs).resize(img.size)

    # Threshold binary mask
    mask_bin = pred_mask.point(lambda p: 255 if p > 128 else 0)

    # Save results
    base = name.replace(".png", "")

    img.save(os.path.join(SAVE_DIR, f"{base}_original.png"))
    mask_bin.save(os.path.join(SAVE_DIR, f"{base}_pred_mask.png"))

    # Create overlay (red mask on image)
    overlay = img.copy()
    overlay_np = np.array(overlay)
    mask_np = np.array(mask_bin)

    overlay_np[mask_np == 255] = [255, 0, 0]  
    overlay = Image.fromarray(overlay_np)
    overlay.save(os.path.join(SAVE_DIR, f"{base}_overlay.png"))

    print(f"Saved: {base}")

print("Done! Results are in:", SAVE_DIR)
