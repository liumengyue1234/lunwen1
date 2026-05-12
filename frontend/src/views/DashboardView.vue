<template>
  <div class="dashboard">
    <div class="page-title">🌿 系统概览</div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" :style="{ background: stat.bg }">
              <el-icon :size="28" :color="stat.color"><component :is="stat.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-num">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header>
            <span>📈 检测趋势（近7天）</span>
          </template>
          <div ref="trendChartRef" style="height:280px"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header>
            <span>🤖 模型使用分布</span>
          </template>
          <div ref="modelChartRef" style="height:280px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作 -->
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header><span>⚡ 快速操作</span></template>
          <div class="quick-actions">
            <el-button type="primary" size="large" @click="$router.push('/detect')">
              <el-icon><Search /></el-icon> 开始检测
            </el-button>
            <el-button size="large" @click="$router.push('/history')">
              <el-icon><List /></el-icon> 查看历史
            </el-button>
            <el-button size="large" @click="$router.push('/report')">
              <el-icon><DataAnalysis /></el-icon> 评估报告
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/request'
import * as echarts from 'echarts'

const trendChartRef = ref()
const modelChartRef = ref()

const stats = ref([
  { label: '总检测次数', value: '—', icon: 'Search',       color: '#409eff', bg: '#ecf5ff' },
  { label: '检测到松材线虫', value: '—', icon: 'Warning',  color: '#f56c6c', bg: '#fef0f0' },
  { label: '今日检测',  value: '—', icon: 'Odometer',      color: '#67c23a', bg: '#f0f9eb' },
  { label: '可用模型',  value: '6',  icon: 'Setting',      color: '#e6a23c', bg: '#fdf6ec' },
])

onMounted(async () => {
  // 尝试加载历史统计
  try {
    const res = await api.get('/detection/history?page=1&size=1')
    const total = res.data.data.total || 0
    stats.value[0].value = total
    stats.value[2].value = '—'
  } catch {}

  initTrendChart()
  initModelChart()
})

function initTrendChart() {
  const chart = echarts.init(trendChartRef.value)
  const days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() - (6 - i))
    return `${d.getMonth() + 1}/${d.getDate()}`
  })
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: days },
    yAxis: { type: 'value', name: '检测次数' },
    series: [{
      name: '检测次数',
      type: 'line',
      smooth: true,
      data: [2, 5, 3, 8, 4, 7, 6],
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [{ offset: 0, color: 'rgba(46,125,50,0.4)' },
                     { offset: 1, color: 'rgba(46,125,50,0.05)' }] } },
      itemStyle: { color: '#2e7d32' },
      lineStyle:  { color: '#2e7d32', width: 2 },
    }],
    grid: { left: 40, right: 20, top: 30, bottom: 30 }
  })
}

function initModelChart() {
  const chart = echarts.init(modelChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 10, left: 'center' },
    series: [{
      type: 'pie',
      radius: ['40%', '65%'],
      data: [
        { value: 35, name: 'YOLOv8s' },
        { value: 25, name: 'YOLOv8n' },
        { value: 18, name: 'YOLOv5s' },
        { value: 12, name: 'YOLOv9t' },
        { value: 6,  name: 'YOLOv10n' },
        { value: 4,  name: 'YOLOv5m' },
      ],
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.2)' } },
      color: ['#2e7d32','#43a047','#66bb6a','#81c784','#a5d6a7','#c8e6c9'],
      label: { show: false }
    }],
  })
}
</script>

<style scoped>
.stat-row .stat-card { border-radius: 8px; }
.stat-content { display: flex; align-items: center; gap: 16px; }
.stat-icon { width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.stat-num { font-size: 28px; font-weight: 700; color: #1a1a1a; }
.stat-label { font-size: 13px; color: #888; margin-top: 4px; }
.quick-actions { display: flex; gap: 12px; flex-wrap: wrap; }
</style>
