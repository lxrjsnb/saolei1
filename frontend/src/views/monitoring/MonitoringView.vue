<template>
  <div class="trajectory">
    <el-card class="filter-card">
      <template #header>
        <div class="card-header">
          <div class="title">
            <span class="title-text">关键轨迹检查</span>
            <span class="title-sub">按车间、时间范围与关键字筛选，支持排序与导出</span>
          </div>
          <el-button type="primary" :icon="Download" @click="handleExport">导出Excel</el-button>
        </div>
      </template>

      <el-row :gutter="16" align="middle">
        <el-col :xs="24" :sm="12" :md="6">
          <el-select v-model="plant" placeholder="Plant" clearable filterable>
            <el-option v-for="p in plants" :key="p" :label="p" :value="p" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="12" :md="10">
          <el-date-picker
            v-model="timeRange"
            type="datetimerange"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            :default-time="defaultTime"
            unlink-panels
          />
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-input v-model="keyword" placeholder="关键字（手动输入）" clearable />
        </el-col>
        <el-col :xs="24" :sm="12" :md="2" class="actions">
          <el-button type="primary" :icon="Search" :loading="loading" @click="loadRows">查询</el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-card>
      <template #header>
        <div class="table-header">
          <span>检查结果</span>
          <span class="table-meta">
            共 {{ filteredRows.length }} 条
          </span>
        </div>
      </template>

      <el-table
        :data="pagedRows"
        stripe
        height="560"
        v-loading="loading"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="time" label="时间" width="180" sortable>
          <template #default="{ row }">
            {{ formatDateTime(row.time) }}
          </template>
        </el-table-column>
        <el-table-column prop="plant" label="Plant" width="120" sortable />
        <el-table-column prop="partNo" label="Robot" width="190" sortable show-overflow-tooltip>
          <template #default="{ row }">
            <span class="mono">{{ row.partNo }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="referenceNo" label="Reference" width="170" sortable />
        <el-table-column prop="axis" label="Axis" width="90" sortable />
        <el-table-column prop="deviation" label="偏差" width="110" sortable>
          <template #default="{ row }">
            <span :class="row.result === 'fail' ? 'bad' : 'ok'">{{ row.deviation.toFixed(3) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="durationMs" label="耗时(ms)" width="120" sortable />
        <el-table-column prop="result" label="结果" width="110" sortable>
          <template #default="{ row }">
            <el-tag :type="row.result === 'pass' ? 'success' : 'danger'" effect="light">
              {{ row.result === 'pass' ? '通过' : '异常' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="filteredRows.length"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        class="pager"
      />
    </el-card>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Search } from '@element-plus/icons-vue'
import { DEMO_MODE } from '@/config/appConfig'
import { getRobotComponents } from '@/api/robots'
import { getAllRobots, robotGroups } from '@/mock/robots'

const keywords = ['路径偏移', '速度突变', '轨迹抖动', '停靠点误差', '路径重规划', '跟踪误差']
const defaultTime = [new Date(2000, 1, 1, 8, 0, 0), new Date(2000, 1, 1, 18, 0, 0)]

const plants = robotGroups.map((g) => g.name)
const plant = ref('')
const keyword = ref('')
const timeRange = ref([new Date(Date.now() - 24 * 3600_000), new Date()])

const loading = ref(false)
const allRows = ref([])

const sortState = ref({ prop: 'time', order: 'descending' })
const currentPage = ref(1)
const pageSize = ref(20)

const formatDateTime = (value) => new Date(value).toLocaleString('zh-CN')

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

const toArray = (value) => (Array.isArray(value) ? value : value ? [value] : [])

const buildRows = (components, count = 240) => {
  const axes = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7']
  const start = new Date(timeRange.value?.[0] || Date.now() - 24 * 3600_000).getTime()
  const end = new Date(timeRange.value?.[1] || Date.now()).getTime()
  const ms = Math.max(1, end - start)

  const rows = []
  const seed = hashString(`trajectory::${start}::${end}`)
  const rand = mulberry32(seed)

  for (let i = 0; i < count; i += 1) {
    const c = components[Math.floor(rand() * components.length)]
    const axis = axes[Math.floor(rand() * axes.length)]
    const kw = keywords[Math.floor(rand() * keywords.length)]
    const t = new Date(start + rand() * ms)

    const ok = c?.checks?.[axis]?.ok !== false
    const base = ok ? 0.015 : 0.06
    const deviation = Math.max(0, base + (rand() - 0.5) * (ok ? 0.02 : 0.07))
    const durationMs = Math.round(120 + rand() * 680 + (ok ? 0 : 180))
    const result = deviation > 0.05 ? 'fail' : 'pass'

    rows.push({
      id: `${i + 1}`,
      time: t.toISOString(),
      plant: c.group || c.plant || '-',
      partNo: c.partNo,
      referenceNo: c.referenceNo,
      axis,
      keyword: kw,
      deviation,
      durationMs,
      result
    })
  }
  return rows
}

const loadRows = async () => {
  loading.value = true
  try {
    let components = []
    if (DEMO_MODE) {
      components = getAllRobots().slice(0, 800)
    } else {
      const params = { tab: 'all', page: 1, page_size: 400 }
      const data = await getRobotComponents(params)
      components = (data.results || data).map((r) => ({
        group: r.group,
        partNo: r.partNo,
        referenceNo: r.referenceNo,
        checks: r.checks
      }))
    }
    allRows.value = buildRows(components, 260)
    currentPage.value = 1
  } catch (e) {
    ElMessage.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const filteredRows = computed(() => {
  const rows = toArray(allRows.value)
  const p = plant.value
  const k = keyword.value.trim().toLowerCase()
  const out = rows.filter((r) => {
    if (p && r.plant !== p) return false
    if (k) {
      const hay = `${r.keyword} ${r.partNo} ${r.referenceNo} ${r.axis}`.toLowerCase()
      if (!hay.includes(k)) return false
    }
    return true
  })

  const { prop, order } = sortState.value
  if (!prop || !order) return out

  const dir = order === 'ascending' ? 1 : -1
  const sorted = out.slice().sort((a, b) => {
    const av = a[prop]
    const bv = b[prop]
    if (av === bv) return 0
    if (av === null || av === undefined) return 1
    if (bv === null || bv === undefined) return -1
    if (typeof av === 'number' && typeof bv === 'number') return (av - bv) * dir
    return String(av).localeCompare(String(bv), 'zh-CN') * dir
  })

  return sorted
})

const pagedRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredRows.value.slice(start, start + pageSize.value)
})

const handleSortChange = ({ prop, order }) => {
  sortState.value = { prop, order }
}

const handleExport = () => {
  ElMessage.success('已生成导出任务（演示按钮）')
}

loadRows()
</script>

<style scoped>
.trajectory {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-card :deep(.el-input__wrapper),
.filter-card :deep(.el-select__wrapper),
.filter-card :deep(.el-date-editor.el-input__wrapper) {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.actions {
  display: flex;
  justify-content: flex-end;
}

.actions :deep(.el-button) {
  width: 100%;
  border-radius: 12px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.table-meta {
  color: var(--app-muted);
  font-size: 12px;
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

.ok {
  color: rgba(15, 23, 42, 0.7);
}

.bad {
  color: #b91c1c;
  font-weight: 800;
}

.pager {
  margin-top: 16px;
  justify-content: center;
}
</style>
