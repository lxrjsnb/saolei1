<template>
  <div class="monitoring">
    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="6">
          <el-select v-model="selectedDevice" placeholder="请选择设备" @change="loadData">
            <el-option
              v-for="device in devices"
              :key="device.id"
              :label="device.name"
              :value="device.id"
            />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="timeRange" @change="loadData">
            <el-option label="最近24小时" value="24h" />
            <el-option label="最近7天" value="7d" />
            <el-option label="最近30天" value="30d" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" :disabled="!selectedDevice" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 统计信息 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <span class="stat-label">平均温度</span>
            <span class="stat-value">{{ formatValue(stats.avg_temp, '℃') }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <span class="stat-label">平均湿度</span>
            <span class="stat-value">{{ formatValue(stats.avg_humidity, '%') }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <span class="stat-label">平均PM2.5</span>
            <span class="stat-value">{{ formatValue(stats.avg_pm25, 'μg/m³') }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-item">
            <span class="stat-label">平均CO2</span>
            <span class="stat-value">{{ formatValue(stats.avg_co2, 'ppm') }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表 -->
    <el-card>
      <template #header>
        <span>实时数据图表</span>
      </template>
      <div ref="chartRef" style="height: 400px"></div>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="data-table">
      <template #header>
        <span>历史数据</span>
      </template>
      <el-table :data="tableData" stripe v-loading="loading" max-height="400">
        <el-table-column prop="timestamp" label="时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.timestamp) }}
          </template>
        </el-table-column>
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
        <el-table-column label="光照强度">
          <template #default="{ row }">
            {{ formatValue(row.light_intensity, 'lux') }}
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
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getDevices } from '@/api/devices'
import { getRealtimeData, getStatistics, exportData } from '@/api/monitoring'

const loading = ref(false)
const devices = ref([])
const selectedDevice = ref(null)
const timeRange = ref('24h')
const tableData = ref([])
const chartRef = ref(null)

let chart = null
let refreshTimer = null

const stats = reactive({
  avg_temp: null,
  avg_humidity: null,
  avg_pm25: null,
  avg_co2: null
})

const formatValue = (value, unit = '') => {
  if (value === null || value === undefined) return '-'
  return `${value.toFixed(1)} ${unit}`
}

const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const loadDevices = async () => {
  try {
    const response = await getDevices()
    devices.value = response.results || response
    if (devices.value.length > 0) {
      selectedDevice.value = devices.value[0].id
      loadData()
    }
  } catch (error) {
    console.error('加载设备列表失败:', error)
    ElMessage.error(error?.response?.data?.error || error?.message || '加载设备列表失败')
  }
}

const loadData = async () => {
  if (!selectedDevice.value) return

  loading.value = true
  try {
    // 加载统计数据
    const statsData = await getStatistics(selectedDevice.value, timeRange.value)
    Object.assign(stats, statsData.summary)

    // 加载实时数据
    const realtimeData = await getRealtimeData(selectedDevice.value)
    tableData.value = realtimeData.data || []

    // 更新图表
    updateChart(tableData.value)
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error(error?.response?.data?.error || error?.message || '加载数据失败')
  } finally {
    loading.value = false
  }
}

const updateChart = (data) => {
  if (!data || data.length === 0) return

  const labels = data.map(item => {
    const date = new Date(item.timestamp)
    return date.toLocaleTimeString('zh-CN')
  }).reverse()

  const tempData = data.map(item => item.temperature).reverse()
  const humidityData = data.map(item => item.humidity).reverse()
  const pm25Data = data.map(item => item.pm25).reverse()

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['温度', '湿度', 'PM2.5']
    },
    xAxis: {
      type: 'category',
      data: labels,
      axisLabel: { rotate: 45 }
    },
    yAxis: [
      {
        type: 'value',
        name: '温度(℃) / 湿度(%)',
        position: 'left'
      },
      {
        type: 'value',
        name: 'PM2.5(μg/m³)',
        position: 'right'
      }
    ],
    series: [
      {
        name: '温度',
        type: 'line',
        data: tempData,
        smooth: true,
        itemStyle: { color: '#409EFF' }
      },
      {
        name: '湿度',
        type: 'line',
        data: humidityData,
        smooth: true,
        itemStyle: { color: '#67C23A' }
      },
      {
        name: 'PM2.5',
        type: 'line',
        yAxisIndex: 1,
        data: pm25Data,
        smooth: true,
        itemStyle: { color: '#E6A23C' }
      }
    ]
  }

  if (chart) {
    chart.setOption(option)
  } else if (chartRef.value) {
    chart = echarts.init(chartRef.value)
    chart.setOption(option)
  }
}

const handleExport = () => {
  if (!selectedDevice.value) return

  const endTime = new Date()
  const startTime = new Date(endTime)
  startTime.setHours(startTime.getHours() - 24)

  exportData({
    device_id: selectedDevice.value,
    start_time: startTime.toISOString().slice(0, 19).replace('T', ' '),
    end_time: endTime.toISOString().slice(0, 19).replace('T', ' '),
    type: 'excel'
  })
}

onMounted(() => {
  loadDevices()
  refreshTimer = setInterval(loadData, 60000) // 每分钟刷新一次
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  if (chart) {
    chart.dispose()
  }
})
</script>

<style scoped>
.monitoring {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-card {
  padding: 10px;
}

.stats-row {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
}

.stat-label {
  color: #999;
  font-size: 14px;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.data-table {
  margin-top: 20px;
}
</style>
