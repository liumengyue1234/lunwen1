#!/usr/bin/env python3
"""
推理服务（Flask API）
供 SpringBoot 后端调用，接收图像并返回检测结果
"""

import os
import sys
import json
import uuid
import base64
import io
from pathlib import Path
from datetime import datetime

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# ── 路径 ────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).parent
MODEL_DIR   = SCRIPT_DIR.parent
WEIGHTS_DIR = MODEL_DIR / "weights"
UPLOAD_DIR  = MODEL_DIR.parent / "backend" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
CORS(app)

# ── 加载模型 ─────────────────────────────────────────────
loaded_models = {}

def load_model(model_name: str):
    """懒加载指定模型"""
    if model_name in loaded_models:
        return loaded_models[model_name]

    weight_path = WEIGHTS_DIR / f"{model_name}_best.pt"
    if not weight_path.exists():
        # fallback: 使用预训练权重（未训练时演示用）
        weight_path = None

    try:
        from ultralytics import YOLO
        if weight_path and weight_path.exists():
            model = YOLO(str(weight_path))
        else:
            model = YOLO(f"{model_name}.pt")
        loaded_models[model_name] = model
        print(f"[OK] 加载模型: {model_name}")
        return model
    except Exception as e:
        print(f"[ERROR] 模型加载失败 {model_name}: {e}")
        return None


AVAILABLE_MODELS = ["yolov8n", "yolov8s", "yolov5s", "yolov5m", "yolov9t", "yolov10n"]
DEFAULT_MODEL    = "yolov8s"

# 预加载默认模型
try:
    load_model(DEFAULT_MODEL)
except Exception:
    pass


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "time": datetime.now().isoformat()})


@app.route("/api/models", methods=["GET"])
def list_models():
    """返回可用模型列表"""
    models = []
    for name in AVAILABLE_MODELS:
        w = WEIGHTS_DIR / f"{name}_best.pt"
        models.append({
            "name": name,
            "trained": w.exists(),
            "path": str(w) if w.exists() else None,
        })
    return jsonify({"models": models, "default": DEFAULT_MODEL})


@app.route("/api/detect", methods=["POST"])
def detect():
    """
    POST body (multipart/form-data):
        image: 图像文件
        model: 模型名称（可选，默认yolov8s）
        conf:  置信度阈值（可选，默认0.25）
    """
    if "image" not in request.files:
        return jsonify({"error": "缺少 image 字段"}), 400

    file = request.files["image"]
    model_name = request.form.get("model", DEFAULT_MODEL)
    conf_thresh = float(request.form.get("conf", 0.25))

    # 保存上传图像
    img_id   = uuid.uuid4().hex
    img_name = f"{img_id}_{file.filename}"
    img_path = UPLOAD_DIR / img_name
    file.save(str(img_path))

    model = load_model(model_name)
    if model is None:
        return jsonify({"error": f"模型 {model_name} 加载失败"}), 500

    try:
        results = model.predict(
            source=str(img_path),
            conf=conf_thresh,
            imgsz=512,
            device="cpu",
            save=True,
            project=str(UPLOAD_DIR / "predict"),
            name=img_id,
            exist_ok=True,
        )

        detections = []
        for r in results:
            boxes = r.boxes
            if boxes is None:
                continue
            for box in boxes:
                xyxy  = box.xyxy[0].tolist()
                conf  = float(box.conf[0])
                cls   = int(box.cls[0])
                label = r.names[cls]
                detections.append({
                    "label": label,
                    "confidence": round(conf, 4),
                    "bbox": {
                        "x1": round(xyxy[0], 2),
                        "y1": round(xyxy[1], 2),
                        "x2": round(xyxy[2], 2),
                        "y2": round(xyxy[3], 2),
                    }
                })

        # 读取结果图
        result_img_path = UPLOAD_DIR / "predict" / img_id / img_name
        result_img_b64  = None
        if result_img_path.exists():
            with open(result_img_path, "rb") as f:
                result_img_b64 = base64.b64encode(f.read()).decode()

        response = {
            "id":          img_id,
            "model":       model_name,
            "image_name":  img_name,
            "detect_count":len(detections),
            "detections":  detections,
            "result_image":result_img_b64,
            "confidence_threshold": conf_thresh,
            "timestamp":   datetime.now().isoformat(),
        }
        return jsonify(response)

    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route("/api/image/<path:filename>")
def serve_image(filename):
    return send_from_directory(str(UPLOAD_DIR), filename)


if __name__ == "__main__":
    port = int(os.environ.get("AI_PORT", 5001))
    print(f"AI推理服务启动于 http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
