<template>
  <div class="bi">
    <el-card class="query-card">
      <template #header>
        <div class="card-header">
          <div class="title">
            <span class="title-text">可视化BI</span>
            <span class="title-sub">按组、机器人与指标轴快速查询并加载可视化结果</span>
          </div>
          <div class="header-actions">
            <el-tag effect="light" type="info">数据源：{{ DEMO_MODE ? '演示' : 'MySQL' }}</el-tag>
            <el-button :icon="Refresh" @click="resetForm">重置</el-button>
          </div>
        </div>
      </template>

      <el-form :model="form" label-position="top" class="query-form">
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item label="Plant">
              <el-select v-model="form.plant" placeholder="请选择组" filterable @change="handlePlantChange">
                <el-option v-for="g in groups" :key="g.key" :label="g.name" :value="g.key" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="10">
            <el-form-item label="Robot / Table">
              <el-select
                v-model="form.componentId"
                class="robot-select"
                placeholder="搜索机器人：名称 / 部件编号 / 参考编号"
                filterable
                remote
                reserve-keyword
                :remote-method="remoteSearchRobots"
                :loading="robotSearching"
                clearable
                @change="handleRobotChange"
              >
                <el-option
                  v-for="item in robotOptions"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                >
                  <div class="option-row">
                    <div class="option-left">
                      <span class="option-name">{{ item.name }}</span>
                      <span class="option-meta">
                        <span class="mono">{{ item.partNo }}</span>
                        <span class="meta-sep">•</span>
                        <span>{{ item.referenceNo }}</span>
                      </span>
                    </div>
                    <span class="option-sub">{{ item.plant }}</span>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="24" :md="8">
            <el-form-item label="Select Data Range">
              <el-date-picker
                v-model="form.range"
                type="datetimerange"
                class="range-picker"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                format="YYYY-MM-DD HH:mm"
                :default-time="defaultTime"
                unlink-panels
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :xs="24" :sm="24" :md="18">
            <el-form-item label="Axis Select">
              <el-select v-model="form.axes" placeholder="选择 A1-A7（可多选）" multiple collapse-tags collapse-tags-tooltip>
                <el-option v-for="k in AXES" :key="k" :label="k" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="24" :md="6" class="load-col">
            <el-button type="primary" :icon="DataLine" :loading="loading" @click="loadData">
              Load Data
            </el-button>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-row :gutter="16" class="content-row">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="chart-header">
              <span>细节图</span>
              <div class="chart-meta" v-if="activeRobot">
                <el-tag :type="levelTagType(activeRobot.level)" effect="light">Level {{ activeRobot.level }}</el-tag>
                <span class="mono">{{ activeRobot.partNo }}</span>
              </div>
            </div>
          </template>
          <div ref="chartRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>BI 概览</span>
          </template>
          <div v-if="activeRobot" class="overview">
            <div class="overview-row">
              <div class="overview-label">Robot</div>
              <div class="overview-value">{{ activeRobot.partNo }}</div>
            </div>
            <div class="overview-row">
              <div class="overview-label">Reference</div>
              <div class="overview-value">{{ activeRobot.referenceNo }}</div>
            </div>
            <div class="overview-row">
              <div class="overview-label">Type</div>
              <div class="overview-value">{{ activeRobot.typeSpec }}</div>
            </div>
            <div class="overview-row">
              <div class="overview-label">Tech</div>
              <div class="overview-value">{{ activeRobot.tech }}</div>
            </div>
            <div class="overview-row">
              <div class="overview-label">Mark</div>
              <div class="overview-value mono">{{ activeRobot.mark ?? 0 }}</div>
            </div>
            <div class="overview-row">
              <div class="overview-label">Remark</div>
              <div class="overview-value" style="white-space: normal">{{ activeRobot.remark }}</div>
            </div>

            <div class="checks">
              <div class="checks-title">A1-A7 状态</div>
              <div class="checks-grid">
                <div v-for="k in AXES" :key="k" class="check-item">
                  <el-tooltip :content="checkTooltip(activeRobot, k)" placement="top" :show-after="120">
                    <div class="check-cell">
                      <span class="check-key">{{ k }}</span>
                      <span class="dot" :class="activeRobot.checks?.[k]?.ok ? 'dot-ok' : 'dot-bad'"></span>
                    </div>
                  </el-tooltip>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="请选择机器人并加载数据" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { DataLine, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { DEMO_MODE } from '@/config/appConfig'
import { getRobotComponent, getRobotComponents, getRobotGroups } from '@/api/robots'
import { createTelemetrySeries, getAllRobots, robotGroups as mockGroups } from '@/mock/robots'

const router = useRouter()
const route = useRoute()

const AXES = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7']
const defaultTime = [new Date(2000, 1, 1, 8, 0, 0), new Date(2000, 1, 1, 18, 0, 0)]

const groupsData = ref([])
const robotOptions = ref([])
const robotSearching = ref(false)

const loading = ref(false)
const chartRef = ref(null)
let chart = null
let resizeHandler = null

const now = new Date()
const yesterday = new Date(now.getTime() - 24 * 3600_000)

const form = reactive({
  plant: (DEMO_MODE ? mockGroups[0].key : ''),
  componentId: null,
  range: [yesterday, now],
  axes: ['A2']
})

const activeRobot = ref(null)

const groups = computed(() => {
  if (DEMO_MODE) return mockGroups
  return groupsData.value
})

const levelTagType = (level) => {
  const types = { H: 'danger', M: 'warning', L: 'info' }
  return types[level] || 'info'
}

const checkTooltip = (robot, key) => {
  const check = robot?.checks?.[key]
  const label = check?.label ? `${key}（${check.label}）` : key
  if (!check) return label
  return check.ok ? `${label}：正常/符合要求` : `${label}：存在异常/待处理`
}

const hashString = (text) => {
  let hash = 2166136261
  for (let i = 0; i < text.length; i += 1) {
    hash ^= text.charCodeAt(i)
    hash = Math.imul(hash, 16777619)
  }
  return hash >>> 0
}

const mulberry32 = (seed) => {
  let t = seed >>> 0
  return () => {
    t += 0x6D2B79F5
    let x = t
    x = Math.imul(x ^ (x >>> 15), x | 1)
    x ^= x + Math.imul(x ^ (x >>> 7), x | 61)
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296
  }
}

const buildAxisSeries = (robot, axisKey, start, end) => {
  const ms = end.getTime() - start.getTime()
  const points = Math.max(30, Math.min(180, Math.round(ms / (8 * 60_000))))
  const interval = Math.max(60, Math.round(ms / points / 1000))

  const telemetry = createTelemetrySeries(robot.robot_id || robot.id, points, interval)
  const ok = robot.checks?.[axisKey]?.ok !== false

  const rand = mulberry32(hashString(`${robot.robot_id || robot.id}::${axisKey}`))
  return telemetry.map((row, idx) => {
    const base = ok ? 0.12 : 0.72
    const wave = Math.sin(idx / 7) * (ok ? 0.06 : 0.1)
    const noise = (rand() - 0.5) * (ok ? 0.06 : 0.12)
    const spike = !ok && rand() < 0.06 ? 0.25 + rand() * 0.18 : 0
    const value = Math.max(0, Math.min(1, base + wave + noise + spike))
    return [row.timestamp, value]
  })
}

const renderChart = (robot, axes, range) => {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)

  const [start, end] = range
  const series = axes.map((axisKey, idx) => {
    const data = buildAxisSeries(robot, axisKey, start, end)
    const ok = robot.checks?.[axisKey]?.ok !== false
    const colors = ['#2563eb', '#16a34a', '#b45309', '#7c3aed', '#0891b2', '#be123c', '#334155']
    const color = colors[idx % colors.length]
    return {
      name: axisKey,
      type: 'line',
      showSymbol: false,
      smooth: true,
      data,
      lineStyle: { width: 2, color: ok ? color : '#ef4444' },
      areaStyle: { opacity: 0.08, color: ok ? color : '#ef4444' }
    }
  })

  chart.setOption({
    grid: { top: 28, right: 18, bottom: 42, left: 46 },
    tooltip: { trigger: 'axis' },
    legend: { data: axes, textStyle: { color: 'rgba(15, 23, 42, 0.75)' } },
    xAxis: {
      type: 'time',
      axisLabel: { color: 'rgba(15, 23, 42, 0.65)' },
      splitLine: { lineStyle: { color: 'rgba(15, 23, 42, 0.06)' } }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 1,
      axisLabel: { color: 'rgba(15, 23, 42, 0.65)' },
      splitLine: { lineStyle: { color: 'rgba(15, 23, 42, 0.06)' } }
    },
    series
  })
}

