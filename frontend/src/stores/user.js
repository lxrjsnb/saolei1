import { defineStore } from 'pinia'
import { login, logout, getUserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: null,
    username: localStorage.getItem('username') || ''
  }),

  getters: {
    isAuthenticated: (state) => !!state.token
  },

  actions: {
    setToken(token) {
      this.token = token
      localStorage.setItem('token', token)
    },

    setUsername(username) {
      this.username = username
      localStorage.setItem('username', username)
    },

    setUserInfo(userInfo) {
      this.userInfo = userInfo
    },

    async login(username, password) {
      try {
        const data = await login(username, password)
        this.setToken(data.token)
        this.setUsername(data.username)
        return data
      } catch (error) {
        throw error
      }
    },

    async logout() {
      try {
        await logout()
      } catch (error) {
        console.error('退出登录失败:', error)
      } finally {
        this.token = ''
        this.userInfo = null
        this.username = ''
        localStorage.removeItem('token')
        localStorage.removeItem('username')
      }
    },

    async fetchUserInfo() {
      try {
        const data = await getUserInfo()
        this.setUserInfo(data)
        return data
      } catch (error) {
        throw error
      }
    }
  }
})
