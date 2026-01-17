import request from '@/utils/request'

export function getRobotGroups() {
  return request({
    url: '/robots/groups/',
    method: 'get'
  })
}

export function getRobotsDashboard() {
  return request({
    url: '/robots/dashboard/',
    method: 'get'
  })
}

export function getRobotComponents(params) {
  return request({
    url: '/robots/components/',
    method: 'get',
    params
  })
}

export function getRobotComponent(id) {
  return request({
    url: `/robots/components/${id}/`,
    method: 'get'
  })
}

export function updateRobotComponent(id, data) {
  return request({
    url: `/robots/components/${id}/`,
    method: 'patch',
    data
  })
}

export function getRiskEvents(params) {
  return request({
    url: '/robots/risk-events/',
    method: 'get',
    params
  })
}

export function acknowledgeRiskEvent(id, notes = '') {
  return request({
    url: `/robots/risk-events/${id}/acknowledge/`,
    method: 'post',
    data: { notes }
  })
}

export function resolveRiskEvent(id, notes = '') {
  return request({
    url: `/robots/risk-events/${id}/resolve/`,
    method: 'post',
    data: { notes }
  })
}

export function getRiskEventStatistics(params) {
  return request({
    url: '/robots/risk-events/statistics/',
    method: 'get',
    params
  })
}
