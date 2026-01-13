import request from '@/utils/request'

// 用户注册
export function register(username, password, email) {
  return request({
    url: '/auth/register/',
    method: 'post',
    data: { username, password, email }
  })
}

// 用户登录
export function login(username, password) {
  return request({
    url: '/auth/login/',
    method: 'post',
    data: { username, password }
  })
}

// 用户登出
export function logout() {
  return request({
    url: '/auth/logout/',
    method: 'post'
  })
}

// 获取用户信息
export function getUserInfo() {
  return request({
    url: '/auth/profile/',
    method: 'get'
  })
}
