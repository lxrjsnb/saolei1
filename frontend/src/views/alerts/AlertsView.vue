<template>
  <div class="alerts">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card stat-danger">
          <div class="stat-content">
            <div class="stat-value">{{ severityStats.critical || 0 }}</div>
            <div class="stat-label">严重</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card stat-high">
          <div class="stat-content">
            <div class="stat-value">{{ severityStats.high || 0 }}</div>
            <div class="stat-label">高</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card stat-medium">
          <div class="stat-content">
            <div class="stat-value">{{ severityStats.medium || 0 }}</div>
            <div class="stat-label">中</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card stat-low">
          <div class="stat-content">
            <div class="stat-value">{{ severityStats.low || 0 }}</div>
            <div class="stat-label">低</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 报警记录表格 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>报警记录</span>
          <div class="header-actions">
            <el-select v-model="statusFilter" placeholder="状态" @change="loadAlerts" style="width: 120px; margin-right: 10px">
              <el-option label="全部" value="" />
              <el-option label="待处理" value="pending" />
              <el-option label="已确认" value="acknowledged" />
              <el-option label="已解决" value="resolved" />
            </el-select>
            <el-button :icon="Refresh" @click="loadAlerts">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table :data="alerts" stripe v-loading="loading">
        <el-table-column prop="device_name" label="设备" width="150" />
        <el-table-column prop="message" label="报警信息" min-width="200" show-overflow-tooltip />
        <el-table-column label="严重程度" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)">
              {{ getSeverityName(row.severity) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="当前值" width="100">
          <template #default="{ row }">
            {{ row.current_value }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="triggered_at" label="触发时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.triggered_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button type="warning" size="small" @click="handleAcknowledge(row)">确认</el-button>
              <el-button type="success" size="small" @click="handleResolve(row)">解决</el-button>
            </template>
            <span v-else class="text-gray">已处理</span>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadAlerts"
        @current-change="loadAlerts"
        style="margin-top: 20px; justify-content: center"
      />
    </el-card>

    <!-- 备注对话框 -->
    <el-dialog v-model="showNotesDialog" title="添加备注" width="400px">
      <el-input
        v-model="notes"
        type="textarea"
        :rows="4"
        placeholder="请输入备注信息"
      />
      <template #footer>
        <el-button @click="showNotesDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmAction">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getAlertRecords, acknowledgeAlert, resolveAlert, getAlertStatistics } from '@/api/alerts'

const loading = ref(false)
const alerts = ref([])
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const severityStats = reactive({
  critical: 0,
  high: 0,
  medium: 0,
  low: 0
})

const showNotesDialog = ref(false)
const notes = ref('')
const currentAlert = ref(null)
const currentAction = ref('')

const getSeverityName = (severity) => {
  const names = {
    'critical': '严重',
    'high': '高',
    'medium': '中',
    'low': '低'
  }
  return names[severity] || severity
}

const getSeverityType = (severity) => {
  const types = {
    'critical': 'danger',
    'high': 'warning',
    'medium': 'info',
    'low': ''
  }
  return types[severity] || 'info'
}

const getStatusName = (status) => {
  const names = {
    'pending': '待处理',
    'acknowledged': '已确认',
    'resolved': '已解决',
    'false_alarm': '误报'
  }
  return names[status] || status
}

const getStatusType = (status) => {
  const types = {
    'pending': 'danger',
    'acknowledged': 'warning',
    'resolved': 'success',
    'false_alarm': 'info'
  }
  return types[status] || 'info'
}

const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const loadAlerts = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }

    const data = await getAlertRecords(params)
    alerts.value = data.results || data
    total.value = data.count || alerts.value.length
  } catch (error) {
    ElMessage.error('加载报警记录失败')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const stats = await getAlertStatistics('7d')
    Object.assign(severityStats, stats.severity_stats || {})
  } catch (error) {
    console.error('加载统计数据失败', error)
  }
}

const handleAcknowledge = (row) => {
  currentAlert.value = row
  currentAction.value = 'acknowledge'
  notes.value = ''
  showNotesDialog.value = true
}

const handleResolve = (row) => {
  currentAlert.value = row
  currentAction.value = 'resolve'
  notes.value = ''
  showNotesDialog.value = true
}

const confirmAction = async () => {
  try {
    if (currentAction.value === 'acknowledge') {
      await acknowledgeAlert(currentAlert.value.id, notes.value)
      ElMessage.success('已确认')
    } else if (currentAction.value === 'resolve') {
      await resolveAlert(currentAlert.value.id, notes.value)
      ElMessage.success('已解决')
    }
    showNotesDialog.value = false
    loadAlerts()
    loadStats()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  loadAlerts()
  loadStats()
})
</script>

<style scoped>
.alerts {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-row {
  display: flex;
  gap: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  text-align: center;
  padding: 10px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 10px;
}

.stat-label {
  color: #999;
  font-size: 14px;
}

.stat-danger .stat-value {
  color: #F56C6C;
}

.stat-high .stat-value {
  color: #E6A23C;
}

.stat-medium .stat-value {
  color: #409EFF;
}

.stat-low .stat-value {
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.text-gray {
  color: #999;
}
</style>