const loadGroups = async () => {
  if (DEMO_MODE) return
  groupsData.value = await getRobotGroups()
  if (!form.plant && groupsData.value.length) {
    form.plant = groupsData.value[0].key
  }
}

const remoteSearchRobots = async (query) => {
  if (!query || !query.trim()) {
    robotOptions.value = []
    return
  }

  robotSearching.value = true
  try {
    if (DEMO_MODE) {
      const key = query.trim().toLowerCase()
      const list = getAllRobots()
        .filter((r) => r.group === form.plant)
        .filter((r) =>
          r.name.toLowerCase().includes(key) ||
          r.partNo.toLowerCase().includes(key) ||
          r.referenceNo.toLowerCase().includes(key)
        )
        .slice(0, 50)
        .map((r) => ({
          id: r.id,
          name: r.name,
          partNo: r.partNo,
          referenceNo: r.referenceNo,
          plant: r.group
        }))
      robotOptions.value = list
      return
    }

    const params = { group: form.plant, tab: 'all', keyword: query, page: 1, page_size: 50 }
    const data = await getRobotComponents(params)
    const rows = data.results || data
    robotOptions.value = rows.map((r) => ({
      id: r.id,
      name: r.name || r.partNo || r.robot_id,
      partNo: r.partNo,
      referenceNo: r.referenceNo,
      plant: r.group
    }))
  } catch (e) {
    robotOptions.value = []
  } finally {
    robotSearching.value = false
  }
}

