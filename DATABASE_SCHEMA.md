# 数据库模型说明

## 概述

物联网环境监测系统使用MySQL数据库，包含11个核心数据表，涵盖设备管理、数据监测、报警管理和用户管理四大模块。

## 数据表结构

### 1. 设备管理模块 (devices)

#### 1.1 devices (设备表)
存储物联网设备的基本信息和硬件配置。

| 字段名 | 类型 | 说明 | 备注 |
|--------|------|------|------|
| id | BigAuto | 主键 | 自增ID |
| name | String(100) | 设备名称 | |
| device_id | String(50) | 设备ID | 唯一索引 |
| device_type | String(20) | 设备类型 | temperature/humidity/light/pm25/co2/composite |
| location | String(200) | 安装位置 | |
| status | String(20) | 设备状态 | online/offline/maintenance/error |
| description | Text | 设备描述 | 可为空 |
| ip_address | GenericIPAddress | IP地址 | 可为空 |
| mac_address | String(17) | MAC地址 | 可为空 |
| firmware_version | String(50) | 固件版本 | 可为空 |
| manufacturer | String(100) | 制造商 | 可为空 |
| model | String(100) | 型号 | 可为空 |
| serial_number | String(100) | 序列号 | 可为空 |
| latitude | Decimal(10,7) | 纬度 | 可为空 |
| longitude | Decimal(10,7) | 经度 | 可为空 |
| altitude | Float | 海拔(米) | 可为空 |
| install_date | Date | 安装日期 | 可为空 |
| warranty_date | Date | 保修期至 | 可为空 |
| owner | ForeignKey(FK) | 所属用户 | 关联auth.User |
| is_active | Boolean | 是否启用 | 默认True |
| created_at | DateTime | 创建时间 | 自动生成 |
| updated_at | DateTime | 更新时间 | 自动更新 |
| last_active | DateTime | 最后活跃时间 | 可为空 |

**索引:**
- device_id (唯一索引)
- status
- device_type
- owner

#### 1.2 device_configs (设备配置表)
存储设备的运行配置参数。

| 字段名 | 类型 | 说明 | 备注 |
|--------|------|------|------|
| id | BigAuto | 主键 | 自增ID |
| device | OneToOne(FK) | 设备 | 关联devices |
| collect_interval | Integer | 采集间隔(秒) | 默认60 |
| enable_alert | Boolean | 启用报警 | 默认True |
| data_retention_days | Integer | 数据保留天数 | 默认90 |
| auto_cleanup | Boolean | 自动清理过期数据 | 默认False |
| extra_config | JSON | 额外配置 | 存储扩展配置 |
| created_at | DateTime | 创建时间 | 自动生成 |
| updated_at | DateTime | 更新时间 | 自动更新 |

#### 1.3 device_maintenance (设备维护记录表)
记录设备的维护历史。

| 字段名 | 类型 | 说明 | 备注 |
|--------|------|------|------|
| id | BigAuto | 主键 | 自增ID |
| device | ForeignKey(FK) | 设备 | 关联devices |
| maintenance_type | String(20) | 维护类型 | routine/repair/upgrade/calibration/replacement |
| description | Text | 维护描述 | |
| scheduled_date | DateTime | 计划时间 | |
| completed_date | DateTime | 完成时间 | 可为空 |
| status | String(20) | 状态 | scheduled/in_progress/completed/cancelled |
| technician | ForeignKey(FK) | 技术人员 | 关联auth.User，可为空 |
| cost | Decimal(10,2) | 费用 | 可为空 |
| notes | Text | 备注 | 可为空 |
| created_at | DateTime | 创建时间 | 自动生成 |

### 2. 数据监测模块 (monitoring)

#### 2.1 sensor_data (传感器数据表)
存储设备上报的传感器数据。

| 字段名 | 类型 | 说明 | 备注 |
|--------|------|------|------|
| id | BigAuto | 主键 | 自增ID |
| device | ForeignKey(FK) | 设备 | 关联devices |
| temperature | Float | 温度(℃) | 可为空 |
| humidity | Float | 湿度(%) | 可为空 |
| pressure | Float | 气压(hPa) | 可为空 |
| light_intensity | Float | 光照强度(lux) | 可为空 |
| uv_index | Float | 紫外线指数 | 可为空 |
| pm25 | Float | PM2.5(μg/m³) | 可为空 |
| pm10 | Float | PM10(μg/m³) | 可为空 |
| co2 | Float | CO2浓度(ppm) | 可为空 |
| voc | Float | VOC浓度(ppb) | 可为空 |
| o3 | Float | O3浓度(ppb) | 可为空 |
| noise_level | Float | 噪音水平(dB) | 可为空 |
| wind_speed | Float | 风速(m/s) | 可为空 |
| wind_direction | Float | 风向(度) | 可为空 |
| rainfall | Float | 降雨量(mm) | 可为空 |
| battery_level | Integer | 电池电量(%) | 可为空 |
| signal_strength | Integer | 信号强度(dBm) | 可为空 |
| timestamp | DateTime | 采集时间 | 自动生成，索引 |
| is_valid | Boolean | 数据是否有效 | 默认True |
| error_message | Text | 错误信息 | 可为空 |

