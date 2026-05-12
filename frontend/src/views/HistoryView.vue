<template>
  <div>
    <div class="page-title">📋 历史检测记录</div>
    <el-card shadow="hover">
      <el-table :data="records" stripe v-loading="loading">
        <el-table-column prop="id" label="任务ID" width="80" />
        <el-table-column prop="imageName" label="图像名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="modelName" label="模型" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.modelName }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detectCount" label="检测数量" width="100">
          <template #default="{ row }">
            <el-tag :type="row.detectCount > 0 ? 'danger' : 'success'" size="small">
              {{ row.detectCount }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'DONE' ? 'success' : row.status === 'FAILED' ? 'danger' : 'warning'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="检测时间" width="170">
          <template #default="{ row }">
            {{ row.createTime?.replace('T', ' ')?.slice(0, 19) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="size"
        :total="total"
        layout="total, prev, pager, next"
        style="margin-top:16px;justify-content:flex-end;display:flex"
        @current-change="loadData"
      />
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="检测详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="任务ID">{{ detail.task?.id }}</el-descriptions-item>
        <el-descriptions-item label="模型">{{ detail.task?.modelName }}</el-descriptions-item>
        <el-descriptions-item label="图像">{{ detail.task?.imageName }}</el-descriptions-item>
        <el-descriptions-item label="检测数量">{{ detail.task?.detectCount }}</el-descriptions-item>
      </el-descriptions>
      <el-table :data="detail.results" stripe size="small" style="margin-top:16px">
        <el-table-column prop="label" label="标签" />
        <el-table-column prop="confidence" label="置信度">
          <template #default="{ row }">{{ (row.confidence * 100).toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column label="坐标">
          <template #default="{ row }">
            ({{ Math.round(row.x1) }},{{ Math.round(row.y1) }}) → ({{ Math.round(row.x2) }},{{ Math.round(row.y2) }})
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/request'

const records = ref([])
const loading = ref(false)
const page = ref(1)
const size = ref(10)
const total = ref(0)
const detailVisible = ref(false)
const detail = ref({ task: null, results: [] })

onMounted(loadData)

async function loadData() {
  loading.value = true
  try {
    const res = await api.get(`/detection/history?page=${page.value}&size=${size.value}`)
    const d = res.data.data
    records.value = d.records || []
    total.value   = Number(d.total) || 0
  } catch {}
  loading.value = false
}

async function viewDetail(row) {
  try {
    const res = await api.get(`/detection/task/${row.id}`)
    detail.value = res.data.data
    detailVisible.value = true
  } catch {}
}
</script>
