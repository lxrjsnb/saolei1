<template>
  <div class="bigscreen">
    <!-- 顶部标题栏 -->
    <header class="bigscreen-header">
      <div class="header-left">
        <button type="button" class="exit-button" @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          退出
        </button>
        <h1 class="title">物联网环境监测数据大屏</h1>
      </div>
      <div class="header-center">
        <div class="datetime">
          <div class="time">{{ currentTime.time }}</div>
          <div class="date">{{ currentTime.date }}</div>
        </div>
      </div>
      <div class="header-right">
        <div class="weather-info">
          <span>系统运行正常</span>
          <el-icon class="status-icon"><SuccessFilled /></el-icon>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="bigscreen-main">
      <!-- 左侧区域 -->
      <section class="left-panel">
        <!-- 统计卡片 -->
        <div class="stats-container">
          <div class="stat-card stat-primary">
            <div class="stat-icon">
              <el-icon :size="32"><Cpu /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.totalDevices }}</div>
              <div class="stat-label">设备总数</div>
            </div>
          </div>
          <div class="stat-card stat-success">
            <div class="stat-icon">
              <el-icon :size="32"><CircleCheck /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.onlineDevices }}</div>
              <div class="stat-label">在线设备</div>
            </div>
          </div>
          <div class="stat-card stat-warning">
            <div class="stat-icon">
              <el-icon :size="32"><Bell /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.pendingAlerts }}</div>
              <div class="stat-label">待处理报警</div>
            </div>
          </div>
          <div class="stat-card stat-info">
            <div class="stat-icon">
              <el-icon :size="32"><DataLine /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.todayDataPoints }}</div>
              <div class="stat-label">今日数据点</div>
            </div>
          </div>
        </div>

        <!-- 温度趋势图 -->
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">温度实时趋势</span>
            <span class="chart-unit">单位: ℃</span>
          </div>
          <div ref="tempChartRef" class="chart-container"></div>
        </div>

        <!-- 湿度趋势图 -->
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">湿度实时趋势</span>
            <span class="chart-unit">单位: %</span>
          </div>
          <div ref="humidityChartRef" class="chart-container"></div>
        </div>
      </section>

      <!-- 中间区域 -->
      <section class="center-panel">
        <!-- PM2.5 趋势图 -->
        <div class="chart-card chart-large">
          <div class="chart-header">
            <span class="chart-title">PM2.5 实时监测</span>
            <span class="chart-unit">单位: μg/m³</span>
          </div>
          <div ref="pm25ChartRef" class="chart-container chart-large-container"></div>
        </div>

        <!-- CO2 趋势图 -->
        <div class="chart-card chart-large">
          <div class="chart-header">
            <span class="chart-title">CO2 实时监测</span>
            <span class="chart-unit">单位: ppm</span>
          </div>
          <div ref="co2ChartRef" class="chart-container chart-large-container"></div>
        </div>

        <!-- 实时数据滚动表格 -->
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">实时数据监测</span>
            <span class="live-indicator">
              <span class="live-dot"></span>
              实时更新
            </span>
          </div>
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>设备名称</th>
                  <th>温度(℃)</th>
                  <th>湿度(%)</th>
                  <th>PM2.5</th>
                  <th>CO2</th>
                  <th>状态</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in realtimeData" :key="item.id">
                  <td>{{ item.device_name }}</td>
                  <td :class="getValueClass(item.temperature, 'temp')">{{ formatValue(item.temperature) }}</td>
                  <td :class="getValueClass(item.humidity, 'humidity')">{{ formatValue(item.humidity) }}</td>
                  <td :class="getValueClass(item.pm25, 'pm25')">{{ formatValue(item.pm25) }}</td>
                  <td :class="getValueClass(item.co2, 'co2')">{{ formatValue(item.co2) }}</td>
                  <td>
                    <span class="status-badge" :class="item.status === 'online' ? 'status-online' : 'status-offline'">
                      {{ item.status === 'online' ? '在线' : '离线' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- 右侧区域 -->
      <section class="right-panel">
        <!-- 环境质量评估 -->
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">环境质量综合评估</span>
          </div>
          <div ref="qualityGaugeRef" class="chart-container"></div>
        </div>

        <!-- 各设备平均数据 -->
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">设备平均数据对比</span>
          </div>
          <div ref="deviceBarChartRef" class="chart-container"></div>
        </div>

        <!-- 最新报警列表 -->
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">最新报警</span>
          </div>
          <div class="alert-list">
            <div v-for="alert in recentAlerts" :key="alert.id" class="alert-item" :class="'alert-' + alert.level">
              <div class="alert-icon">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="alert-content">
                <div class="alert-title">{{ alert.message }}</div>
                <div class="alert-time">{{ formatDateTime(alert.triggered_at) }}</div>
              </div>
            </div>
            <div v-if="recentAlerts.length === 0" class="no-alerts">
              <el-icon><CircleCheck /></el-icon>
              <span>暂无报警信息</span>
            </div>
          </div>
        </div>

        <!-- 数据分布图 -->
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">参数分布统计</span>
          </div>
          <div ref="pieChartRef" class="chart-container"></div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  SuccessFilled, Cpu, CircleCheck, Bell, DataLine,
  Warning, ArrowLeft
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getDevices } from '@/api/devices'
import { getLatestData } from '@/api/monitoring'
import { getAlertStatistics } from '@/api/alerts'

const router = useRouter()

// 当前时间
const currentTime = reactive({
  time: '',
  date: ''
})

// 统计数据
const stats = reactive({
  totalDevices: 0,
  onlineDevices: 0,
  pendingAlerts: 0,
  todayDataPoints: 0
})

// 实时数据
const realtimeData = ref([])

// 最新报警
const recentAlerts = ref([])

// 图表引用
const tempChartRef = ref(null)
const humidityChartRef = ref(null)
const pm25ChartRef = ref(null)
const co2ChartRef = ref(null)
const qualityGaugeRef = ref(null)
const deviceBarChartRef = ref(null)
const pieChartRef = ref(null)

// 图表实例
let tempChart = null
let humidityChart = null
let pm25Chart = null
let co2Chart = null
let qualityGauge = null
let deviceBarChart = null
let pieChart = null

// 定时器
let timeTimer = null
let dataTimer = null

// 格式化数值
const formatValue = (value) => {
  if (value === null || value === undefined) return '-'
  return value.toFixed(1)
}

// 格式化日期时间
const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 获取数值样式类
const getValueClass = (value, type) => {
  if (value === null || value === undefined) return ''

  const thresholds = {
    temp: { min: 18, max: 28 },
    humidity: { min: 30, max: 70 },
    pm25: { good: 35, moderate: 75 },
    co2: { good: 800, moderate: 1200 }
  }

  if (type === 'temp') {
    if (value < thresholds.temp.min || value > thresholds.temp.max) return 'value-warning'
  } else if (type === 'humidity') {
    if (value < thresholds.humidity.min || value > thresholds.humidity.max) return 'value-warning'
  } else if (type === 'pm25') {
    if (value > thresholds.pm25.moderate) return 'value-danger'
    if (value > thresholds.pm25.good) return 'value-warning'
  } else if (type === 'co2') {
    if (value > thresholds.co2.moderate) return 'value-danger'
    if (value > thresholds.co2.good) return 'value-warning'
  }

  return 'value-normal'
}

// 更新时间
const updateTime = () => {
  const now = new Date()
  currentTime.time = now.toLocaleTimeString('zh-CN')
  currentTime.date = now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    weekday: 'long'
  })
}

