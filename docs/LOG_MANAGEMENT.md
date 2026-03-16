# 日志管理文档

## 概述

Agent Dashboard 采用日志轮转和压缩机制，确保日志文件不会无限增长导致磁盘空间被占满。

## 日志配置

后端使用 Python 的 `RotatingFileHandler` 实现日志轮转，配置参数如下：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `log_level` | INFO | 日志级别 |
| `log_dir` | ./logs | 日志目录 |
| `log_max_bytes` | 50 MB | 单个日志文件最大大小 |
| `log_backup_count` | 7 | 保留的日志文件数量 |
| `compress_logs` | True | 是否压缩旧日志 |

## 日志文件说明

```
backend/logs/
├── backend.log       # 当前日志文件
├── backend.log.1     # 最近一次轮转的日志（未压缩）
├── backend.log.2.gz  # 压缩的历史日志
├── backend.log.3.gz  # 压缩的历史日志
└── ...               # 最多保留 7 个备份
```

## 手动清理脚本

```bash
# 清理 agent-dashboard 项目的过期日志
./scripts/cleanup-logs.sh
```

## 配置调整

通过环境变量或 `.env` 文件调整：

```bash
LOG_LEVEL=INFO
LOG_MAX_BYTES=52428800  # 50MB
LOG_BACKUP_COUNT=7
COMPRESS_LOGS=true
```
