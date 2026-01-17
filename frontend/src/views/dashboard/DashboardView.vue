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
              <div class="stat-value">{{ stats.total }}</div>
              <div class="stat-label">部件总数</div>
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
              <div class="stat-value">{{ stats.highRisk }}</div>
              <div class="stat-label">高风险（Level H）</div>
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
              <div class="stat-value">{{ stats.historyHighRisk }}</div>
              <div class="stat-label">历史高风险（有记录）</div>
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
              <div class="stat-value">{{ stats.marked }}</div>
              <div class="stat-label">已标记（mark≠0）</div>
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
            <span>近24小时风险事件</span>
          </template>
          <div ref="tempChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>A1-A7 异常分布</span>
          </template>
          <div ref="humidityChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最新数据表格 -->
    <el-row :gutter="20" class="data-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>组别明细</span>
          </template>
          <el-table :data="groupRows" stripe v-loading="loading" height="360">
            <el-table-column prop="name" label="Plant" width="140" />
            <el-table-column prop="expected_total" label="预期" width="90" />
            <el-table-column prop="total" label="当前" width="90" />
            <el-table-column prop="highRisk" label="高风险(H)" width="110" />
            <el-table-column prop="historyHighRisk" label="历史高风险" width="120" />
            <el-table-column prop="marked" label="标记" width="90" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近更新部件</span>
          </template>
          <el-table :data="recentRows" stripe v-loading="loading" height="360">
            <el-table-column prop="partNo" label="Robot" width="190" show-overflow-tooltip />
            <el-table-column prop="referenceNo" label="Reference" width="170" />
            <el-table-column prop="number" label="Number" width="100" />
            <el-table-column prop="typeSpec" label="Type" min-width="160" show-overflow-tooltip />
            <el-table-column prop="level" label="Level" width="90" />
            <el-table-column prop="mark" label="Mark" width="90" />
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
import { DEMO_MODE } from '@/config/appConfig'
import { getRobotsDashboard } from '@/api/robots'
import { createRiskEvents, getAllRobots } from '@/mock/robots'

const loading = ref(false)
const tempChartRef = ref(null)
const humidityChartRef = ref(null)
const groupRows = ref([])
const recentRows = ref([])

let tempChart = null
let humidityChart = null
let refreshTimer = null

const stats = reactive({
  total: 0,
  highRisk: 0,
  historyHighRisk: 0,
  marked: 0
})

const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const loadStats = async () => {
  loading.value = true
  try {
    if (DEMO_MODE) {
      const robots = getAllRobots()
      stats.total = robots.length
      stats.highRisk = robots.filter((r) => r.level === 'H').length
      stats.historyHighRisk = robots.filter((r) => r.riskHistory?.length).length
      stats.marked = robots.filter((r) => (r.mark ?? 0) !== 0).length

      groupRows.value = []
      recentRows.value = robots.slice(0, 18).map((r) => ({
        partNo: r.partNo,
        referenceNo: r.referenceNo,
        number: r.number ?? 0,
        typeSpec: r.typeSpec,
        level: r.level,
        mark: r.mark ?? 0
      }))

      const axisBad = {}
      for (const axis of ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7']) {
        axisBad[axis] = robots.filter((r) => r.checks?.[axis]?.ok === false).length
      }
      const events = createRiskEvents(120)
      updateCharts({ axisBad, events24h: events })
      return
    }

    const data = await getRobotsDashboard()
    stats.total = data.summary?.total ?? 0
    stats.highRisk = data.summary?.highRisk ?? 0
    stats.historyHighRisk = data.summary?.historyHighRisk ?? 0
    stats.marked = data.summary?.marked ?? 0

    groupRows.value = data.groupStats || []
    recentRows.value = (data.recentUpdated || []).slice(0, 18)

    updateCharts(data)
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error(error?.response?.data?.error || error?.message || '加载数据失败')
  } finally {
    loading.value = false
  }
}

const updateCharts = (dashboard) => {
  // 近24小时风险事件（折线）
  const events24h = dashboard.events24h || []
  const timeLabels = events24h.map((item) =>
    new Date(item.time || item.triggered_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  )
  const counts = events24h.map((item) => item.count ?? 1)

  if (tempChart) {
    tempChart.setOption({
      xAxis: { data: timeLabels },
      series: [{ data: counts }]
    })
  } else if (tempChartRef.value) {
    tempChart = echarts.init(tempChartRef.value)
    tempChart.setOption({
      title: { text: '' },
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: timeLabels,
        axisLabel: { rotate: 45 }
      },
      yAxis: { type: 'value', min: 0 },
      series: [{
        name: '事件数',
        type: 'line',
        data: counts,
        smooth: true,
        itemStyle: { color: '#409EFF' }
      }]
    })
  }

  // A1-A7 异常分布（柱状）
  const axisBad = dashboard.axisBad || {}
  const axisKeys = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7']
  const axisCounts = axisKeys.map((k) => axisBad[k] ?? 0)

  if (humidityChart) {
    humidityChart.setOption({
      xAxis: { data: axisKeys },
      series: [{ data: axisCounts }]
    })
  } else if (humidityChartRef.value) {
    humidityChart = echarts.init(humidityChartRef.value)
    humidityChart.setOption({
      title: { text: '' },
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      xAxis: {
        type: 'category',
        data: axisKeys
      },
      yAxis: {
        type: 'value',
        minInterval: 1
      },
      series: [{
        name: '异常数量',
        type: 'bar',
        data: axisCounts,
        itemStyle: { color: '#E6A23C' },
        barWidth: '60%'
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
