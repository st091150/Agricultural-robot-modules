# utils/metrics.py
import numpy as np

def evaluate_segmentation(gt_list, pred_list, num_classes=3, ignore_index=255):
    hist = np.zeros((num_classes, num_classes))

    for gt, pred in zip(gt_list, pred_list):
        # Обрезаем всё, что не 0/1/2 (шум от ресайза)
        gt = np.clip(gt, 0, num_classes-1)
        pred = np.clip(pred, 0, num_classes-1)

        # Игнорируем ignore_index
        if ignore_index is not None:
            mask = (gt != ignore_index)
            gt = gt[mask]
            pred = pred[mask]

        # Быстро строим histogram
        hist += np.bincount(
            num_classes * gt.astype(int) + pred.astype(int),
            minlength=num_classes**2
        ).reshape(num_classes, num_classes)

    # IoU
    tp = np.diag(hist)
    fp = hist.sum(axis=0) - tp
    fn = hist.sum(axis=1) - tp
    union = tp + fp + fn

    iou = tp / (union + 1e-9)
    
    # Если класс вообще не встретился в тесте — IoU не портит mIoU
    present = union > 0
    miou = np.mean(iou[present])

    print("=" * 60)
    print("   Класс   |   IoU    |   Пикселей в GT")
    print("-" * 60)
    for i in range(num_classes):
        pixels_in_gt = hist.sum(1)[i]
        if pixels_in_gt > 0 or hist.sum(0)[i] > 0:
            print(f"   {i} (class {i}) | {iou[i]:.4f}  | {int(pixels_in_gt):,}")
        else:
            print(f"   {i} (class {i}) |  —  (не было в тесте)")
    print("-" * 60)
    print(f"   mIoU          = {miou:.4f}")
    print(f"   Pixel Accuracy = {tp.sum() / hist.sum():.4f}")
    print("=" * 60)

    return miou