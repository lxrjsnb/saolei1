# 物联网环境监测系统

一个基于Django框架的物联网环境监测系统，支持多种传感器数据的实时采集、监测、报警和数据导出功能。

## 功能特性

### 核心功能
- **设备管理**：支持添加、编辑、删除监测设备，管理设备配置
- **数据采集**：支持温度、湿度、光照强度、PM2.5、CO2等多种传感器数据
- **实时监测**：WebSocket实时数据推送，仪表盘可视化展示
- **历史数据查询**：按时间范围查询历史数据，支持分页
- **数据统计**：按小时/天统计数据，提供平均值、最大值、最小值等
- **数据导出**：支持Excel、CSV格式导出

### 报警系统
- **报警规则**：支持自定义报警规则（阈值、条件、严重程度）
- **报警记录**：记录所有报警事件，支持确认和解决操作
- **报警通知**：支持邮件、短信、Webhook等多种通知方式
- **报警统计**：按时间范围、设备、严重程度统计报警数据

### 用户管理
- 用户注册、登录、登出
- Token认证
- 权限控制

## 技术栈

### 后端
- Django 6.0
- Django REST Framework
- Celery（异步任务）
- Channels（WebSocket）
- MySQL（数据库）
- Redis（缓存、消息队列）

### 前端
- Vue 3 (Composition API)
- Vite（构建工具）
- Element Plus（UI组件库）
- Vue Router 4（路由）
- Pinia（状态管理）
- ECharts（图表）

## 系统架构

```
物联网环境监测系统
├── backend/                  # Django后端
│   ├── devices/              # 设备管理模块
│   ├── monitoring/           # 数据监测模块
│   ├── alerts/               # 报警管理模块
│   ├── users/                # 用户管理模块
│   └── iot_monitor/          # 项目配置
└── frontend/                 # Vue3前端
    ├── src/
    │   ├── api/              # API接口
    │   ├── views/            # 页面组件
    │   ├── router/           # 路由配置
    │   └── stores/           # 状态管理
    └── package.json
```

## 数据库模型

### 设备模块 (devices)
- Device：设备信息
- DeviceConfig：设备配置

### 监测模块 (monitoring)
- SensorData：传感器数据
- DataSummary：数据汇总

### 报警模块 (alerts)
- AlertRule：报警规则
- AlertRecord：报警记录
- NotificationConfig：通知配置

## 安装部署

### 1. 环境准备

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r backend/requirements.txt
```

### 2. 数据库配置

在 `backend/iot_monitor/settings.py` 中配置MySQL数据库：

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "iot_monitor",
        "USER": "root",
        "PASSWORD": "your_password",
        "HOST": "localhost",
        "PORT": "3306",
    }
}
```

创建数据库：

```sql
CREATE DATABASE iot_monitor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 初始化数据库

```bash
# 进入backend目录
cd backend

# 执行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 创建必要的目录
mkdir -p logs staticfiles media
```

### 4. 启动服务

#### 后端服务
```bash
# 进入backend目录
cd backend

# 启动Django开发服务器
python manage.py runserver

# 启动Celery worker（另开一个终端）
celery -A iot_monitor worker -l info

# 启动Celery beat（定时任务，可选）
celery -A iot_monitor beat -l info
```

#### 前端服务
```bash
# 进入前端目录
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

### 5. 访问系统

- 前端界面：http://localhost:5173/
- 后端API：http://localhost:8000/api/
- 管理后台：http://localhost:8000/admin/

## API接口

### 用户认证
- POST `/api/auth/register/` - 用户注册
- POST `/api/auth/login/` - 用户登录
- POST `/api/auth/logout/` - 用户登出
- GET `/api/auth/profile/` - 获取用户信息

### 设备管理
- GET `/api/devices/devices/` - 获取设备列表
- POST `/api/devices/devices/` - 创建设备
- GET `/api/devices/devices/{id}/` - 获取设备详情
- PUT `/api/devices/devices/{id}/` - 更新设备
- DELETE `/api/devices/devices/{id}/` - 删除设备
- GET `/api/devices/devices/{id}/latest_data/` - 获取最新数据

