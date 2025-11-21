# train.py
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.amp import autocast, GradScaler   
from tqdm import tqdm
import argparse
from pathlib import Path

from config import *
from models.deeplab_mnv3 import build_model
from datasets.weed_dataset import WeedDataset
from utils.augmentations import get_train_augs, get_valid_augs


def parse_args():
    parser = argparse.ArgumentParser(description="Weed Segmentation — DeepLabV3 MobileNetV3 Training")
    parser.add_argument("--root-dir", type=str, default=None,
                        help="Root directory of dataset (overrides config.py)")
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--lr", type=float, default=DEFAULT_LR)
    parser.add_argument("--input-size", type=int, default=INPUT_SIZE)
    parser.add_argument("--weights-dir", type=str, default="/kaggle/working/weights")
    parser.add_argument("--resume", type=str, default=None, help="Path to .pth to resume")
    return parser.parse_args()


def train_one_epoch(model, loader, criterion, optimizer, scaler, device):
    model.train()
    total = 0
    for imgs, masks in tqdm(loader, desc="Train", leave=False):
        imgs = imgs.to(device)
        masks = masks.to(device)

        with autocast('cuda'):
            out = model(imgs)["out"]
            loss = criterion(out, masks)

        optimizer.zero_grad()
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        total += loss.item()
    return total / len(loader)


def validate(model, loader, criterion, device):
    model.eval()
    total = 0
    with torch.no_grad():
        for imgs, masks in tqdm(loader, desc="Val", leave=False):
            imgs = imgs.to(device)
            masks = masks.to(device)
            with autocast('cuda'):
                out = model(imgs)["out"]
                loss = criterion(out, masks)
            total += loss.item()
    return total / len(loader)


def main():
    args = parse_args()

    # Переопределяем пути, если указан root-dir
    global TRAIN_LIST, VAL_LIST, TEST_LIST, IMAGES_DIR, MASKS_DIR
    if args.root_dir:
        root = Path(args.root_dir)
        TRAIN_LIST = root / "data_list/train.txt"
        VAL_LIST   = root / "data_list/val.txt"
        TEST_LIST  = root / "data_list/test.txt"
        IMAGES_DIR = root / "images"
        MASKS_DIR  = root / "mask"

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print(f"Dataset root: {Path(IMAGES_DIR).parent}")

    weights_dir = Path(args.weights_dir)
    weights_dir.mkdir(parents=True, exist_ok=True)

    train_transform = get_train_augs(args.input_size)
    val_transform   = get_valid_augs(args.input_size)

    train_ds = WeedDataset(str(TRAIN_LIST), str(IMAGES_DIR), str(MASKS_DIR), train_transform)
    val_ds   = WeedDataset(str(VAL_LIST),   str(IMAGES_DIR), str(MASKS_DIR), val_transform)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=4, pin_memory=True, drop_last=True)
    val_loader   = DataLoader(val_ds,   batch_size=args.batch_size, shuffle=False, num_workers=4, pin_memory=True)

    model = build_model(num_classes=NUM_CLASSES, pretrained=True).to(device)

    criterion = nn.CrossEntropyLoss(ignore_index=255)
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scaler = GradScaler('cuda')

    best_loss = float('inf')
    start_epoch = 1

    if args.resume:
        ckpt = torch.load(args.resume, map_location=device)
        model.load_state_dict(ckpt)
        start_epoch = int(Path(args.resume).stem.split('_')[-1]) + 1 if 'epoch' in args.resume else 1
        print(f"Resumed from {args.resume}, continue from epoch {start_epoch}")

    print(f"\nTraining started — {args.epochs} epochs\n")

    for epoch in range(start_epoch, args.epochs + 1):
        train_loss = train_one_epoch(model, train_loader, criterion, optimizer, scaler, device)
        val_loss = validate(model, val_loader, criterion, device)

        print(f"Epoch {epoch:03d} | Train: {train_loss:.5f} | Val: {val_loss:.5f}")

        # Сохраняем каждую эпоху + лучшую
        epoch_path = weights_dir / f"epoch_{epoch:03d}.pth"
        torch.save(model.state_dict(), epoch_path)
        print(f"   Saved: {epoch_path.name}")

        if val_loss < best_loss:
            best_loss = val_loss
            best_path = weights_dir / "best_model.pth"
            torch.save(model.state_dict(), best_path)
            print(f"   BEST → {best_path.name} ({val_loss:.5f})")

    print("\nОбучение завершено! Все веса в:", weights_dir)


if __name__ == "__main__":
    main()