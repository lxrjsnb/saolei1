<template>
  <div class="devices">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>设备管理</span>
          <el-button type="primary" :icon="Plus" @click="showAddDialog">添加设备</el-button>
        </div>
      </template>

      <el-table :data="devices" stripe v-loading="loading">
        <el-table-column prop="name" label="设备名称" />
        <el-table-column prop="device_id" label="设备ID" />
        <el-table-column label="类型">
          <template #default="{ row }">
            {{ getDeviceTypeName(row.device_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="location" label="位置" />
        <el-table-column label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最后活跃" width="180">
          <template #default="{ row }">
            {{ row.last_active ? formatDateTime(row.last_active) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">查看</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加设备对话框 -->
    <el-dialog v-model="showDialog" title="添加设备" width="500px">
      <el-form :model="deviceForm" :rules="rules" ref="deviceFormRef" label-width="100px">
        <el-form-item label="设备名称" prop="name">
          <el-input v-model="deviceForm.name" placeholder="请输入设备名称" />
        </el-form-item>
        <el-form-item label="设备类型" prop="device_type">
          <el-select v-model="deviceForm.device_type" placeholder="请选择设备类型" style="width: 100%">
            <el-option label="温度传感器" value="temperature" />
            <el-option label="湿度传感器" value="humidity" />
            <el-option label="光照传感器" value="light" />
            <el-option label="PM2.5传感器" value="pm25" />
            <el-option label="CO2传感器" value="co2" />
            <el-option label="综合传感器" value="composite" />
          </el-select>
        </el-form-item>
        <el-form-item label="安装位置" prop="location">
          <el-input v-model="deviceForm.location" placeholder="请输入安装位置" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="deviceForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入设备描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getDevices, createDevice, deleteDevice, getDevice } from '@/api/devices'

const loading = ref(false)
const devices = ref([])
const showDialog = ref(false)
const submitting = ref(false)
const deviceFormRef = ref(null)

const deviceForm = reactive({
  name: '',
  device_type: '',
  location: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  device_type: [{ required: true, message: '请选择设备类型', trigger: 'change' }],
  location: [{ required: true, message: '请输入安装位置', trigger: 'blur' }]
}

const getDeviceTypeName = (type) => {
  const types = {
    'temperature': '温度传感器',
    'humidity': '湿度传感器',
    'light': '光照传感器',
    'pm25': 'PM2.5传感器',
    'co2': 'CO2传感器',
    'composite': '综合传感器'
  }
  return types[type] || type
}

const getStatusName = (status) => {
  const names = {
    'online': '在线',
    'offline': '离线',
    'maintenance': '维护中'
  }
  return names[status] || status
}

const getStatusType = (status) => {
  const types = {
    'online': 'success',
    'offline': 'danger',
    'maintenance': 'warning'
  }
  return types[status] || 'info'
}

const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const loadDevices = async () => {
  loading.value = true
  try {
    const response = await getDevices()
    devices.value = response.results || response
  } catch (error) {
    console.error('加载设备列表失败:', error)
    ElMessage.error(error?.response?.data?.error || error?.message || '加载设备列表失败')
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  Object.assign(deviceForm, {
    name: '',
    device_type: '',
    location: '',
    description: ''
  })
  showDialog.value = true
}

const handleSubmit = async () => {
  const valid = await deviceFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await createDevice(deviceForm)
    ElMessage.success('添加成功')
    showDialog.value = false
    loadDevices()
  } catch (error) {
    ElMessage.error(error.message || '添加失败')
  } finally {
    submitting.value = false
  }
}

const handleView = async (row) => {
  try {
    const device = await getDevice(row.id)
    ElMessageBox.alert(
      `
        <p><strong>设备名称:</strong> ${device.name}</p>
        <p><strong>设备ID:</strong> ${device.device_id}</p>
        <p><strong>设备类型:</strong> ${getDeviceTypeName(device.device_type)}</p>
        <p><strong>安装位置:</strong> ${device.location}</p>
        <p><strong>设备状态:</strong> ${getStatusName(device.status)}</p>
        <p><strong>创建时间:</strong> ${formatDateTime(device.created_at)}</p>
      `,
      '设备详情',
      { dangerouslyUseHTMLString: true }
    )
  } catch (error) {
    ElMessage.error('获取设备详情失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除此设备吗？', '提示', {
      type: 'warning'
    })
    await deleteDevice(row.id)
    ElMessage.success('删除成功')
    loadDevices()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadDevices()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
