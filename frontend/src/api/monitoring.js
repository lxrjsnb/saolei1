import request from '@/utils/request'

// 获取所有设备最新数据
export function getLatestData() {
  return request({
    url: '/monitoring/data/latest/',
    method: 'get'
  })
}

// 上报传感器数据
export function uploadData(data) {
  return request({
    url: '/monitoring/upload/',
    method: 'post',
    data
  })
}

// 查询历史数据
export function queryData(params) {
  return request({
    url: '/monitoring/query/',
    method: 'get',
    params
  })
}

// 获取实时数据
export function getRealtimeData(deviceId) {
  return request({
    url: `/monitoring/realtime/${deviceId}/`,
    method: 'get'
  })
}

// 获取统计数据
export function getStatistics(deviceId, range = '24h') {
  return request({
    url: `/monitoring/statistics/${deviceId}/`,
    method: 'get',
    params: { range }
  })
}

// 导出数据
export function exportData(params) {
  const url = `/api/monitoring/export/?${new URLSearchParams(params)}`
  window.open(url, '_blank')
}
