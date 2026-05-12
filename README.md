# 🌲 松材线虫病CT图像检测系统

> 东北林业大学 · 软件工程 2022级4班 · 刘昕月（2022222997）  
> 指导教师：邱兆文 教授 · 企业导师：高启 工程师

---

## 系统功能

- **CT图像上传与检测**：支持 PNG/JPG/BMP/TIFF 格式CT图像上传
- **多模型检测**：集成 YOLOv5s/v5m、YOLOv8n/v8s、YOLOv9t、YOLOv10n 六个模型
- **可视化结果**：自动标注病变区域、绘制检测框、显示置信度
- **历史记录**：记录所有检测任务，支持分页查询
- **评估报告**：多模型性能对比（mAP、Precision、Recall），雷达图可视化

---

## 技术架构

```
pine-wilt-detection/
├── frontend/           # Vue 3 + Vite + Element Plus
├── backend/            # Spring Boot 3 + MyBatis-Plus + JWT
└── ai-model/           # Python + PyTorch + YOLOv5/v8/v9/v10
    ├── scripts/
    │   ├── prepare_dataset.py   # 数据预处理（LabelMe → YOLO）
    │   ├── train_models.py      # 多模型训练
    │   ├── evaluate_models.py   # 评估报告生成
    │   └── inference_server.py  # Flask API推理服务
    ├── data/                    # 训练数据集（YOLO格式）
    ├── weights/                 # 训练好的模型权重
    └── results/                 # 评估报告
```

---

## 快速启动

### 前置条件

- Node.js 18+
- Python 3.10+
- Java 17+ & Maven 3.8+

---

### Step 1：数据预处理

```bash
cd ai-model
pip install -r requirements.txt

# 将 LabelMe 标注转换为 YOLO 格式
python scripts/prepare_dataset.py
```

> 数据集路径已配置为 `D:\松材线虫\标注\first` 和 `D:\松材线虫\标注\third`  
> 若路径不同请修改 `prepare_dataset.py` 中的 `DATASETS` 列表

---

### Step 2：训练模型（可选，GPU 推荐）

```bash
cd ai-model
python scripts/train_models.py
```

> 会依次训练 YOLOv5s/m、YOLOv8n/s、YOLOv9t、YOLOv10n  
> 训练好的权重保存在 `ai-model/weights/`  
> 首次使用可跳过此步，系统将使用预训练权重（演示模式）

---

### Step 3：启动 AI 推理服务

```bash
cd ai-model
python scripts/inference_server.py
# 服务启动在 http://localhost:5001
```

---

### Step 4：启动后端

```bash
cd backend
mvn spring-boot:run
# 或双击 start-backend.bat
# 服务启动在 http://localhost:8080
```

---

### Step 5：启动前端

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:3000
```

---

### 一键启动（Windows）

```bash
# 在项目根目录
start-all.bat
```

---

## 默认账号

| 账号       | 密码      | 权限   |
|-----------|----------|-------|
| admin     | admin123 | 管理员 |
| liuxinyue | user123  | 普通用户 |

---

## API 接口说明

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/login` | POST | 登录获取Token |
| `/api/auth/register` | POST | 注册新用户 |
| `/api/detection/detect` | POST | 上传图像检测（multipart） |
| `/api/detection/history` | GET | 获取历史记录 |
| `/api/detection/task/{id}` | GET | 获取任务详情 |
| `/api/detection/models` | GET | 获取可用模型列表 |

---

## 模型性能（演示数据）

| 模型       | mAP@0.5 | Precision | Recall |
|-----------|--------|-----------|--------|
| YOLOv5s   | 82.3%  | 86.1%     | 79.8%  |
| YOLOv5m   | 85.4%  | 87.9%     | 83.2%  |
| YOLOv8n   | 84.1%  | 85.6%     | 81.9%  |
| YOLOv8s   | 87.2%  | 89.1%     | 85.1%  |
| YOLOv9t   | 86.5%  | 88.3%     | 84.3%  |
| **YOLOv10n** | **87.9%** | **89.8%** | **85.7%** |

---

## 生成评估报告

```bash
cd ai-model
python scripts/evaluate_models.py
# 报告保存在 ai-model/results/evaluation_report.html
```

---

## License

MIT © 2026 刘昕月 · 东北林业大学
