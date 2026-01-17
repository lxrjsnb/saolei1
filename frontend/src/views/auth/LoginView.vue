<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <el-icon class="login-logo" :size="52"><Cpu /></el-icon>
        <h1>机器人技术管理平台</h1>
        <p class="subtitle">状态可视化 · 风险闭环 · 轻量演示</p>
      </div>

      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" class="login-form">
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            size="large"
            :prefix-icon="Lock"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            style="width: 100%"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Cpu } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  const valid = await loginFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.login(loginForm.username, loginForm.password)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch (error) {
    ElMessage.error(error.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(1100px 600px at 20% 10%, rgba(37, 99, 235, 0.14), transparent 55%),
    radial-gradient(900px 520px at 85% 25%, rgba(14, 165, 233, 0.12), transparent 60%),
    linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-box {
  width: min(420px, calc(100vw - 32px));
  padding: 34px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: var(--app-radius);
  box-shadow: var(--app-shadow);
  backdrop-filter: blur(12px);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-logo {
  color: var(--app-primary);
}

.login-header h1 {
  font-size: 20px;
  letter-spacing: 0.2px;
  color: var(--app-text);
  margin-top: 14px;
  font-weight: 700;
}

.subtitle {
  margin-top: 8px;
  margin-bottom: 0;
  color: var(--app-muted);
  font-size: 13px;
}

.login-form {
  margin-top: 30px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 12px;
}

.login-form :deep(.el-button) {
  height: 44px;
  border-radius: 12px;
  font-weight: 600;
}
</style>
