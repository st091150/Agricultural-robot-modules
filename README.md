# 🌾 Wheat Detection with YOLOv8

This project uses **YOLOv8** to detect **wheat** in field images.

## 📘 Overview
- Model: `YOLOv8n`
- Task: Single-class detection (`wheat`)
- Framework: Ultralytics YOLOv8 + PyTorch
- Device: NVIDIA RTX 4060 Laptop GPU

## ⚙️ Usage
1. Install environment:
```bash
pip install -r requirements.txt
```
Run prediction:

```bash
yolo task=detect mode=predict model=best.pt source=images/test save=True conf=0.45
```
Results are saved to:

```bash
runs/detect/predict/
```
## 📁 Dataset
Custom dataset with YOLO-format labels:

data/
 ├── images/{train,val,test}
 └── labels/{train,val,test}