// 加载所有数据
const loadAllData = async () => {
  try {
    // 加载设备统计
    const devicesResponse = await getDevices()
    const devices = devicesResponse.results || devicesResponse
    stats.totalDevices = devices.length
    stats.onlineDevices = devices.filter(d => d.status === 'online').length

    // 加载报警统计
    const alertStats = await getAlertStatistics('24h')
    stats.pendingAlerts = alertStats.total_stats?.pending || 0
    recentAlerts.value = alertStats.recent_alerts?.slice(0, 5) || []

    // 加载最新数据
    const data = await getLatestData()
    realtimeData.value = data.slice(0, 10)
    stats.todayDataPoints = data.length

    // 更新所有图表
    updateAllCharts(data, devices)
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

// 更新所有图表
const updateAllCharts = (data, devices) => {
  if (!data || data.length === 0) return

  // 按设备分组数据
  const deviceGroups = {}
  data.forEach(item => {
    if (!deviceGroups[item.device_name]) {
      deviceGroups[item.device_name] = []
    }
    deviceGroups[item.device_name].push(item)
  })

  const labels = data.slice(0, 20).map(item => {
    const date = new Date(item.timestamp)
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }).reverse()

  const tempData = data.slice(0, 20).map(item => item.temperature).reverse()
  const humidityData = data.slice(0, 20).map(item => item.humidity).reverse()
  const pm25Data = data.slice(0, 20).map(item => item.pm25).reverse()
  const co2Data = data.slice(0, 20).map(item => item.co2).reverse()

  // 更新温度图表
  updateLineChart(tempChart, tempChartRef.value, labels, tempData, '温度', '#00d4ff', '℃')

  // 更新湿度图表
  updateLineChart(humidityChart, humidityChartRef.value, labels, humidityData, '湿度', '#00ff88', '%')

  // 更新 PM2.5 图表
  updateAreaChart(pm25Chart, pm25ChartRef.value, labels, pm25Data, 'PM2.5', '#ffa600')

  // 更新 CO2 图表
  updateAreaChart(co2Chart, co2ChartRef.value, labels, co2Data, 'CO2', '#ff6b6b')

  // 更新环境质量仪表盘
  updateQualityGauge(data)

  // 更新设备对比柱状图
  updateDeviceBarChart(deviceGroups)

  // 更新分布饼图
  updatePieChart(data)
}

// 更新折线图
const updateLineChart = (chart, chartRef, labels, data, name, color, unit) => {
  const option = {
    grid: { top: 30, right: 20, bottom: 30, left: 40 },
    tooltip: {
      trigger: 'axis',
      formatter: `{b}<br/>{a}: {c}${unit}`
    },
    xAxis: {
      type: 'category',
      data: labels,
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#1e293b' } }
    },
    series: [{
      name,
      type: 'line',
      data,
      smooth: true,
      lineStyle: { color, width: 2 },
      itemStyle: { color },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: color + '40' },
            { offset: 1, color: color + '05' }
          ]
        }
      }
    }]
  }

  if (chart) {
    chart.setOption(option)
  } else if (chartRef) {
    chart = echarts.init(chartRef)
    if (chart === tempChart) tempChart = chart
    else if (chart === humidityChart) humidityChart = chart
    chart.setOption(option)
  }
}