**索引:**
- device, -timestamp (复合索引)
- timestamp
- is_valid

#### 2.2 data_summaries (数据汇总表)
按小时/天/周/月汇总的统计数据。

| 字段名 | 类型 | 说明 | 备注 |
|--------|------|------|------|
| id | BigAuto | 主键 | 自增ID |
| device | ForeignKey(FK) | 设备 | 关联devices |
| summary_type | String(10) | 汇总类型 | hour/day/week/month |
| start_time | DateTime | 开始时间 | |
| end_time | DateTime | 结束时间 | |
| temp_avg | Float | 平均温度 | 可为空 |
| temp_max | Float | 最高温度 | 可为空 |
| temp_min | Float | 最低温度 | 可为空 |
| humidity_avg | Float | 平均湿度 | 可为空 |
| humidity_max | Float | 最高湿度 | 可为空 |
| humidity_min | Float | 最低湿度 | 可为空 |
| pm25_avg | Float | 平均PM2.5 | 可为空 |
| pm25_max | Float | 最高PM2.5 | 可为空 |
| co2_avg | Float | 平均CO2 | 可为空 |
| co2_max | Float | 最高CO2 | 可为空 |
| data_count | Integer | 数据点数量 | 默认0 |
| created_at | DateTime | 创建时间 | 自动生成 |

**唯一约束:**
- device + summary_type + start_time

#### 2.3 data_exports (数据导出记录表)
记录数据导出操作的历史。

| 字段名 | 类型 | 说明 | 备注 |
|--------|------|------|------|
| id | BigAuto | 主键 | 自增ID |
| user | ForeignKey(FK) | 用户 | 关联auth.User |
| device | ForeignKey(FK) | 设备 | 关联devices |
| export_type | String(10) | 导出类型 | excel/csv/json |
| start_time | DateTime | 开始时间 | |
| end_time | DateTime | 结束时间 | |
| status | String(20) | 状态 | pending/processing/completed/failed |
| file_path | String(255) | 文件路径 | 可为空 |
| file_size | Integer | 文件大小(字节) | 可为空 |
| row_count | Integer | 数据行数 | 可为空 |
| created_at | DateTime | 创建时间 | 自动生成 |
| completed_at | DateTime | 完成时间 | 可为空 |
| error_message | Text | 错误信息 | 可为空 |

### 3. 报警管理模块 (alerts)

#### 3.1 alert_rules (报警规则表)
定义设备的报警规则。

| 字段名 | 类型 | 说明 | 备注 |
|--------|------|------|------|
| id | BigAuto | 主键 | 自增ID |
| name | String(100) | 规则名称 | |
| device | ForeignKey(FK) | 设备 | 关联devices |
| sensor_type | String(20) | 传感器类型 | |
| condition | String(20) | 条件 | greater_than/less_than/equal/not_equal/between/outside |
| threshold | Float | 阈值 | 可为空 |
| threshold_min | Float | 最小阈值 | 可为空 |
| threshold_max | Float | 最大阈值 | 可为空 |
| severity | String(20) | 严重程度 | info/low/medium/high/critical |
| enabled | Boolean | 是否启用 | 默认True |
| description | Text | 描述 | 可为空 |
| cooldown_minutes | Integer | 冷却时间(分钟) | 默认5 |
| repeat_alert | Boolean | 重复报警 | 默认False |
| repeat_interval_minutes | Integer | 重复间隔(分钟) | 默认30 |
| created_by | ForeignKey(FK) | 创建人 | 关联auth.User |
| created_at | DateTime | 创建时间 | 自动生成 |
| updated_at | DateTime | 更新时间 | 自动更新 |

**索引:**
- device, enabled (复合索引)

#### 3.2 alert_records (报警记录表)
记录触发的报警事件。

| 字段名 | 类型 | 说明 | 备注 |
|--------|------|------|------|
| id | BigAuto | 主键 | 自增ID |
| rule | ForeignKey(FK) | 报警规则 | 关联alert_rules |
| device | ForeignKey(FK) | 设备 | 关联devices |
| status | String(20) | 状态 | pending/acknowledged/resolved/false_alarm/auto_resolved |
| message | Text | 报警消息 | |
| current_value | Float | 当前值 | |
| severity | String(20) | 严重程度 | |
| triggered_at | DateTime | 触发时间 | 自动生成，索引 |
| acknowledged_at | DateTime | 确认时间 | 可为空 |
| acknowledged_by | ForeignKey(FK) | 确认人 | 关联auth.User，可为空 |
| resolved_at | DateTime | 解决时间 | 可为空 |
| resolved_by | ForeignKey(FK) | 解决人 | 关联auth.User，可为空 |
| notes | Text | 备注 | 可为空 |
| recovery_value | Float | 恢复值 | 可为空 |
| recovery_time | DurationField | 恢复耗时 | 可为空 |
| notification_sent | Boolean | 通知已发送 | 默认False |
| notification_count | Integer | 通知次数 | 默认0 |

**索引:**
- device, -triggered_at (复合索引)
- status, -triggered_at (复合索引)
- severity, -triggered_at (复合索引)

