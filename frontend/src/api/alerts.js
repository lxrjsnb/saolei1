import request from '@/utils/request'

// 获取报警规则列表
export function getAlertRules() {
  return request({
    url: '/alerts/rules/',
    method: 'get'
  })
}

// 创建报警规则
export function createAlertRule(data) {
  return request({
    url: '/alerts/rules/',
    method: 'post',
    data
  })
}

// 更新报警规则
export function updateAlertRule(id, data) {
  return request({
    url: `/alerts/rules/${id}/`,
    method: 'patch',
    data
  })
}

// 删除报警规则
export function deleteAlertRule(id) {
  return request({
    url: `/alerts/rules/${id}/`,
    method: 'delete'
  })
}

// 切换报警规则状态
export function toggleAlertRule(id) {
  return request({
    url: `/alerts/rules/${id}/toggle/`,
    method: 'post'
  })
}

// 获取报警记录
export function getAlertRecords(params) {
  return request({
    url: '/alerts/records/',
    method: 'get',
    params
  })
}

// 确认报警
export function acknowledgeAlert(id, notes = '') {
  return request({
    url: `/alerts/records/${id}/acknowledge/`,
    method: 'post',
    data: { notes }
  })
}

// 解决报警
export function resolveAlert(id, notes = '') {
  return request({
    url: `/alerts/records/${id}/resolve/`,
    method: 'post',
    data: { notes }
  })
}

// 获取报警统计
export function getAlertStatistics(range = '7d') {
  return request({
    url: '/alerts/statistics/',
    method: 'get',
    params: { range }
  })
}

// 获取待处理报警
export function getPendingAlerts() {
  return request({
    url: '/alerts/records/pending/',
    method: 'get'
  })
}