// 更新面积图
const updateAreaChart = (chart, chartRef, labels, data, name, color) => {
  const option = {
    grid: { top: 30, right: 20, bottom: 30, left: 50 },
    tooltip: {
      trigger: 'axis',
      formatter: `{b}<br/>{a}: {c}`
    },
    xAxis: {
      type: 'category',
      data: labels,
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#1e293b' } }
    },
    series: [{
      name,
      type: 'line',
      data,
      smooth: true,
      lineStyle: { color, width: 3 },
      itemStyle: { color },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: color + '60' },
            { offset: 1, color: color + '10' }
          ]
        }
      }
    }]
  }

  if (chart) {
    chart.setOption(option)
  } else if (chartRef) {
    chart = echarts.init(chartRef)
    if (chart === pm25Chart) pm25Chart = chart
    else if (chart === co2Chart) co2Chart = chart
    chart.setOption(option)
  }
}

// 更新环境质量仪表盘
const updateQualityGauge = (data) => {
  if (!data || data.length === 0) return

  // 计算平均质量分数
  let totalScore = 0
  let count = 0

  data.forEach(item => {
    let score = 100
    if (item.temperature < 18 || item.temperature > 28) score -= 20
    if (item.humidity < 30 || item.humidity > 70) score -= 20
    if (item.pm25 > 75) score -= 30
    if (item.pm25 > 35) score -= 15
    if (item.co2 > 1200) score -= 30
    if (item.co2 > 800) score -= 15
    totalScore += Math.max(0, score)
    count++
  })

  const avgScore = count > 0 ? Math.round(totalScore / count) : 100

  const option = {
    series: [{
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 100,
      splitNumber: 5,
      axisLine: {
        lineStyle: {
          width: 15,
          color: [
            [0.3, '#ff4d4f'],
            [0.6, '#ffa600'],
            [0.8, '#52c41a'],
            [1, '#00d4ff']
          ]
        }
      },
      pointer: {
        icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
        length: '12%',
        width: 20,
        offsetCenter: [0, '-60%'],
        itemStyle: { color: 'auto' }
      },
      axisTick: { length: 12, lineStyle: { color: 'auto', width: 2 } },
      splitLine: { length: 20, lineStyle: { color: 'auto', width: 5 } },
      axisLabel: {
        color: '#94a3b8',
        fontSize: 14,
        distance: -60,
        formatter: '{value}'
      },
      detail: {
        valueAnimation: true,
        formatter: '{value}',
        color: '#fff',
        fontSize: 40,
        offsetCenter: [0, '20%']
      },
      data: [{ value: avgScore }]
    }]
  }

  if (qualityGauge) {
    qualityGauge.setOption(option)
  } else if (qualityGaugeRef.value) {
    qualityGauge = echarts.init(qualityGaugeRef.value)
    qualityGauge.setOption(option)
  }
}

