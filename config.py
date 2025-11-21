# config.py
DATA_ROOT = "/kaggle/input/deeplabv3/Weed_Seg/data"

TRAIN_LIST = f"{DATA_ROOT}/data_list/train.txt"
VAL_LIST   = f"{DATA_ROOT}/data_list/val.txt"
TEST_LIST  = f"{DATA_ROOT}/data_list/test.txt"

IMAGES_DIR = f"{DATA_ROOT}/images"
MASKS_DIR  = f"{DATA_ROOT}/mask"
PRED_DIR = "/kaggle/input/deeplabv3/Weed_Seg/predictions"

NUM_CLASSES = 3
INPUT_SIZE = 512

DEFAULT_BATCH_SIZE = 8
DEFAULT_EPOCHS = 50
DEFAULT_LR = 1e-4
DEFAULT_MODEL_PATH = "/kaggle/working/best_model.pth"