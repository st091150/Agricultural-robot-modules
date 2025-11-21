# datasets/weed_dataset.py
from torch.utils.data import Dataset
from PIL import Image
import numpy as np
import albumentations as A

class WeedDataset(Dataset):
    def __init__(self, txt_file, image_dir, mask_dir, transform=None):
        with open(txt_file) as f:
            self.names = [line.strip() for line in f if line.strip()]

        self.image_dir = image_dir
        self.mask_dir = mask_dir
        self.transform = transform

    def __len__(self):
        return len(self.names)

    def __getitem__(self, idx):
        name = self.names[idx]
        img_path = f"{self.image_dir}/{name}.png"
        mask_path = f"{self.mask_dir}/{name}.png"

        image = np.array(Image.open(img_path).convert("RGB"))
        mask = np.array(Image.open(mask_path).convert("L"))

        mask = (mask).astype(np.int64)

        if self.transform:
            augmented = self.transform(image=image, mask=mask)
            image = augmented['image']
            mask = augmented['mask']

        return image, mask.long()