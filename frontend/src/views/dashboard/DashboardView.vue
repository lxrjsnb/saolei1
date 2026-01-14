<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card stat-primary">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="40"><Cpu /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalDevices }}</div>
              <div class="stat-label">设备总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card stat-success">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="40"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.onlineDevices }}</div>
              <div class="stat-label">在线设备</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card stat-warning">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="40"><Bell /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pendingAlerts }}</div>
              <div class="stat-label">待处理报警</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card stat-info">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="40"><DataLine /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.todayDataPoints }}</div>
              <div class="stat-label">今日数据点</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>温度趋势</span>
          </template>
          <div ref="tempChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>湿度趋势</span>
          </template>
          <div ref="humidityChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最新数据表格 -->
    <el-row class="data-row">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>最新传感器数据</span>
          </template>
          <el-table :data="latestData" stripe v-loading="loading">
            <el-table-column prop="device_name" label="设备名称" />
            <el-table-column label="温度">
              <template #default="{ row }">
                {{ formatValue(row.temperature, '℃') }}
              </template>
            </el-table-column>
            <el-table-column label="湿度">
              <template #default="{ row }">
                {{ formatValue(row.humidity, '%') }}
              </template>
            </el-table-column>
            <el-table-column label="PM2.5">
              <template #default="{ row }">
                {{ formatValue(row.pm25, 'μg/m³') }}
              </template>
            </el-table-column>
            <el-table-column label="CO2">
              <template #default="{ row }">
                {{ formatValue(row.co2, 'ppm') }}
              </template>
            </el-table-column>
            <el-table-column prop="timestamp" label="采集时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.timestamp) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { getDevices } from '@/api/devices'
import { getLatestData } from '@/api/monitoring'
import { getAlertStatistics } from '@/api/alerts'

const loading = ref(false)
const latestData = ref([])
const tempChartRef = ref(null)
const humidityChartRef = ref(null)

let tempChart = null
let humidityChart = null
let refreshTimer = null

const stats = reactive({
  totalDevices: 0,
  onlineDevices: 0,
  pendingAlerts: 0,
  todayDataPoints: 0
})

const formatValue = (value, unit = '') => {
  if (value === null || value === undefined) return '-'
  return `${value.toFixed(1)} ${unit}`
}

const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const loadStats = async () => {
  try {
    // 加载设备统计
    const devicesResponse = await getDevices()
    const devices = devicesResponse.results || devicesResponse
    stats.totalDevices = devices.length
    stats.onlineDevices = devices.filter(d => d.status === 'online').length

    // 加载报警统计
    const alertStats = await getAlertStatistics('24h')
    stats.pendingAlerts = alertStats.total_stats?.pending || 0

    // 加载最新数据
    const data = await getLatestData()
    latestData.value = data
    stats.todayDataPoints = data.length

    // 更新图表
    updateCharts(data)
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error(error?.response?.data?.error || error?.message || '加载数据失败')
  }
}

const updateCharts = (data) => {
  if (!data || data.length === 0) return

  const labels = data.map(item => {
    const date = new Date(item.timestamp)
    return date.toLocaleTimeString('zh-CN')
  })

  const tempData = data.map(item => item.temperature)
  const humidityData = data.map(item => item.humidity)

  // 温度图表
  if (tempChart) {
    tempChart.setOption({
      xAxis: { data: labels },
      series: [{ data: tempData }]
    })
  } else if (tempChartRef.value) {
    tempChart = echarts.init(tempChartRef.value)
    tempChart.setOption({
      title: { text: '' },
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: labels,
        axisLabel: { rotate: 45 }
      },
      yAxis: { type: 'value' },
      series: [{
        name: '温度',
        type: 'line',
        data: tempData,
        smooth: true,
        itemStyle: { color: '#409EFF' }
      }]
    })
  }

  // 湿度图表
  if (humidityChart) {
    humidityChart.setOption({
      xAxis: { data: labels },
      series: [{ data: humidityData }]
    })
  } else if (humidityChartRef.value) {
    humidityChart = echarts.init(humidityChartRef.value)
    humidityChart.setOption({
      title: { text: '' },
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: labels,
        axisLabel: { rotate: 45 }
      },
      yAxis: {
        type: 'value',
        max: 100
      },
      series: [{
        name: '湿度',
        type: 'line',
        data: humidityData,
        smooth: true,
        itemStyle: { color: '#67C23A' }
      }]
    })
  }
}

onMounted(() => {
  loadStats()
  refreshTimer = setInterval(loadStats, 30000) // 每30秒刷新一次
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  if (tempChart) {
    tempChart.dispose()
  }
  if (humidityChart) {
    humidityChart.dispose()
  }
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.stat-card:hover {
  transform: translateY(-3px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.stat-primary .stat-icon {
  background-color: rgba(37, 99, 235, 0.1);
  color: var(--app-primary);
}

.stat-success .stat-icon {
  background-color: rgba(34, 197, 94, 0.12);
  color: #16a34a;
}

.stat-warning .stat-icon {
  background-color: rgba(245, 158, 11, 0.14);
  color: #b45309;
}

.stat-info .stat-icon {
  background-color: rgba(148, 163, 184, 0.16);
  color: rgba(15, 23, 42, 0.55);
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  color: var(--app-muted);
  font-size: 14px;
}

.charts-row {
  margin-bottom: 20px;
}

.data-row {
  margin-bottom: 20px;
}
</style>
