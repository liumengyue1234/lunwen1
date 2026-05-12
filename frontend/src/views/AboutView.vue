<template>
  <div>
    <div class="page-title">ℹ️ 关于系统</div>
    <el-card shadow="hover">
      <el-descriptions title="系统信息" :column="2" border>
        <el-descriptions-item label="项目名称">基于CT图像的松材线虫病检测系统</el-descriptions-item>
        <el-descriptions-item label="版本">v1.0.0</el-descriptions-item>
        <el-descriptions-item label="学生">刘昕月（2022222997）</el-descriptions-item>
        <el-descriptions-item label="专业">软件工程 2022级4班</el-descriptions-item>
        <el-descriptions-item label="指导教师">邱兆文 教授</el-descriptions-item>
        <el-descriptions-item label="企业导师">高启 工程师</el-descriptions-item>
        <el-descriptions-item label="学院">计算机与控制工程学院 — 东北林业大学</el-descriptions-item>
        <el-descriptions-item label="完成时间">2026年5月</el-descriptions-item>
      </el-descriptions>

      <el-divider>技术栈</el-divider>
      <el-row :gutter="16">
        <el-col :span="8" v-for="tech in techStack" :key="tech.name">
          <el-card class="tech-card" shadow="hover">
            <div class="tech-icon">{{ tech.icon }}</div>
            <div class="tech-name">{{ tech.name }}</div>
            <div class="tech-desc">{{ tech.desc }}</div>
          </el-card>
        </el-col>
      </el-row>

      <el-divider>检测模型</el-divider>
      <el-row :gutter="12">
        <el-col :span="4" v-for="m in modelList" :key="m">
          <el-tag size="large" type="success" style="width:100%;text-align:center;padding:10px">{{ m }}</el-tag>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
const techStack = [
  { icon: '⚡', name: 'Vue 3 + Vite',      desc: '前端框架，Composition API' },
  { icon: '🍃', name: 'Spring Boot 3',      desc: '后端框架，RESTful API' },
  { icon: '🔥', name: 'PyTorch + YOLO',    desc: '深度学习推理引擎' },
  { icon: '🗄️', name: 'H2 / MySQL',        desc: '数据库存储' },
  { icon: '🔐', name: 'JWT + Spring Security', desc: '认证授权' },
  { icon: '📊', name: 'ECharts',            desc: '数据可视化' },
]
const modelList = ['YOLOv5s', 'YOLOv5m', 'YOLOv8n', 'YOLOv8s', 'YOLOv9t', 'YOLOv10n']
</script>

<style scoped>
.tech-card { text-align: center; padding: 8px; }
.tech-icon { font-size: 32px; margin-bottom: 8px; }
.tech-name { font-weight: 600; color: #1a1a1a; }
.tech-desc { font-size: 12px; color: #888; margin-top: 4px; }
</style>
