# Wheat Segmentation

This folder contains the dataset (train / validation / test) and the scripts
used for training, inference and metric evaluation of a wheat segmentation model
based on U-Net (ResNet34).

## Folder Structure
train/ # training images and masks
validation/ # validation images and masks
test/ # test images and masks

train_unet.py # model training script
predict_val.py # inference on validation set
predict_test.py # inference on test set
compute_metrics.py # calculate Dice / IoU / Precision / Recall
convert_all_masks.py# convert Eschikon JSON annotations to PNG masks
requirements.txt # project dependencies

## Usage

- Place images and masks into the `train/`, `validation/`, and `test/` folders.  
- Run `train_unet.py` to train the model.  
- Use `predict_*.py` scripts for inference.  
- Use `compute_metrics.py` to calculate evaluation metrics.

## Notes
- The trained model (`wheat_unet_best.pth`) is **not included** due to size.  
- Output folders (e.g., results) are generated automatically and not stored here.