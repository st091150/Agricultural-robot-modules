import os
import numpy as np
from PIL import Image

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

import albumentations as A
from albumentations.pytorch import ToTensorV2
import segmentation_models_pytorch as smp
from tqdm import tqdm


# ===========================
# Dataset
# ===========================
class WheatSegDataset(Dataset):
    def __init__(self, img_dir, mask_dir, transforms=None):
        self.img_dir = img_dir
        self.mask_dir = mask_dir
        self.names = sorted([n for n in os.listdir(img_dir) if n.endswith(".png")])
        self.transforms = transforms

    def __len__(self):
        return len(self.names)

    def __getitem__(self, idx):
        name = self.names[idx]
        img_path = os.path.join(self.img_dir, name)
        mask_path = os.path.join(self.mask_dir, name)

        img = Image.open(img_path).convert("RGB")
        mask = Image.open(mask_path).convert("L")

        img = np.array(img)
        mask = np.array(mask)

        mask = (mask > 0).astype("float32")

        if self.transforms is not None:
            augmented = self.transforms(image=img, mask=mask)
            img = augmented["image"]
            mask = augmented["mask"].unsqueeze(0).float()
        else:
            img = torch.from_numpy(img).permute(2, 0, 1).float() / 255.0
            mask = torch.from_numpy(mask).unsqueeze(0).float()

        return img, mask


# ===========================
# Paths
# ===========================
TRAIN_IMG_DIR = r"E:\wheat_segmentation_experiments\train\img"
TRAIN_MASK_DIR = r"E:\wheat_segmentation_experiments\train\mask"
VAL_IMG_DIR = r"E:\wheat_segmentation_experiments\validation\img"
VAL_MASK_DIR = r"E:\wheat_segmentation_experiments\validation\mask"


# ===========================
# Transforms
# ===========================
train_transforms = A.Compose(
    [
        A.Resize(350, 350),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.RandomRotate90(p=0.5),
        A.ShiftScaleRotate(shift_limit=0.05, scale_limit=0.1, rotate_limit=15, p=0.5),
        A.RandomBrightnessContrast(p=0.3),
        A.Normalize(mean=(0.485, 0.456, 0.406),
                    std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ]
)

val_transforms = A.Compose(
    [
        A.Resize(350, 350),
        A.Normalize(mean=(0.485, 0.456, 0.406),
                    std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ]
)

train_ds = WheatSegDataset(TRAIN_IMG_DIR, TRAIN_MASK_DIR, transforms=train_transforms)
val_ds = WheatSegDataset(VAL_IMG_DIR, VAL_MASK_DIR, transforms=val_transforms)

train_loader = DataLoader(train_ds, batch_size=8, shuffle=True, num_workers=0, pin_memory=True)
val_loader = DataLoader(val_ds, batch_size=8, shuffle=False, num_workers=0, pin_memory=True)


# ===========================
# Model, Loss, Optimizer
# ===========================
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)

model = smp.Unet(
    encoder_name="resnet34",
    encoder_weights="imagenet",
    in_channels=3,
    classes=1,
)
model = model.to(device)

bce = nn.BCEWithLogitsLoss()
dice_loss = smp.losses.DiceLoss(mode="binary")


def criterion(logits, targets):
    return 0.5 * bce(logits, targets) + 0.5 * dice_loss(logits, targets)


optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)


# ===========================
# Metrics
# ===========================
def compute_iou_and_dice(preds, targets):
    preds = preds.view(-1)
    targets = targets.view(-1)

    intersection = (preds * targets).sum()
    union = preds.sum() + targets.sum() - intersection
    dice = (2 * intersection) / (preds.sum() + targets.sum() + 1e-7)
    iou = intersection / (union + 1e-7)
    return iou.item(), dice.item()


# ===========================
# Train / Val Loop
# ===========================
EPOCHS = 30
best_val_dice = 0.0

for epoch in range(EPOCHS):
    model.train()
    train_losses = []

    pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{EPOCHS} [Train]")
    for imgs, masks in pbar:
        imgs = imgs.to(device)
        masks = masks.to(device)

        optimizer.zero_grad()
        logits = model(imgs)
        loss = criterion(logits, masks)
        loss.backward()
        optimizer.step()

        train_losses.append(loss.item())
        pbar.set_postfix({"loss": f"{loss.item():.4f}"})

    avg_train_loss = np.mean(train_losses)

    model.eval()
    val_losses = []
    val_ious = []
    val_dices = []

    with torch.no_grad():
        for imgs, masks in val_loader:
            imgs = imgs.to(device)
            masks = masks.to(device)

            logits = model(imgs)
            loss = criterion(logits, masks)
            val_losses.append(loss.item())

            probs = torch.sigmoid(logits)
            preds = (probs > 0.5).float()

            iou, dice = compute_iou_and_dice(preds, masks)
            val_ious.append(iou)
            val_dices.append(dice)

    avg_val_loss = np.mean(val_losses)
    avg_val_iou = np.mean(val_ious)
    avg_val_dice = np.mean(val_dices)

    print(
        f"Epoch {epoch+1}/{EPOCHS} "
        f"- Train Loss: {avg_train_loss:.4f} "
        f"- Val Loss: {avg_val_loss:.4f} "
        f"- Val IoU: {avg_val_iou:.4f} "
        f"- Val Dice: {avg_val_dice:.4f}"
    )

    if avg_val_dice > best_val_dice:
        best_val_dice = avg_val_dice
        torch.save(model.state_dict(), "wheat_unet_best.pth")
        print(f"  -> New best model saved! Dice={best_val_dice:.4f}")

print("Training finished. Best Val Dice:", best_val_dice)
