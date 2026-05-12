#!/usr/bin/env python3
"""
多YOLO模型训练脚本
支持：YOLOv5, YOLOv8, YOLOv9, YOLOv10
自动下载权重，依次训练并保存最优权重到 ../weights/
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

SCRIPT_DIR  = Path(__file__).parent
MODEL_DIR   = SCRIPT_DIR.parent
DATA_YAML   = MODEL_DIR / "data" / "dataset.yaml"
WEIGHTS_DIR = MODEL_DIR / "weights"
RESULTS_DIR = MODEL_DIR / "results"
RUNS_DIR    = MODEL_DIR / "runs"

WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ── 训练配置 ──────────────────────────────────────────────
EPOCHS      = 50
IMG_SIZE    = 512
BATCH_SIZE  = 8
DEVICE      = "cpu"   # 改为 "0" 使用 GPU

# ── 模型定义 ──────────────────────────────────────────────
MODELS = [
    {
        "name":    "yolov5s",
        "type":    "yolov5",
        "weights": "yolov5s.pt",
    },
    {
        "name":    "yolov5m",
        "type":    "yolov5",
        "weights": "yolov5m.pt",
    },
    {
        "name":    "yolov8n",
        "type":    "ultralytics",
        "weights": "yolov8n.pt",
    },
    {
        "name":    "yolov8s",
        "type":    "ultralytics",
        "weights": "yolov8s.pt",
    },
    {
        "name":    "yolov9t",
        "type":    "ultralytics",
        "weights": "yolov9t.pt",
    },
    {
        "name":    "yolov10n",
        "type":    "ultralytics",
        "weights": "yolov10n.pt",
    },
]


def install_dependencies():
    """安装所需依赖"""
    print("正在安装依赖……")
    pkgs = [
        "torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu",
        "ultralytics",
        "opencv-python",
        "matplotlib",
        "seaborn",
        "pandas",
        "pillow",
        "pyyaml",
    ]
    for pkg in pkgs:
        subprocess.run(
            f"{sys.executable} -m pip install {pkg} -q",
            shell=True, check=False
        )

    # YOLOv5 仓库
    yolov5_dir = MODEL_DIR / "yolov5"
    if not yolov5_dir.exists():
        subprocess.run(
            "git clone https://github.com/ultralytics/yolov5.git " + str(yolov5_dir),
            shell=True, check=False
        )
        subprocess.run(
            f"{sys.executable} -m pip install -r {yolov5_dir / 'requirements.txt'} -q",
            shell=True, check=False
        )
    print("依赖安装完成")


def train_yolov5(model_cfg: dict) -> Path:
    """使用YOLOv5训练"""
    yolov5_dir = MODEL_DIR / "yolov5"
    run_name   = model_cfg["name"]
    out_dir    = RUNS_DIR / "yolov5" / run_name

    cmd = (
        f"{sys.executable} {yolov5_dir / 'train.py'} "
        f"--img {IMG_SIZE} "
        f"--batch {BATCH_SIZE} "
        f"--epochs {EPOCHS} "
        f"--data {DATA_YAML} "
        f"--weights {model_cfg['weights']} "
        f"--name {run_name} "
        f"--project {RUNS_DIR / 'yolov5'} "
        f"--device {DEVICE} "
        f"--exist-ok"
    )
    print(f"\n[YOLOv5] 训练 {run_name}...")
    print(f"命令: {cmd}")
    subprocess.run(cmd, shell=True, check=False)

    best_pt = out_dir / "weights" / "best.pt"
    if best_pt.exists():
        dst = WEIGHTS_DIR / f"{run_name}_best.pt"
        shutil.copy2(best_pt, dst)
        print(f"✓ 权重已保存: {dst}")
        return dst
    return None


def train_ultralytics(model_cfg: dict) -> Path:
    """使用 ultralytics YOLO 训练（YOLOv8/v9/v10）"""
    run_name = model_cfg["name"]

    train_script = f"""
from ultralytics import YOLO
import shutil
from pathlib import Path

model = YOLO('{model_cfg["weights"]}')
results = model.train(
    data=r'{DATA_YAML}',
    epochs={EPOCHS},
    imgsz={IMG_SIZE},
    batch={BATCH_SIZE},
    name='{run_name}',
    project=r'{RUNS_DIR / "ultralytics"}',
    device='{DEVICE}',
    exist_ok=True,
    verbose=True,
)

# 复制最优权重
out_dir = Path(r'{RUNS_DIR / "ultralytics"}') / '{run_name}'
best_pt = out_dir / 'weights' / 'best.pt'
weights_dir = Path(r'{WEIGHTS_DIR}')
if best_pt.exists():
    dst = weights_dir / '{run_name}_best.pt'
    shutil.copy2(best_pt, dst)
    print(f'权重已保存: {{dst}}')
"""
    print(f"\n[Ultralytics] 训练 {run_name}...")
    result = subprocess.run(
        [sys.executable, "-c", train_script],
        capture_output=False, text=True
    )

    dst = WEIGHTS_DIR / f"{run_name}_best.pt"
    if dst.exists():
        print(f"✓ 权重已保存: {dst}")
        return dst
    return None


def train_all():
    """依次训练所有模型"""
    results = {}
    for model_cfg in MODELS:
        try:
            if model_cfg["type"] == "yolov5":
                w = train_yolov5(model_cfg)
            else:
                w = train_ultralytics(model_cfg)
            results[model_cfg["name"]] = str(w) if w else "FAILED"
        except Exception as e:
            print(f"[ERROR] {model_cfg['name']} 训练失败: {e}")
            results[model_cfg["name"]] = "ERROR"

    print("\n\n========== 训练汇总 ==========")
    for name, path in results.items():
        print(f"  {name}: {path}")
    return results


if __name__ == "__main__":
    install_dependencies()
    train_all()
