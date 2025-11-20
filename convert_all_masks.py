import os
import json
import zlib
import base64
from io import BytesIO

import numpy as np
from PIL import Image


def decode_one_json(json_path, save_path):
    with open(json_path, "r") as f:
        data = json.load(f)

    H = data["size"]["height"]
    W = data["size"]["width"]
    full_mask = np.zeros((H, W), dtype=np.uint8)

    for obj in data["objects"]:
        bmp = obj["bitmap"]
        origin_x, origin_y = bmp["origin"]

        compressed = base64.b64decode(bmp["data"])
        png_bytes = zlib.decompress(compressed)

        sub_img = Image.open(BytesIO(png_bytes)).convert("L")
        sub_mask = np.array(sub_img)
        sub_mask = (sub_mask > 0).astype(np.uint8)

        h, w = sub_mask.shape
        full_mask[origin_y:origin_y + h, origin_x:origin_x + w] = np.maximum(
            full_mask[origin_y:origin_y + h, origin_x:origin_x + w],
            sub_mask,
        )

    out_img = Image.fromarray(full_mask * 255)
    out_img.save(save_path)


def process_split(root, split):
    ann_dir = os.path.join(root, split, "ann")
    out_dir = os.path.join(root, split, "mask")
    os.makedirs(out_dir, exist_ok=True)

    for name in os.listdir(ann_dir):
        if not name.endswith(".json"):
            continue
        in_path = os.path.join(ann_dir, name)
        clean_name = name.replace(".png.json", ".png")
        out_path = os.path.join(out_dir, clean_name)
        decode_one_json(in_path, out_path)
        print(f"{split}: saved {out_path}")


if __name__ == "__main__":
    ROOT = r"E:\wheat_segmentation_experiments"
    for split in ["train", "validation", "test"]:
        print(f"Processing {split}...")
        process_split(ROOT, split)
    print("Done all splits.")