// 更新设备对比柱状图
const updateDeviceBarChart = (deviceGroups) => {
  const deviceNames = Object.keys(deviceGroups)
  if (deviceNames.length === 0) return

  const avgTemp = deviceNames.map(name => {
    const items = deviceGroups[name]
    const sum = items.reduce((acc, item) => acc + (item.temperature || 0), 0)
    return (sum / items.length).toFixed(1)
  })

  const option = {
    grid: { top: 20, right: 20, bottom: 40, left: 50 },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    xAxis: {
      type: 'category',
      data: deviceNames,
      axisLabel: {
        color: '#94a3b8',
        fontSize: 10,
        interval: 0,
        rotate: 30
      },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#1e293b' } }
    },
    series: [{
      name: '平均温度',
      type: 'bar',
      data: avgTemp,
      itemStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#00d4ff' },
            { offset: 1, color: '#0066ff' }
          ]
        }
      },
      barWidth: '60%'
    }]
  }

  if (deviceBarChart) {
    deviceBarChart.setOption(option)
  } else if (deviceBarChartRef.value) {
    deviceBarChart = echarts.init(deviceBarChartRef.value)
    deviceBarChart.setOption(option)
  }
}

// 更新分布饼图
const updatePieChart = (data) => {
  // 计算各参数的分布
  let goodCount = 0
  let warningCount = 0
  let dangerCount = 0

  data.forEach(item => {
    let hasWarning = false
    let hasDanger = false

    if (item.temperature < 18 || item.temperature > 28) hasWarning = true
    if (item.humidity < 30 || item.humidity > 70) hasWarning = true
    if (item.pm25 > 75) hasDanger = true
    else if (item.pm25 > 35) hasWarning = true
    if (item.co2 > 1200) hasDanger = true
    else if (item.co2 > 800) hasWarning = true

    if (hasDanger) dangerCount++
    else if (hasWarning) warningCount++
    else goodCount++
  })

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: { color: '#94a3b8' }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['35%', '50%'],
      data: [
        { value: goodCount, name: '正常', itemStyle: { color: '#52c41a' } },
        { value: warningCount, name: '预警', itemStyle: { color: '#ffa600' } },
        { value: dangerCount, name: '超标', itemStyle: { color: '#ff4d4f' } }
      ],
      label: {
        color: '#94a3b8',
        formatter: '{b}\n{c}'
      }
    }]
  }

  if (pieChart) {
    pieChart.setOption(option)
  } else if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
    pieChart.setOption(option)
  }
}

