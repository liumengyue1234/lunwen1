<template>
  <div class="login-page">
    <div class="login-container">
      <!-- 左侧宣传区 -->
      <div class="login-banner">
        <div class="banner-content">
          <div class="logo">🌲</div>
          <h1>松材线虫病CT图像检测系统</h1>
          <p>基于深度学习的林业病害智能诊断平台</p>
          <div class="features">
            <div class="feature-item">
              <span class="icon">🔬</span>
              <span>多模型检测（YOLOv5/v8/v9/v10）</span>
            </div>
            <div class="feature-item">
              <span class="icon">📊</span>
              <span>可视化病变区域标注</span>
            </div>
            <div class="feature-item">
              <span class="icon">📋</span>
              <span>智能病害分析报告生成</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="login-form-area">
        <div class="form-header">
          <h2>用户登录</h2>
          <p>请输入账号和密码</p>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          @submit.prevent="handleLogin"
          class="login-form"
        >
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="用户名"
              size="large"
              prefix-icon="User"
              clearable
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码"
              size="large"
              prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-button
            type="primary"
            size="large"
            style="width: 100%; margin-top: 8px"
            :loading="loading"
            @click="handleLogin"
          >
            登 录
          </el-button>

          <div class="tips">
            <p>演示账号：<code>admin</code> / <code>admin123</code></p>
            <p>普通用户：<code>liuxinyue</code> / <code>user123</code></p>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref()
const loading = ref(false)

const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    await authStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch (e) {
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 50%, #a5d6a7 100%);
}

.login-container {
  display: flex;
  width: 900px;
  min-height: 520px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.login-banner {
  flex: 1;
  background: linear-gradient(135deg, #2e7d32, #388e3c);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.banner-content {
  text-align: center;
}

.logo { font-size: 60px; margin-bottom: 16px; }

.login-banner h1 {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 12px;
}

.login-banner p {
  font-size: 14px;
  opacity: 0.85;
  margin-bottom: 32px;
}

.features { text-align: left; }

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 12px 0;
  font-size: 14px;
  opacity: 0.9;
}

.feature-item .icon { font-size: 20px; }

.login-form-area {
  width: 380px;
  background: white;
  padding: 50px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.form-header { margin-bottom: 32px; }
.form-header h2 { font-size: 24px; color: #1a1a1a; margin-bottom: 6px; }
.form-header p  { font-size: 14px; color: #666; }

.tips {
  margin-top: 20px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 6px;
  font-size: 12px;
  color: #666;
  line-height: 1.8;
}

.tips code {
  background: #e8f5e9;
  color: #2e7d32;
  padding: 1px 4px;
  border-radius: 3px;
}
</style>
