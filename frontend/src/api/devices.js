import request from '@/utils/request'

// 获取设备列表
export function getDevices() {
  return request({
    url: '/devices/devices/',
    method: 'get'
  })
}

// 获取设备详情
export function getDevice(id) {
  return request({
    url: `/devices/devices/${id}/`,
    method: 'get'
  })
}

// 创建设备
export function createDevice(data) {
  return request({
    url: '/devices/devices/',
    method: 'post',
    data
  })
}

// 更新设备
export function updateDevice(id, data) {
  return request({
    url: `/devices/devices/${id}/`,
    method: 'patch',
    data
  })
}

// 删除设备
export function deleteDevice(id) {
  return request({
    url: `/devices/devices/${id}/`,
    method: 'delete'
  })
}

// 获取设备最新数据
export function getDeviceLatestData(id) {
  return request({
    url: `/devices/devices/${id}/latest_data/`,
    method: 'get'
  })
}

// 更新设备状态
export function updateDeviceStatus(id, status) {
  return request({
    url: `/devices/devices/${id}/toggle-status/`,
    method: 'post',
    data: { status }
  })
}

// 更新设备配置
export function updateDeviceConfig(id, data) {
  return request({
    url: `/devices/devices/${id}/update_config/`,
    method: 'post',
    data
  })
}
