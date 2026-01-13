// 仪表盘页面脚本

// 设备管理相关
let devicesData = [];
let monitoringChart = null;

// 加载设备列表
async function loadDevices() {
    try {
        devicesData = await devicesAPI.list();
        const tbody = document.getElementById('deviceTable');

        if (!devicesData || devicesData.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">暂无设备</td></tr>';
            return;
        }

        tbody.innerHTML = devicesData.map(device => `
            <tr>
                <td>${device.name}</td>
                <td>${device.device_id}</td>
                <td>${getDeviceTypeName(device.device_type)}</td>
                <td>${device.location}</td>
                <td><span class="status-badge status-${device.status}">${getDeviceStatusName(device.status)}</span></td>
                <td>${device.last_active ? formatDateTime(device.last_active) : '-'}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="viewDevice(${device.id})">查看</button>
                        <button class="btn btn-outline-danger" onclick="deleteDevice(${device.id})">删除</button>
                    </div>
                </td>
            </tr>
        `).join('');

        // 更新监测页面的设备选择器
        updateDeviceSelector();
    } catch (error) {
        showNotification('加载设备列表失败: ' + error.message, 'danger');
    }
}

function getDeviceTypeName(type) {
    const types = {
        'temperature': '温度传感器',
        'humidity': '湿度传感器',
        'light': '光照传感器',
        'pm25': 'PM2.5传感器',
        'co2': 'CO2传感器',
        'composite': '综合传感器',
    };
    return types[type] || type;
}

function getDeviceStatusName(status) {
    const statuses = {
        'online': '在线',
        'offline': '离线',
        'maintenance': '维护中',
    };
    return statuses[status] || status;
}

// 查看设备详情
async function viewDevice(deviceId) {
    try {
        const device = await devicesAPI.get(deviceId);
        showNotification(`设备: ${device.name}\n类型: ${getDeviceTypeName(device.device_type)}\n位置: ${device.location}`, 'info');
    } catch (error) {
        showNotification('获取设备详情失败: ' + error.message, 'danger');
    }
}

// 删除设备
async function deleteDevice(deviceId) {
    if (!confirm('确定要删除此设备吗？')) return;

    try {
        await devicesAPI.delete(deviceId);
        showNotification('设备已删除', 'success');
        loadDevices();
    } catch (error) {
        showNotification('删除设备失败: ' + error.message, 'danger');
    }
}

// 显示添加设备模态框
function showAddDeviceModal() {
    // 简单实现，使用prompt获取基本信息
    const name = prompt('设备名称:');
    if (!name) return;

    const deviceType = prompt('设备类型 (temperature/humidity/light/pm25/co2/composite):');
    if (!deviceType) return;

    const location = prompt('安装位置:');
    if (!location) return;

    addDevice({
        name,
        device_type: deviceType,
        location,
        description: ''
    });
}

// 添加设备
async function addDevice(deviceData) {
    try {
        // 生成随机设备ID
        deviceData.device_id = 'DEV' + Date.now().toString().slice(-6);

        await devicesAPI.create(deviceData);
        showNotification('设备添加成功', 'success');
        loadDevices();
    } catch (error) {
        showNotification('添加设备失败: ' + error.message, 'danger');
    }
}

// 监测数据相关
function updateDeviceSelector() {
    const select = document.getElementById('monitoringDeviceSelect');
    select.innerHTML = '<option value="">请选择设备</option>' +
        devicesData.map(device => `<option value="${device.id}">${device.name}</option>`).join('');
}

// 加载监测数据
async function loadMonitoringData() {
    const deviceId = document.getElementById('monitoringDeviceSelect').value;
    const timeRange = document.getElementById('timeRangeSelect').value;

    if (!deviceId) {
        showNotification('请先选择设备', 'warning');
        return;
    }

    try {
        const stats = await monitoringAPI.statistics(deviceId, timeRange);

        // 显示统计信息
        console.log('统计数据:', stats);

        // 加载图表数据
        const realtimeData = await monitoringAPI.realtime(deviceId);
        updateMonitoringChart(realtimeData.data);
    } catch (error) {
        showNotification('加载监测数据失败: ' + error.message, 'danger');
    }
}

