#!/bin/bash
# Agent Dashboard 日志清理脚本
# 用于清理过期的日志文件，防止磁盘空间被占满

set -e

# 配置
LOG_DIR="/root/.openclaw/workspace/agent-dashboard/backend/logs"
MAX_LOG_SIZE_MB=100
MAX_LOG_FILES=7
MAX_LOG_AGE_DAYS=30
NPM_LOGS_DIR="/root/.npm/_logs"
NPM_LOGS_MAX_AGE_DAYS=7

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Agent Dashboard 日志清理"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

# 函数：格式化大小
format_size() {
    local size=$1
    if [ $size -ge 1073741824 ]; then
        echo "$(echo "scale=2; $size/1073741824" | bc) GB"
    elif [ $size -ge 1048576 ]; then
        echo "$(echo "scale=2; $size/1048576" | bc) MB"
    elif [ $size -ge 1024 ]; then
        echo "$(echo "scale=2; $size/1024" | bc) KB"
    else
        echo "$size B"
    fi
}

# 清理 agent-dashboard 后端日志
echo ""
echo -e "${YELLOW}[1] 清理 Agent Dashboard 后端日志${NC}"
echo "日志目录: $LOG_DIR"

if [ -d "$LOG_DIR" ]; then
    # 获取当前日志总大小
    TOTAL_SIZE=$(du -sb "$LOG_DIR" 2>/dev/null | cut -f1)
    echo "当前日志总大小: $(format_size $TOTAL_SIZE)"
    
    # 列出所有日志文件
    echo ""
    echo "日志文件列表:"
    ls -lh "$LOG_DIR"/ 2>/dev/null || echo "  目录为空"
    
    # 删除超过保留天数的日志文件（除了当前日志）
    DELETED_COUNT=0
    DELETED_SIZE=0
    
    for logfile in "$LOG_DIR"/*.log.[0-9]* "$LOG_DIR"/*.log.*.gz; do
        if [ -f "$logfile" ]; then
            # 检查文件修改时间
            FILE_AGE=$(( ($(date +%s) - $(stat -c %Y "$logfile")) / 86400 ))
            
            if [ $FILE_AGE -gt $MAX_LOG_AGE_DAYS ]; then
                FILE_SIZE=$(stat -c %s "$logfile")
                echo -e "  ${RED}删除${NC}: $(basename "$logfile") ($(format_size $FILE_SIZE), ${FILE_AGE}天前)"
                rm -f "$logfile"
                DELETED_COUNT=$((DELETED_COUNT + 1))
                DELETED_SIZE=$((DELETED_SIZE + FILE_SIZE))
            fi
        fi
    done
    
    # 如果日志文件数量超过限制，删除最旧的
    LOG_COUNT=$(ls -1 "$LOG_DIR"/*.log.[0-9]* 2>/dev/null | wc -l)
    if [ $LOG_COUNT -gt $MAX_LOG_FILES ]; then
        EXCESS=$((LOG_COUNT - MAX_LOG_FILES))
        echo ""
        echo "日志文件数量 ($LOG_COUNT) 超过限制 ($MAX_LOG_FILES)，删除最旧的 $EXCESS 个文件"
        
        ls -1t "$LOG_DIR"/*.log.[0-9]* 2>/dev/null | tail -n $EXCESS | while read oldfile; do
            FILE_SIZE=$(stat -c %s "$oldfile")
            echo -e "  ${RED}删除${NC}: $(basename "$oldfile") ($(format_size $FILE_SIZE))"
            rm -f "$oldfile"
            DELETED_COUNT=$((DELETED_COUNT + 1))
            DELETED_SIZE=$((DELETED_SIZE + FILE_SIZE))
        done
    fi
    
    # 获取清理后的日志总大小
    NEW_SIZE=$(du -sb "$LOG_DIR" 2>/dev/null | cut -f1)
    echo ""
    echo -e "清理后日志总大小: $(format_size $NEW_SIZE)"
    if [ $DELETED_COUNT -gt 0 ]; then
        echo -e "删除文件数: ${RED}$DELETED_COUNT${NC}"
        echo -e "释放空间: ${GREEN}$(format_size $DELETED_SIZE)${NC}"
    fi
else
    echo "日志目录不存在"
fi

# 清理 npm 调试日志
echo ""
echo -e "${YELLOW}[2] 清理 npm 调试日志${NC}"
echo "日志目录: $NPM_LOGS_DIR"

if [ -d "$NPM_LOGS_DIR" ]; then
    NPM_TOTAL=$(du -sb "$NPM_LOGS_DIR" 2>/dev/null | cut -f1)
    echo "当前大小: $(format_size $NPM_TOTAL)"
    
    NPM_DELETED=0
    NPM_DELETED_SIZE=0
    
    for logfile in "$NPM_LOGS_DIR"/*.log; do
        if [ -f "$logfile" ]; then
            FILE_AGE=$(( ($(date +%s) - $(stat -c %Y "$logfile")) / 86400 ))
            
            if [ $FILE_AGE -gt $NPM_LOGS_MAX_AGE_DAYS ]; then
                FILE_SIZE=$(stat -c %s "$logfile")
                echo -e "  ${RED}删除${NC}: $(basename "$logfile") (${FILE_AGE}天前)"
                rm -f "$logfile"
                NPM_DELETED=$((NPM_DELETED + 1))
                NPM_DELETED_SIZE=$((NPM_DELETED_SIZE + FILE_SIZE))
            fi
        fi
    done
    
    if [ $NPM_DELETED -gt 0 ]; then
        echo -e "删除文件数: ${RED}$NPM_DELETED${NC}"
        echo -e "释放空间: ${GREEN}$(format_size $NPM_DELETED_SIZE)${NC}"
    else
        echo "无需清理"
    fi
else
    echo "npm 日志目录不存在"
fi

# 检查当前日志文件大小
echo ""
echo -e "${YELLOW}[3] 检查当前日志文件大小${NC}"

if [ -f "$LOG_DIR/backend.log" ]; then
    CURRENT_LOG_SIZE=$(stat -c %s "$LOG_DIR/backend.log")
    CURRENT_LOG_SIZE_MB=$((CURRENT_LOG_SIZE / 1048576))
    
    echo "backend.log 大小: $(format_size $CURRENT_LOG_SIZE) / ${MAX_LOG_SIZE_MB}MB"
    
    if [ $CURRENT_LOG_SIZE_MB -ge $MAX_LOG_SIZE_MB ]; then
        echo -e "${RED}警告: 当前日志文件已达到大小限制！${NC}"
        echo "建议手动触发日志轮转或增加 maxBytes 配置"
    else
        echo -e "${GREEN}正常${NC}"
    fi
fi

echo ""
echo "========================================"
echo "日志清理完成"
echo "========================================"
