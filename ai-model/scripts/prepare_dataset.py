#!/usr/bin/env python3
"""
数据集准备脚本：将LabelMe格式的JSON标注转换为YOLO格式
支持first和third两个数据集的合并处理
"""

import os
import json
import shutil
import random
from pathlib import Path
import base64


# ============================================================
#  配置
# ============================================================
# 原始数据集根目录（包含 scan1/scan2/scan3 子目录）
DATASETS = [
    r"D:\松材线虫\标注\first",
    r"D:\松材线虫\标注\third",
]

# YOLO数据输出目录（相对于本脚本的上级目录）
SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR.parent / "data"
TRAIN_IMAGES = OUTPUT_DIR / "images" / "train"
VAL_IMAGES   = OUTPUT_DIR / "images" / "val"
TRAIN_LABELS = OUTPUT_DIR / "labels" / "train"
VAL_LABELS   = OUTPUT_DIR / "labels" / "val"

# 类别映射（统一为小写）
CLASS_MAP = {
    "vector insect": 0,
    "hsdoiaihod": 0,   # 噪声标注，同归为松材线虫
    "pine wilt": 0,
    "lesion": 0,
    "disease": 0,
}
CLASS_NAMES = ["pine_wilt_nematode"]   # 只有一个类别：松材线虫

VAL_RATIO = 0.2     # 20% 作为验证集
RANDOM_SEED = 42


def ensure_dirs():
    for d in [TRAIN_IMAGES, VAL_IMAGES, TRAIN_LABELS, VAL_LABELS]:
        d.mkdir(parents=True, exist_ok=True)


def collect_pairs(datasets):
    """收集所有 (image_path, json_path) 对"""
    pairs = []
    for ds_root in datasets:
        ds_path = Path(ds_root)
        if not ds_path.exists():
            print(f"[WARN] 数据集路径不存在: {ds_root}")
            continue
        for json_file in sorted(ds_path.rglob("*.json")):
            img_file = json_file.with_suffix(".png")
            if not img_file.exists():
                # 尝试 .jpg
                img_file = json_file.with_suffix(".jpg")
            if img_file.exists():
                pairs.append((img_file, json_file))
    print(f"共找到 {len(pairs)} 个标注图像对")
    return pairs


def labelme_to_yolo(json_path, img_w, img_h):
    """将LabelMe JSON转换为YOLO格式标注行列表"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = []
    for shape in data.get("shapes", []):
        label_raw = shape.get("label", "").strip().lower()
        cls_id = CLASS_MAP.get(label_raw, 0)   # 未知标签统一为0
        shape_type = shape.get("shape_type", "rectangle")
        points = shape.get("points", [])

        if not points:
            continue

        if shape_type == "rectangle" and len(points) == 2:
            x1, y1 = points[0]
            x2, y2 = points[1]
        elif shape_type == "polygon" and len(points) >= 3:
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            x1, x2 = min(xs), max(xs)
            y1, y2 = min(ys), max(ys)
        else:
            # 其它形状跳过
            continue

        # 归一化坐标
        xc = ((x1 + x2) / 2) / img_w
        yc = ((y1 + y2) / 2) / img_h
        bw = abs(x2 - x1) / img_w
        bh = abs(y2 - y1) / img_h

        # 截断到 [0,1]
        xc = max(0.0, min(1.0, xc))
        yc = max(0.0, min(1.0, yc))
        bw = max(0.001, min(1.0, bw))
        bh = max(0.001, min(1.0, bh))

        lines.append(f"{cls_id} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}")
    return lines


def write_yaml():
    """生成 dataset.yaml"""
    yaml_path = OUTPUT_DIR / "dataset.yaml"
    content = f"""# 松材线虫CT图像检测数据集
path: {OUTPUT_DIR.as_posix()}
train: images/train
val:   images/val

nc: {len(CLASS_NAMES)}
names: {CLASS_NAMES}
"""
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"dataset.yaml 已写入: {yaml_path}")
    return yaml_path


def main():
    random.seed(RANDOM_SEED)
    ensure_dirs()

    pairs = collect_pairs(DATASETS)
    if not pairs:
        print("[ERROR] 未找到任何图像-标注对，请检查数据集路径")
        return

    random.shuffle(pairs)
    n_val = max(1, int(len(pairs) * VAL_RATIO))
    val_pairs   = pairs[:n_val]
    train_pairs = pairs[n_val:]
    print(f"训练集: {len(train_pairs)}  验证集: {len(val_pairs)}")

    stats = {"train": 0, "val": 0, "skipped": 0}

    for split, split_pairs in [("train", train_pairs), ("val", val_pairs)]:
        img_dir = TRAIN_IMAGES if split == "train" else VAL_IMAGES
        lbl_dir = TRAIN_LABELS if split == "train" else VAL_LABELS

        for img_path, json_path in split_pairs:
            # 获取图像尺寸（从JSON元数据）
            with open(json_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            img_w = meta.get("imageWidth", 512)
            img_h = meta.get("imageHeight", 512)

            yolo_lines = labelme_to_yolo(json_path, img_w, img_h)
            if not yolo_lines:
                stats["skipped"] += 1
                continue

            # 复制图像
            dst_img = img_dir / img_path.name
            shutil.copy2(str(img_path), str(dst_img))

            # 写入标注
            lbl_name = img_path.stem + ".txt"
            with open(lbl_dir / lbl_name, "w") as f:
                f.write("\n".join(yolo_lines) + "\n")

            stats[split] += 1

    yaml_path = write_yaml()

    print(f"\n[完成] 数据集转换统计：")
    print(f"  训练集图像: {stats['train']}")
    print(f"  验证集图像: {stats['val']}")
    print(f"  跳过（无标注）: {stats['skipped']}")
    print(f"  YAML路径: {yaml_path}")


if __name__ == "__main__":
    main()
