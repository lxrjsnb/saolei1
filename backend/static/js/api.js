// API配置
const API_BASE_URL = '/api';

// 存储token
let authToken = localStorage.getItem('authToken');

// 设置认证头
function getAuthHeaders() {
    const headers = {
        'Content-Type': 'application/json',
    };
    if (authToken) {
        headers['Authorization'] = `Token ${authToken}`;
    }
    return headers;
}

// 通用API请求函数
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: getAuthHeaders(),
    };

    const response = await fetch(API_BASE_URL + url, {
        ...defaultOptions,
        ...options,
    });

    if (response.status === 401) {
        // Token过期，清除本地存储
        localStorage.removeItem('authToken');
        authToken = null;
        updateAuthUI();
        // 显示登录模态框
        const modal = new bootstrap.Modal(document.getElementById('loginModal'));
        modal.show();
        throw new Error('未授权');
    }

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || error.detail || '请求失败');
    }

    return response.json();
}

// 用户认证API
const authAPI = {
    // 注册
    register: (username, password, email) => apiRequest('/auth/register/', {
        method: 'POST',
        body: JSON.stringify({ username, password, email }),
    }),

    // 登录
    login: (username, password) => apiRequest('/auth/login/', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
    }),

    // 登出
    logout: () => apiRequest('/auth/logout/', {
        method: 'POST',
    }),

    // 获取用户信息
    profile: () => apiRequest('/auth/profile/'),
};

// 设备管理API
const devicesAPI = {
    // 获取设备列表
    list: () => apiRequest('/devices/devices/'),

    // 获取设备详情
    get: (id) => apiRequest(`/devices/devices/${id}/`),

    // 创建设备
    create: (data) => apiRequest('/devices/devices/', {
        method: 'POST',
        body: JSON.stringify(data),
    }),

    // 更新设备
    update: (id, data) => apiRequest(`/devices/devices/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
    }),

    // 删除设备
    delete: (id) => apiRequest(`/devices/devices/${id}/`, {
        method: 'DELETE',
    }),

    // 获取设备最新数据
    latestData: (id) => apiRequest(`/devices/devices/${id}/latest_data/`),

    // 更新设备配置
    updateConfig: (id, data) => apiRequest(`/devices/devices/${id}/update_config/`, {
        method: 'POST',
        body: JSON.stringify(data),
    }),
};

// 监测数据API
const monitoringAPI = {
    // 获取所有设备最新数据
    latestAll: () => apiRequest('/monitoring/data/latest/'),

    // 上报数据
    upload: (data) => apiRequest('/monitoring/upload/', {
        method: 'POST',
        body: JSON.stringify(data),
    }),

    // 查询历史数据
    query: (params) => apiRequest(`/monitoring/query/?${new URLSearchParams(params)}`),

    // 获取实时数据
    realtime: (deviceId) => apiRequest(`/monitoring/realtime/${deviceId}/`),

    // 获取统计数据
    statistics: (deviceId, range = '24h') => apiRequest(`/monitoring/statistics/${deviceId}/?range=${range}`),

    // 导出数据
    export: (params) => {
        const url = `${API_BASE_URL}/monitoring/export/?${new URLSearchParams(params)}`;
        window.open(url, '_blank');
    },
};

// 报警管理API
const alertsAPI = {
    // 获取报警规则列表
    listRules: () => apiRequest('/alerts/rules/'),

    // 创建报警规则
    createRule: (data) => apiRequest('/alerts/rules/', {
        method: 'POST',
        body: JSON.stringify(data),
    }),

    // 更新报警规则
    updateRule: (id, data) => apiRequest(`/alerts/rules/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
    }),

    // 删除报警规则
    deleteRule: (id) => apiRequest(`/alerts/rules/${id}/`, {
        method: 'DELETE',
    }),

    // 获取报警记录
    listRecords: (params) => {
        const queryString = params ? `?${new URLSearchParams(params)}` : '';
        return apiRequest(`/alerts/records/${queryString}`);
    },

    // 确认报警
    acknowledge: (id, notes = '') => apiRequest(`/alerts/records/${id}/acknowledge/`, {
        method: 'POST',
        body: JSON.stringify({ notes }),
    }),

    // 解决报警
    resolve: (id, notes = '') => apiRequest(`/alerts/records/${id}/resolve/`, {
        method: 'POST',
        body: JSON.stringify({ notes }),
    }),

    // 获取报警统计
    statistics: (range = '7d') => apiRequest(`/alerts/statistics/?range=${range}`),

    // 获取待处理报警
    pending: () => apiRequest('/alerts/records/pending/'),
};

// 工具函数
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

function formatValue(value, unit = '') {
    if (value === null || value === undefined) return '-';
    return `${value.toFixed(1)} ${unit}`;
}

// 显示通知
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);

    // 3秒后自动关闭
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// 检查登录状态
function isLoggedIn() {
    return !!authToken;
}

// 更新认证UI
function updateAuthUI() {
    const userMenu = document.getElementById('userMenu');
    const loginMenu = document.getElementById('loginMenu');
    const usernameSpan = document.getElementById('username');

    if (authToken) {
        userMenu.style.display = 'block';
        loginMenu.style.display = 'none';
        // 获取用户信息
        authAPI.profile().then(data => {
            usernameSpan.textContent = data.username;
        }).catch(() => {
            usernameSpan.textContent = '用户';
        });
    } else {
        userMenu.style.display = 'none';
        loginMenu.style.display = 'block';
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    updateAuthUI();
});
