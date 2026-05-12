<template>
  <div class="detect-page">
    <div class="page-title">🔬 CT图像松材线虫病检测</div>

    <el-row :gutter="20">
      <!-- 左侧：上传和参数配置 -->
      <el-col :span="10">
        <el-card shadow="hover" class="upload-card">
          <template #header><span>📁 上传CT图像</span></template>

          <!-- 上传组件 -->
          <el-upload
            class="upload-area"
            drag
            :auto-upload="false"
            accept=".png,.jpg,.jpeg,.bmp,.tiff"
            :limit="1"
            :file-list="fileList"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
          >
            <el-icon size="40" color="#2e7d32"><UploadFilled /></el-icon>
            <div style="margin-top:12px;font-size:14px;color:#666">
              拖拽文件到此处，或 <em style="color:#2e7d32">点击上传</em>
            </div>
            <template #tip>
              <div style="font-size:12px;color:#999;margin-top:6px">
                支持 PNG / JPG / BMP / TIFF，建议 512×512
              </div>
            </template>
          </el-upload>

          <!-- 预览 -->
          <div v-if="previewUrl" class="preview-box">
            <img :src="previewUrl" alt="预览" class="preview-img" />
          </div>

          <!-- 检测参数 -->
          <el-divider>检测参数</el-divider>
          <el-form label-width="90px" size="small">
            <el-form-item label="检测模型">
              <el-select v-model="modelName" style="width:100%">
                <el-option v-for="m in models" :key="m.value"
                  :value="m.value" :label="m.label" />
              </el-select>
            </el-form-item>
            <el-form-item label="置信度">
              <el-slider v-model="conf" :min="0.1" :max="0.9" :step="0.05" show-input />
            </el-form-item>
          </el-form>

          <el-button
            type="primary"
            size="large"
            style="width:100%;margin-top:8px"
            :loading="detecting"
            :disabled="!selectedFile"
            @click="startDetect"
          >
            <el-icon><VideoPlay /></el-icon>
            {{ detecting ? '检测中...' : '开始检测' }}
          </el-button>
        </el-card>
      </el-col>

      <!-- 右侧：检测结果 -->
      <el-col :span="14">
        <el-card shadow="hover" class="result-card" v-if="!result">
          <el-empty description="请上传CT图像并点击开始检测" :image-size="120">
            <template #image>
              <div style="font-size:80px">🌲</div>
            </template>
          </el-empty>
        </el-card>

        <el-card shadow="hover" v-else>
          <template #header>
            <div style="display:flex;align-items:center;justify-content:space-between">
              <span>🎯 检测结果</span>
              <el-tag :type="result.detectCount > 0 ? 'danger' : 'success'" size="large">
                {{ result.detectCount > 0 ? `发现 ${result.detectCount} 处病变` : '未检测到病变' }}
              </el-tag>
            </div>
          </template>

          <!-- 结果图像 -->
          <div class="result-image-area">
            <canvas ref="canvasRef" class="result-canvas" />
          </div>

          <!-- 检测列表 -->
          <el-divider>检测框详情</el-divider>
          <el-table :data="result.detections" stripe size="small">
            <el-table-column prop="label" label="标签" width="160">
              <template #default="{ row }">
                <el-tag type="danger" size="small">{{ row.label }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="置信度" width="100">
              <template #default="{ row }">
                <el-progress
                  :percentage="Math.round(row.confidence * 100)"
                  :stroke-width="10"
                  :color="row.confidence > 0.7 ? '#f56c6c' : '#e6a23c'"
                />
              </template>
            </el-table-column>
            <el-table-column label="边界框坐标">
              <template #default="{ row }">
                [{{ Math.round(row.bbox.x1) }}, {{ Math.round(row.bbox.y1) }}]
                → [{{ Math.round(row.bbox.x2) }}, {{ Math.round(row.bbox.y2) }}]
              </template>
            </el-table-column>
          </el-table>

          <!-- 摘要信息 -->
          <div class="result-meta">
            <el-descriptions :column="2" border size="small" style="margin-top:16px">
              <el-descriptions-item label="模型">{{ result.modelName }}</el-descriptions-item>
              <el-descriptions-item label="文件">{{ result.imageName }}</el-descriptions-item>
              <el-descriptions-item label="检测数量">{{ result.detectCount }}</el-descriptions-item>
              <el-descriptions-item label="任务ID">{{ result.taskId }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api/request'

const fileList = ref([])
const selectedFile = ref(null)
const previewUrl = ref(null)
const detecting = ref(false)
const result = ref(null)
const canvasRef = ref()
const modelName = ref('yolov8s')
const conf = ref(0.25)
const models = ref([
  { value: 'yolov8n', label: 'YOLOv8n (超轻量)' },
  { value: 'yolov8s', label: 'YOLOv8s (标准)' },
  { value: 'yolov5s', label: 'YOLOv5s' },
  { value: 'yolov5m', label: 'YOLOv5m' },
  { value: 'yolov9t', label: 'YOLOv9t' },
  { value: 'yolov10n', label: 'YOLOv10n' },
])

onMounted(async () => {
  try {
    const res = await api.get('/detection/models')
    if (res.data.data?.length) models.value = res.data.data
  } catch {}
})

function handleFileChange(file) {
  selectedFile.value = file.raw
  previewUrl.value = URL.createObjectURL(file.raw)
  result.value = null
}

function handleFileRemove() {
  selectedFile.value = null
  previewUrl.value = null
  result.value = null
}

async function startDetect() {
  if (!selectedFile.value) return
  detecting.value = true
  result.value = null

  try {
    const formData = new FormData()
    formData.append('image', selectedFile.value)
    formData.append('model', modelName.value)
    formData.append('conf', conf.value)

    const res = await api.post('/detection/detect', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    result.value = res.data.data
    await nextTick()
    drawResult()
    ElMessage.success(`检测完成，发现 ${result.value.detectCount} 处病变`)
  } catch (e) {
    ElMessage.error('检测失败: ' + e.message)
  } finally {
    detecting.value = false
  }
}

function drawResult() {
  if (!canvasRef.value || !result.value) return
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  const img = new Image()
  img.onload = () => {
    const maxW = 520
    const scale = maxW / img.width
    canvas.width  = maxW
    canvas.height = img.height * scale
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height)

    // 画检测框
    ctx.lineWidth = 2
    ctx.font = '13px Arial'
    for (const d of (result.value.detections || [])) {
      const { x1, y1, x2, y2 } = d.bbox
      const sx1 = x1 * scale, sy1 = y1 * scale
      const sw  = (x2 - x1) * scale, sh = (y2 - y1) * scale
      ctx.strokeStyle = '#ff4444'
      ctx.fillStyle   = 'rgba(255,68,68,0.15)'
      ctx.strokeRect(sx1, sy1, sw, sh)
      ctx.fillRect(sx1, sy1, sw, sh)
      // 标签
      const label = `${d.label} ${(d.confidence * 100).toFixed(0)}%`
      ctx.fillStyle = '#ff4444'
      ctx.fillRect(sx1, sy1 - 18, ctx.measureText(label).width + 8, 18)
      ctx.fillStyle = 'white'
      ctx.fillText(label, sx1 + 4, sy1 - 4)
    }

    // 结果图为空时用原图
    if (!result.value.resultImage) {
      result.value._canvasDataUrl = canvas.toDataURL()
    }
  }
  img.src = result.value.resultImage
    ? `data:image/png;base64,${result.value.resultImage}`
    : previewUrl.value
}
</script>

<style scoped>
.upload-area :deep(.el-upload-dragger) { padding: 20px; }
.preview-box { margin-top: 12px; text-align: center; }
.preview-img { max-width: 100%; max-height: 200px; border-radius: 6px; border: 1px solid #eee; }
.result-canvas { max-width: 100%; border-radius: 6px; display: block; margin: 0 auto; }
.result-image-area { text-align: center; background: #000; border-radius: 8px; padding: 8px; min-height: 100px; }
</style>
