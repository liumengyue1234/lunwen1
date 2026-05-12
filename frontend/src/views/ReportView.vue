<template>
  <div>
    <div class="page-title">📊 模型评估报告</div>
    <el-card shadow="hover">
      <template #header>
        <div style="display:flex;align-items:center;justify-content:space-between">
          <span>多模型性能对比</span>
          <el-button type="success" @click="exportReport" size="small">
            <el-icon><Download /></el-icon> 导出报告
          </el-button>
        </div>
      </template>

      <!-- 性能指标表格 -->
      <el-table :data="modelResults" stripe border>
        <el-table-column prop="model" label="模型名称" width="140">
          <template #default="{ row }">
            <strong>{{ row.model }}</strong>
            <el-tag v-if="row.isBest" type="danger" size="small" style="margin-left:6px">最优</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="mAP@0.5" width="110">
          <template #default="{ row }">
            <el-progress :percentage="Math.round(row.mAP50 * 100)" :color="mapColor(row.mAP50)" :stroke-width="12" />
            <div style="font-size:12px;text-align:right;margin-top:2px">{{ (row.mAP50 * 100).toFixed(1) }}%</div>
          </template>
        </el-table-column>
        <el-table-column label="mAP@0.5:0.95" width="130">
          <template #default="{ row }">{{ (row.mAP50_95 * 100).toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column label="Precision" width="110">
          <template #default="{ row }">{{ (row.precision * 100).toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column label="Recall" width="110">
          <template #default="{ row }">{{ (row.recall * 100).toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'ok' ? 'success' : 'danger'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <!-- ECharts 图表 -->
      <div ref="radarRef" style="height:360px;margin-top:24px" />
    </el-card>

    <!-- 指标说明 -->
    <el-card shadow="hover" style="margin-top:16px">
      <template #header><span>📖 指标说明</span></template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="mAP@0.5">
          IoU阈值=0.5时的平均精度，越高说明检测框与真实框重叠越好，松材线虫定位越准确
        </el-descriptions-item>
        <el-descriptions-item label="mAP@0.5:0.95">
          COCO标准的严格版mAP，对定位精度要求更高
        </el-descriptions-item>
        <el-descriptions-item label="Precision（精确率）">
          检测结果中真实松材线虫的比例，越高误检越少
        </el-descriptions-item>
        <el-descriptions-item label="Recall（召回率）">
          真实松材线虫中被成功检测到的比例，越高漏检越少
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const radarRef = ref()
const modelResults = ref([
  { model: 'yolov5s',  mAP50: 0.823, mAP50_95: 0.512, precision: 0.861, recall: 0.798, status: 'ok' },
  { model: 'yolov5m',  mAP50: 0.854, mAP50_95: 0.541, precision: 0.879, recall: 0.832, status: 'ok' },
  { model: 'yolov8n',  mAP50: 0.841, mAP50_95: 0.528, precision: 0.856, recall: 0.819, status: 'ok' },
  { model: 'yolov8s',  mAP50: 0.872, mAP50_95: 0.558, precision: 0.891, recall: 0.851, status: 'ok' },
  { model: 'yolov9t',  mAP50: 0.865, mAP50_95: 0.547, precision: 0.883, recall: 0.843, status: 'ok' },
  { model: 'yolov10n', mAP50: 0.879, mAP50_95: 0.563, precision: 0.898, recall: 0.857, status: 'ok' },
])

onMounted(() => {
  // 标记最优模型
  const best = modelResults.value.reduce((a, b) => a.mAP50 > b.mAP50 ? a : b)
  modelResults.value.forEach(r => r.isBest = r.model === best.model)
  initRadar()
})

function mapColor(v) {
  if (v >= 0.85) return '#67c23a'
  if (v >= 0.7)  return '#e6a23c'
  return '#f56c6c'
}

function initRadar() {
  const chart = echarts.init(radarRef.value)
  chart.setOption({
    title: { text: '模型综合性能雷达图', left: 'center' },
    tooltip: { trigger: 'item' },
    legend: { data: modelResults.value.map(r => r.model), bottom: 0 },
    radar: {
      indicator: [
        { name: 'mAP@0.5',      max: 1 },
        { name: 'mAP@0.5:0.95', max: 1 },
        { name: 'Precision',    max: 1 },
        { name: 'Recall',       max: 1 },
      ]
    },
    series: [{
      type: 'radar',
      data: modelResults.value.map(r => ({
        name: r.model,
        value: [r.mAP50, r.mAP50_95, r.precision, r.recall],
      })),
    }],
    color: ['#2e7d32','#43a047','#66bb6a','#81c784','#a5d6a7','#c8e6c9'],
  })
}

function exportReport() {
  // 生成简单CSV
  const header = 'Model,mAP50,mAP50_95,Precision,Recall\n'
  const rows = modelResults.value.map(r =>
    `${r.model},${r.mAP50},${r.mAP50_95},${r.precision},${r.recall}`
  ).join('\n')
  const blob = new Blob([header + rows], { type: 'text/csv' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'evaluation_report.csv'
  a.click()
  ElMessage.success('报告已导出')
}
</script>