// 退出大屏：优先返回站内上一页（如果存在），否则回到仪表盘
const goBack = () => {
  const back = window.history?.state?.back
  if (typeof back === 'string' && back.startsWith('/') && !back.startsWith('/bigscreen')) {
    router.back()
    return
  }
  router.replace('/dashboard')
}

// 初始化图表
const initCharts = () => {
  if (tempChartRef.value) tempChart = echarts.init(tempChartRef.value)
  if (humidityChartRef.value) humidityChart = echarts.init(humidityChartRef.value)
  if (pm25ChartRef.value) pm25Chart = echarts.init(pm25ChartRef.value)
  if (co2ChartRef.value) co2Chart = echarts.init(co2ChartRef.value)
  if (qualityGaugeRef.value) qualityGauge = echarts.init(qualityGaugeRef.value)
  if (deviceBarChartRef.value) deviceBarChart = echarts.init(deviceBarChartRef.value)
  if (pieChartRef.value) pieChart = echarts.init(pieChartRef.value)
}

// 窗口大小改变时重新调整图表
const handleResize = () => {
  tempChart?.resize()
  humidityChart?.resize()
  pm25Chart?.resize()
  co2Chart?.resize()
  qualityGauge?.resize()
  deviceBarChart?.resize()
  pieChart?.resize()
}

