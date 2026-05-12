import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/request'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))

  const isLoggedIn = computed(() => !!token.value)

  async function login(username, password) {
    const res = await api.post('/auth/login', { username, password })
    token.value = res.data.data.token
    userInfo.value = {
      username: res.data.data.username,
      realName: res.data.data.realName,
      role: res.data.data.role
    }
    localStorage.setItem('token', token.value)
    localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    return res.data
  }

  function logout() {
    token.value = ''
    userInfo.value = {}
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  return { token, userInfo, isLoggedIn, login, logout }
})
