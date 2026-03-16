# 日志管理文档

## 概述

Agent Dashboard 采用多层日志管理策略，确保日志文件不会无限增长导致磁盘空间被占满。

## 日志配置

### 后端日志配置

后端使用 Python 的 `RotatingFileHandler` 实现日志轮转，配置参数如下：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `log_level` | INFO | 日志级别 |
| `log_dir` | ./logs | 日志目录 |
| `log_max_bytes` | 50 MB | 单个日志文件最大大小 |
| `log_backup_count` | 7 | 保留的日志文件数量 |
| `compress_logs` | True | 是否压缩旧日志 |

### 日志轮转机制

1. **自动轮转**: 当日志文件达到 `log_max_bytes` 时自动轮转
2. **自动压缩**: 轮转后的日志文件自动压缩为 `.gz` 格式
3. **自动清理**: 超过 `log_backup_count` 的旧日志文件自动删除

## 日志文件说明

```
backend/logs/
├── backend.log       # 当前日志文件
├── backend.log.1     # 最近一次轮转的日志（未压缩）
├── backend.log.2.gz  # 压缩的历史日志
├── backend.log.3.gz  # 压缩的历史日志
├── backend.log.4.gz  # 压缩的历史日志
├── backend.log.5.gz  # 压缩的历史日志
├── backend.log.6.gz  # 压缩的历史日志
└── backend.log.7.gz  # 压缩的历史日志
```

## 手动管理脚本

### 清理脚本

位于 `scripts/cleanup-logs.sh`，用于手动清理过期日志：

```bash
# 运行清理脚本
./scripts/cleanup-logs.sh
```

脚本功能：
- 清理超过 30 天的日志文件
- 限制日志文件数量不超过 7 个
- 清理超过 7 天的 npm 调试日志
- 显示日志大小统计信息

### 压缩旧日志

```bash
# 手动压缩旧的日志文件
cd backend/logs
for f in backend.log.[2-9]; do
    gzip -f "$f"
done
```

## 系统级日志轮转（可选）

如需额外的系统级日志管理，可以将 `scripts/logrotate-agent-dashboard` 配置到系统 logrotate：

```bash
# 复制配置到系统目录
sudo cp scripts/logrotate-agent-dashboard /etc/logrotate.d/agent-dashboard

# 测试配置
sudo logrotate -d /etc/logrotate.d/agent-dashboard

# 手动触发轮转
sudo logrotate -f /etc/logrotate.d/agent-dashboard
```

## 监控建议

1. **磁盘空间监控**: 设置告警，当 `/root/.openclaw/workspace/agent-dashboard/backend/logs` 目录超过 1GB 时告警
2. **日志文件数量**: 正常情况下不应超过 8 个日志文件
3. **定期检查**: 每月检查一次日志配置是否生效

## 性能影响

- 压缩旧日志： negligible（异步执行，不影响主进程）
- 日志轮转： minimal（瞬间完成）
- 磁盘空间： 预估最大占用 ~400MB（未压缩情况下约 1GB）

## 配置调整

如需调整日志配置，修改 `backend/app/config.py` 或通过环境变量：

```bash
# 环境变量配置
export LOG_LEVEL=DEBUG
export LOG_MAX_BYTES=104857600  # 100MB
export LOG_BACKUP_COUNT=10
export COMPRESS_LOGS=true
```

## 故障排查

### 日志文件过大

1. 检查日志轮转是否正常工作
2. 运行清理脚本释放空间
3. 检查日志级别是否过于详细

### 日志丢失

1. 检查 `log_backup_count` 设置是否太小
2. 检查是否有其他进程清理了日志文件

### 磁盘空间告警

1. 立即运行清理脚本
2. 检查是否有其他大型日志文件
3. 考虑增加磁盘空间或减少日志保留时间