### 数据监测
- GET `/api/monitoring/data/latest/` - 获取所有设备最新数据
- POST `/api/monitoring/upload/` - 上报传感器数据
- GET `/api/monitoring/query/` - 查询历史数据
- GET `/api/monitoring/realtime/{device_id}/` - 获取实时数据
- GET `/api/monitoring/statistics/{device_id}/` - 获取统计数据
- GET `/api/monitoring/export/` - 导出数据

### 报警管理
- GET `/api/alerts/rules/` - 获取报警规则列表
- POST `/api/alerts/rules/` - 创建报警规则
- GET `/api/alerts/records/` - 获取报警记录
- POST `/api/alerts/records/{id}/acknowledge/` - 确认报警
- POST `/api/alerts/records/{id}/resolve/` - 解决报警
- GET `/api/alerts/statistics/` - 获取报警统计

## 数据上报示例

### HTTP POST 上报数据

```bash
curl -X POST http://localhost:8000/api/monitoring/upload/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device": 1,
    "temperature": 25.5,
    "humidity": 60.2,
    "light_intensity": 500,
    "pm25": 35,
    "co2": 450
  }'
```

### Python 上报示例

```python
import requests

url = "http://localhost:8000/api/monitoring/upload/"
headers = {
    "Authorization": "Token YOUR_TOKEN",
    "Content-Type": "application/json"
}
data = {
    "device": 1,
    "temperature": 25.5,
    "humidity": 60.2,
    "pm25": 35
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

## 开发说明

### 目录结构
```
sg/
├── alerts/              # 报警模块
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tasks.py
├── devices/             # 设备模块
├── monitoring/          # 监测模块
├── users/               # 用户模块
├── iot_monitor/         # 项目配置
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── asgi.py
├── templates/           # HTML模板
├── static/              # 静态资源
├── manage.py
└── requirements.txt
```

### 扩展开发
1. 添加新的传感器类型：在 `backend/monitoring/models.py` 的 `SensorData` 模型中添加字段
2. 自定义报警规则：在 `backend/alerts/models.py` 的 `AlertRule` 模型中扩展
3. 添加新的通知方式：在 `backend/alerts/tasks.py` 的 `send_alert_notifications` 任务中实现
4. 前端扩展：在 `frontend/src/views/` 中添加新页面组件
5. API扩展：在 `frontend/src/api/` 中添加API调用函数

### 前端开发
前端项目位于 `frontend/` 目录，是一个独立的Vue3应用：

- **添加新页面**: 在 `frontend/src/views/` 创建新的 `.vue` 文件
- **添加路由**: 在 `frontend/src/router/index.js` 中添加路由配置
- **API调用**: 在 `frontend/src/api/` 中添加API接口函数
- **状态管理**: 在 `frontend/src/stores/` 中添加Pinia store

### 后端开发
后端项目位于 `backend/` 目录，包含所有Django应用：

- **添加新模型**: 在对应应用的 `models.py` 中定义模型
- **创建API**: 在对应应用的 `views.py` 和 `serializers.py` 中实现
- **注册路由**: 在对应应用的 `urls.py` 和 `backend/iot_monitor/urls.py` 中配置
- **数据库迁移**: 在 `backend/` 目录下运行 `python manage.py makemigrations`

## 常见问题

### 1. 数据库连接失败
- 检查MySQL服务是否启动
- 检查数据库配置是否正确
- 确保数据库已创建

### 2. Celery任务不执行
- 确保Redis服务已启动
- 检查Celery worker是否运行
- 查看Celery日志

### 3. WebSocket连接失败
- 确保channels配置正确
- 检查Redis服务
- 查看asgi.py配置

## 许可证

MIT License

## 作者

物联网环境监测系统开发团队

## 更新日志

### v1.0.0 (2024-01-13)
- 初始版本发布
- 实现设备管理功能
- 实现数据采集和监测功能
- 实现报警系统
- 实现数据导出功能