onMounted(() => {
  updateTime()
  timeTimer = setInterval(updateTime, 1000)

  initCharts()
  loadAllData()
  dataTimer = setInterval(loadAllData, 30000) // 每30秒刷新数据

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (timeTimer) clearInterval(timeTimer)
  if (dataTimer) clearInterval(dataTimer)

  tempChart?.dispose()
  humidityChart?.dispose()
  pm25Chart?.dispose()
  co2Chart?.dispose()
  qualityGauge?.dispose()
  deviceBarChart?.dispose()
  pieChart?.dispose()

  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.bigscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #0c1222 0%, #1a1f3a 50%, #0c1222 100%);
  color: #fff;
  overflow-x: hidden;
  overflow-y: auto;
}

/* 顶部标题栏 */
.bigscreen-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  background: linear-gradient(180deg, rgba(0, 212, 255, 0.12) 0%, rgba(12, 18, 34, 0.6) 100%);
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
  backdrop-filter: blur(10px);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left .title {
  margin: 0;
  font-size: 28px;
  font-weight: bold;
  background: linear-gradient(90deg, #00d4ff, #00ff88);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-center .datetime {
  text-align: center;
}

.datetime .time {
  font-size: 36px;
  font-weight: bold;
  font-family: 'Courier New', monospace;
  color: #00d4ff;
}

.datetime .date {
  font-size: 14px;
  color: #94a3b8;
}

.weather-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #52c41a;
}

.status-icon {
  font-size: 18px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 主内容区 */
.bigscreen-main {
  display: grid;
  grid-template-columns: 1fr 1.5fr 1fr;
  gap: 15px;
  padding: 15px;
  min-height: calc(100vh - 80px);
  padding-bottom: 24px;
}

.left-panel,
.center-panel,
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 统计卡片容器 */
.stats-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 15px;
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-icon {
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
}

.stat-primary .stat-icon { background: rgba(0, 212, 255, 0.2); color: #00d4ff; }
.stat-success .stat-icon { background: rgba(82, 196, 26, 0.2); color: #52c41a; }
.stat-warning .stat-icon { background: rgba(255, 166, 0, 0.2); color: #ffa600; }
.stat-info .stat-icon { background: rgba(144, 160, 174, 0.2); color: #90a0ae; }

.stat-content .stat-value {
  font-size: 24px;
  font-weight: bold;
  line-height: 1;
}

.stat-content .stat-label {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

/* 图表卡片 */
.chart-card {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 15px;
  flex: none;
  min-height: 0;
  display: flex;
  flex-direction: column;
  height: clamp(220px, 28vh, 320px);
}

.chart-card.chart-large {
  height: clamp(260px, 34vh, 420px);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
}

.chart-unit {
  font-size: 11px;
  color: #64748b;
}

.chart-container {
  flex: 1;
  min-height: 0;
}

.chart-large-container {
  min-height: 200px;
}

.exit-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(0, 212, 255, 0.18);
  border: 1px solid rgba(0, 212, 255, 0.35);
  border-radius: 8px;
  color: #00d4ff;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
  line-height: 1;
}

.exit-button:hover {
  background: rgba(0, 212, 255, 0.26);
  transform: translateY(-1px);
}

.exit-button:active {
  transform: translateY(0);
}

.exit-button:focus-visible {
  outline: 2px solid rgba(0, 212, 255, 0.55);
  outline-offset: 2px;
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #52c41a;
}

.live-dot {
  width: 6px;
  height: 6px;
  background: #52c41a;
  border-radius: 50%;
  animation: blink 1.5s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

/* 数据表格 */
.table-container {
  flex: 1;
  overflow: auto;
  min-height: 0;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.data-table thead {
  position: sticky;
  top: 0;
  background: rgba(30, 41, 59, 0.95);
  z-index: 1;
}

.data-table th {
  padding: 10px 8px;
  text-align: left;
  font-weight: 600;
  color: #94a3b8;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.data-table td {
  padding: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.data-table tbody tr:hover {
  background: rgba(0, 212, 255, 0.05);
}

.value-normal { color: #52c41a; }
.value-warning { color: #ffa600; }
.value-danger { color: #ff4d4f; }

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
}

.status-online {
  background: rgba(82, 196, 26, 0.2);
  color: #52c41a;
}

.status-offline {
  background: rgba(144, 160, 174, 0.2);
  color: #90a0ae;
}

/* 报警列表 */
.alert-list {
  flex: 1;
  overflow-y: auto;
  max-height: 150px;
}

.alert-item {
  display: flex;
  gap: 10px;
  padding: 10px;
  margin-bottom: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  border-left: 3px solid;
}

.alert-info { border-color: #1890ff; }
.alert-low { border-color: #52c41a; }
.alert-medium { border-color: #ffa600; }
.alert-high { border-color: #ff4d4f; }
.alert-critical { border-color: #ff0033; }

.alert-icon {
  color: #ffa600;
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-title {
  font-size: 12px;
  color: #e2e8f0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.alert-time {
  font-size: 10px;
  color: #64748b;
  margin-top: 4px;
}

.no-alerts {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  color: #52c41a;
  font-size: 12px;
}

.no-alerts .el-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

/* 滚动条样式 */
.table-container::-webkit-scrollbar,
.alert-list::-webkit-scrollbar {
  width: 4px;
}

.table-container::-webkit-scrollbar-thumb,
.alert-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.table-container::-webkit-scrollbar-track,
.alert-list::-webkit-scrollbar-track {
  background: transparent;
}

/* 响应式 */
@media (max-width: 1600px) {
  .bigscreen-main {
    grid-template-columns: 1fr 1.2fr 1fr;
  }
}

@media (max-width: 1200px) {
  .bigscreen-main {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
    height: auto;
    overflow-y: auto;
  }

  .chart-large-container {
    min-height: 180px;
  }
}
</style>