#### 3.3 notification_configs (通知配置表)
用户的通知偏好配置。

| 字段名 | 类型 | 说明 | 备注 |
|--------|------|------|------|
| id | BigAuto | 主键 | 自增ID |
| user | ForeignKey(FK) | 用户 | 关联auth.User |
| notification_type | String(20) | 通知类型 | email/sms/webhook/wechat/dingtalk/feishu |
| enabled | Boolean | 是否启用 | 默认True |
| config | JSON | 配置信息 | 存储具体配置参数 |
| min_severity | String(20) | 最低严重程度 | 默认medium |
| notify_24h | Boolean | 24小时通知 | 默认True |
| quiet_hours_start | Time | 免打扰开始时间 | 可为空 |
| quiet_hours_end | Time | 免打扰结束时间 | 可为空 |
| created_at | DateTime | 创建时间 | 自动生成 |
| updated_at | DateTime | 更新时间 | 自动更新 |

#### 3.4 notification_logs (通知发送日志表)
记录通知发送的历史。

| 字段名 | 类型 | 说明 | 备注 |
|--------|------|------|------|
| id | BigAuto | 主键 | 自增ID |
| alert_record | ForeignKey(FK) | 报警记录 | 关联alert_records |
| notification_config | ForeignKey(FK) | 通知配置 | 关联notification_configs |
| status | String(20) | 状态 | pending/sent/failed/retrying |
| recipient | String(255) | 接收人 | |
| content | Text | 通知内容 | |
| sent_at | DateTime | 发送时间 | 可为空 |
| error_message | Text | 错误信息 | 可为空 |
| retry_count | Integer | 重试次数 | 默认0 |
| created_at | DateTime | 创建时间 | 自动生成 |

**索引:**
- alert_record, status (复合索引)
- notification_config, -created_at (复合索引)

### 4. 用户管理模块 (users)

#### 4.1 user_profiles (用户配置表)
扩展的用户配置信息。

| 字段名 | 类型 | 说明 | 备注 |
|--------|------|------|------|
| id | BigAuto | 主键 | 自增ID |
| user | OneToOne(FK) | 用户 | 关联auth.User |
| phone | String(20) | 手机号 | 可为空 |
| avatar | ImageField | 头像 | 可为空 |
| organization | String(200) | 组织/公司 | 可为空 |
| position | String(100) | 职位 | 可为空 |
| email_notification | Boolean | 邮件通知 | 默认True |
| sms_notification | Boolean | 短信通知 | 默认False |
| webhook_notification | Boolean | Webhook通知 | 默认False |
| language | String(10) | 语言 | 默认zh-hans |
| timezone | String(50) | 时区 | 默认Asia/Shanghai |
| theme | String(20) | 主题 | 默认light |
| items_per_page | Integer | 每页显示数量 | 默认20 |
| default_data_range | String(20) | 默认数据范围 | 默认24h |
| auto_refresh_interval | Integer | 自动刷新间隔(秒) | 默认30 |
| two_factor_enabled | Boolean | 启用双因素认证 | 默认False |
| last_password_change | DateTime | 上次修改密码时间 | 可为空 |
| login_notification | Boolean | 登录通知 | 默认True |
| is_active | Boolean | 是否启用 | 默认True |
| created_at | DateTime | 创建时间 | 自动生成 |
| updated_at | DateTime | 更新时间 | 自动更新 |

#### 4.2 user_activity_logs (用户活动日志表)
记录用户的操作历史。

| 字段名 | 类型 | 说明 | 备注 |
|--------|------|------|------|
| id | BigAuto | 主键 | 自增ID |
| user | ForeignKey(FK) | 用户 | 关联auth.User |
| action_type | String(50) | 操作类型 | login/logout/create_device/update_device等 |
| description | Text | 操作描述 | |
| ip_address | GenericIPAddress | IP地址 | 可为空 |
| user_agent | Text | 用户代理 | 可为空 |
| created_at | DateTime | 创建时间 | 自动生成 |

**索引:**
- user, -created_at (复合索引)
- action_type, -created_at (复合索引)

## ER图关系

```
auth.User (1) ----< (1) UserProfile
auth.User (1) ----< (*) Device
auth.User (1) ----< (*) AlertRule
auth.User (1) ----< (*) UserActivityLog

Device (1) ----< (1) DeviceConfig
Device (1) ----< (*) DeviceMaintenance
Device (1) ----< (*) SensorData
Device (1) ----< (*) DataSummary
Device (1) ----< (*) AlertRule
Device (1) ----< (*) AlertRecord
Device (1) ----< (*) DataExport

AlertRule (1) ----< (*) AlertRecord
AlertRecord (1) ----< (*) NotificationLog

NotificationConfig (1) ----< (*) NotificationLog
```

## 使用建议

1. **索引优化**: 主要查询字段都已添加索引，确保查询性能
2. **数据分区**: sensor_data表数据量大，建议按时间分区
3. **定期清理**: 利用data_retention_days配置定期清理过期数据
4. **备份策略**: 建议每日备份alert_records和sensor_data表
5. **监控**: 监控user_activity_logs表用于审计和安全分析