const resolveRobotFromId = async (componentId) => {
  if (!componentId) return null
  if (DEMO_MODE) {
    return getAllRobots().find((r) => r.id === componentId) || null
  }
  return await getRobotComponent(componentId)
}

const loadData = async () => {
  if (!form.plant) {
    ElMessage.warning('请选择组（plant）')
    return
  }
  if (!form.componentId) {
    ElMessage.warning('请选择机器人（enter table name）')
    return
  }
  if (!form.axes?.length) {
    ElMessage.warning('请选择指标轴（A1-A7）')
    return
  }

  loading.value = true
  try {
    const robot = await resolveRobotFromId(form.componentId)
    if (!robot) {
      ElMessage.error('未找到机器人数据')
      return
    }

    activeRobot.value = robot
    renderChart(robot, form.axes, form.range)

    router.replace({
      path: '/alerts',
      query: {
        plant: form.plant,
        componentId: String(form.componentId),
        axes: form.axes.join(','),
        start: new Date(form.range[0]).toISOString(),
        end: new Date(form.range[1]).toISOString()
      }
    })
  } finally {
    loading.value = false
  }
}

const handlePlantChange = () => {
  form.componentId = null
  activeRobot.value = null
  robotOptions.value = []
}

const handleRobotChange = async () => {
  if (!form.componentId) {
    activeRobot.value = null
    return
  }
  // Allow quick load after selecting robot
  await loadData()
}

