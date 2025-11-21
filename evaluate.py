# evaluate.py
from utils.metrics import evaluate_segmentation
from config import *
from PIL import Image
import numpy as np

with open(TEST_LIST) as f:
    names = [x.strip() for x in f]

gt_list, pred_list = [], []
for name in names:
    gt = np.array(Image.open(f"{MASKS_DIR}/{name}.png").convert("L"))
    pred = np.array(Image.open(f"{PRED_DIR}/{name}.png").convert("L"))
    gt_list.append(gt)
    pred_list.append(pred)

evaluate_segmentation(gt_list, pred_list, NUM_CLASSES)