// 更新监测图表
function updateMonitoringChart(data) {
    const ctx = document.getElementById('monitoringChart').getContext('2d');

    const labels = data.map(item => {
        const date = new Date(item.timestamp);
        return date.toLocaleTimeString('zh-CN');
    });

    const tempData = data.map(item => item.temperature);
    const humidityData = data.map(item => item.humidity);
    const pm25Data = data.map(item => item.pm25);

    if (monitoringChart) monitoringChart.destroy();

    monitoringChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels.reverse(),
            datasets: [
                {
                    label: '温度 (℃)',
                    data: tempData.reverse(),
                    borderColor: 'rgb(255, 99, 132)',
                    yAxisID: 'y',
                    tension: 0.1
                },
                {
                    label: '湿度 (%)',
                    data: humidityData.reverse(),
                    borderColor: 'rgb(54, 162, 235)',
                    yAxisID: 'y',
                    tension: 0.1
                },
                {
                    label: 'PM2.5 (μg/m³)',
                    data: pm25Data.reverse(),
                    borderColor: 'rgb(255, 206, 86)',
                    yAxisID: 'y1',
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            }
        }
    });
}

// 导出数据
function exportData() {
    const deviceId = document.getElementById('monitoringDeviceSelect').value;
    if (!deviceId) {
        showNotification('请先选择设备', 'warning');
        return;
    }

    const endTime = new Date();
    const startTime = new Date(endTime - 24 * 60 * 60 * 1000);

    monitoringAPI.export({
        device_id: deviceId,
        start_time: startTime.toISOString().slice(0, 19).replace('T', ' '),
        end_time: endTime.toISOString().slice(0, 19).replace('T', ' '),
        type: 'excel'
    });
}

// 报警管理相关
async function loadAlerts() {
    try {
        const records = await alertsAPI.listRecords();
        const stats = await alertsAPI.statistics('7d');

        // 更新统计数据
        const severityStats = stats.severity_stats || {};
        document.getElementById('criticalAlerts').textContent = severityStats.critical || 0;
        document.getElementById('highAlerts').textContent = severityStats.high || 0;
        document.getElementById('mediumAlerts').textContent = severityStats.medium || 0;
        document.getElementById('lowAlerts').textContent = severityStats.low || 0;

        // 更新报警记录表格
        updateAlertTable(records);
    } catch (error) {
        showNotification('加载报警数据失败: ' + error.message, 'danger');
    }
}

function updateAlertTable(records) {
    const tbody = document.getElementById('alertTable');

    if (!records || records.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">暂无报警记录</td></tr>';
        return;
    }

    tbody.innerHTML = records.map(alert => `
        <tr class="alert-${alert.status}">
            <td>${alert.device_name}</td>
            <td>${alert.message}</td>
            <td><span class="severity-badge severity-${alert.severity}">${getSeverityName(alert.severity)}</span></td>
            <td>${alert.current_value}</td>
            <td>${getAlertStatusName(alert.status)}</td>
            <td>${formatDateTime(alert.triggered_at)}</td>
            <td>
                ${alert.status === 'pending' ? `
                    <button class="btn btn-sm btn-outline-warning" onclick="acknowledgeAlert(${alert.id})">确认</button>
                    <button class="btn btn-sm btn-outline-success" onclick="resolveAlert(${alert.id})">解决</button>
                ` : '-'}
            </td>
        </tr>
    `).join('');
}

function getSeverityName(severity) {
    const severities = {
        'critical': '严重',
        'high': '高',
        'medium': '中',
        'low': '低',
    };
    return severities[severity] || severity;
}

function getAlertStatusName(status) {
    const statuses = {
        'pending': '待处理',
        'acknowledged': '已确认',
        'resolved': '已解决',
        'false_alarm': '误报',
    };
    return statuses[status] || status;
}

async function acknowledgeAlert(alertId) {
    try {
        await alertsAPI.acknowledge(alertId);
        showNotification('报警已确认', 'success');
        loadAlerts();
    } catch (error) {
        showNotification('确认报警失败: ' + error.message, 'danger');
    }
}

async function resolveAlert(alertId) {
    try {
        await alertsAPI.resolve(alertId);
        showNotification('报警已解决', 'success');
        loadAlerts();
    } catch (error) {
        showNotification('解决报警失败: ' + error.message, 'danger');
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    // 根据当前页面加载数据
    const pageId = window.location.hash.substring(1) || 'dashboard';

    if (pageId === 'devices') {
        loadDevices();
    } else if (pageId === 'monitoring') {
        loadDevices().then(() => updateDeviceSelector());
    } else if (pageId === 'alerts') {
        loadAlerts();
    }
});

// 监听页面切换
window.addEventListener('hashchange', () => {
    const pageId = window.location.hash.substring(1) || 'dashboard';

    if (pageId === 'devices') {
        loadDevices();
    } else if (pageId === 'monitoring') {
        loadDevices().then(() => updateDeviceSelector());
    } else if (pageId === 'alerts') {
        loadAlerts();
    }
});