const resetForm = () => {
  const now2 = new Date()
  const yesterday2 = new Date(now2.getTime() - 24 * 3600_000)
  form.plant = DEMO_MODE ? mockGroups[0].key : (groupsData.value[0]?.key || '')
  form.componentId = null
  form.range = [yesterday2, now2]
  form.axes = ['A2']
  activeRobot.value = null
  robotOptions.value = []
  if (chart) chart.clear()
}

const hydrateFromRoute = async () => {
  const plant = route.query.plant?.toString()
  const componentId = route.query.componentId?.toString()
  const axes = route.query.axes?.toString()
  const start = route.query.start?.toString()
  const end = route.query.end?.toString()

  if (plant) form.plant = plant
  if (axes) form.axes = axes.split(',').filter(Boolean)
  if (start && end) {
    const s = new Date(start)
    const e = new Date(end)
    if (!Number.isNaN(s.getTime()) && !Number.isNaN(e.getTime())) {
      form.range = [s, e]
    }
  }
  if (componentId) {
    form.componentId = DEMO_MODE ? componentId : Number(componentId)
    await loadData()
  }
}

onMounted(async () => {
  await loadGroups()
  await hydrateFromRoute()
  resizeHandler = () => chart?.resize()
  window.addEventListener('resize', resizeHandler)
})

onUnmounted(() => {
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
  }
  if (chart) chart.dispose()
  chart = null
})

watch(
  () => route.query,
  async (q, prev) => {
    if (q?.componentId && q?.componentId !== prev?.componentId) {
      await hydrateFromRoute()
    }
  }
)
</script>

<style scoped>
.bi {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.title {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.title-text {
  font-size: 16px;
  font-weight: 800;
}

.title-sub {
  color: var(--app-muted);
  font-size: 12px;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.query-form :deep(.el-select),
.query-form :deep(.el-date-editor) {
  width: 100%;
}

.query-form :deep(.el-form-item) {
  margin-bottom: 14px;
}

.query-form :deep(.el-form-item__label) {
  font-weight: 700;
  color: rgba(15, 23, 42, 0.82);
  padding-bottom: 6px;
}

.query-form :deep(.el-input__wrapper),
.query-form :deep(.el-select__wrapper) {
  border-radius: 12px;
}

.range-picker :deep(.el-range-editor.el-input__wrapper) {
  min-height: 40px;
}

.robot-select :deep(.el-select__wrapper) {
  background: rgba(148, 163, 184, 0.06);
}

.load-col {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.load-col :deep(.el-form-item__content) {
  width: 100%;
}

.load-col :deep(.el-button) {
  width: 100%;
  height: 40px;
  border-radius: 12px;
  font-weight: 700;
}

.chart {
  height: 420px;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.chart-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-variant-numeric: tabular-nums;
}

.overview {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.overview-row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.overview-label {
  width: 86px;
  color: var(--app-muted);
  font-size: 12px;
  padding-top: 2px;
}

.overview-value {
  flex: 1;
  font-size: 13px;
  font-weight: 600;
  color: rgba(15, 23, 42, 0.86);
  word-break: break-word;
}

.checks {
  margin-top: 6px;
  padding-top: 12px;
  border-top: 1px solid var(--app-border);
}

.checks-title {
  font-weight: 700;
  margin-bottom: 10px;
}

.checks-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.check-cell {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 12px;
  background: rgba(148, 163, 184, 0.06);
}

.check-key {
  font-weight: 800;
  color: rgba(15, 23, 42, 0.8);
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 0 2px rgba(15, 23, 42, 0.06);
}

.dot-ok {
  background: #22c55e;
}

.dot-bad {
  background: #ef4444;
}

.option-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
}

.option-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.option-name {
  font-weight: 700;
  color: rgba(15, 23, 42, 0.86);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.option-meta {
  display: inline-flex;
  gap: 6px;
  align-items: center;
  color: rgba(15, 23, 42, 0.62);
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meta-sep {
  color: rgba(15, 23, 42, 0.28);
}

.option-sub {
  color: var(--app-muted);
  font-size: 12px;
  flex: none;
  padding-left: 10px;
}
</style>
