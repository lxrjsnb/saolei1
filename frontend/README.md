# 物联网环境监测系统 - 前端

基于 Vue3 + Vite + Element Plus 的物联网环境监测系统前端项目。

## 技术栈

- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **UI组件库**: Element Plus
- **路由**: Vue Router 4
- **状态管理**: Pinia
- **HTTP客户端**: Axios
- **图表库**: ECharts

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API接口模块
│   │   ├── auth.js       # 用户认证API
│   │   ├── devices.js    # 设备管理API
│   │   ├── monitoring.js # 监测数据API
│   │   └── alerts.js     # 报警管理API
│   ├── assets/           # 静态资源
│   ├── router/           # 路由配置
│   │   └── index.js
│   ├── stores/           # Pinia状态管理
│   │   └── user.js       # 用户状态
│   ├── utils/            # 工具函数
│   │   └── request.js    # Axios封装
│   ├── views/            # 页面组件
│   │   ├── auth/         # 认证页面
│   │   ├── dashboard/    # 仪表盘
│   │   ├── devices/      # 设备管理
│   │   ├── monitoring/   # 数据监测
│   │   ├── alerts/       # 报警管理
│   │   └── LayoutView.vue # 布局组件
│   ├── App.vue           # 根组件
│   └── main.js           # 入口文件
├── index.html
├── vite.config.js        # Vite配置
└── package.json
```

## 功能模块

### 1. 用户认证
- 用户登录
- 用户注册
- Token认证
- 路由守卫

### 2. 仪表盘
- 设备统计
- 报警统计
- 数据统计
- 实时图表

### 3. 设备管理
- 设备列表
- 添加设备
- 编辑设备
- 删除设备
- 设备状态管理

### 4. 数据监测
- 实时数据展示
- 历史数据查询
- 数据统计
- 图表可视化
- 数据导出

### 5. 报警管理
- 报警记录
- 报警统计
- 确认报警
- 解决报警
- 严重程度分类

## 开发指南

### 安装依赖
```bash
cd frontend
npm install
```

### 启动开发服务器
```bash
npm run dev
```

访问 http://localhost:5173

### 构建生产版本
```bash
npm run build
```

### 预览生产版本
```bash
npm run preview
```

## API代理配置

开发环境下，Vite会将 `/api` 请求代理到后端服务器（http://localhost:8000）。

配置在 `vite.config.js`:
```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

## 环境变量

创建 `.env` 文件：
```
VITE_API_BASE_URL=/api
```

## 组件使用说明

### API请求
```javascript
import { getDevices, createDevice } from '@/api/devices'

// 获取设备列表
const devices = await getDevices()

// 创建设备
await createDevice({
  name: '温度传感器1',
  device_type: 'temperature',
  location: '办公室'
})
```

### 状态管理
```javascript
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
await userStore.login(username, password)
```

### 路由导航
```javascript
import { useRouter } from 'vue-router'

const router = useRouter()
router.push('/devices')
```

## License

MIT
