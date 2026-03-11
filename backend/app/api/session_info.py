"""Session Info API - 获取会话详细信息用于 Dashboard 展示"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.db.database import get_db
from app.services.openclaw_parser import parse_openclaw_sessions
from app.models.session import Session
from sqlalchemy import select
from datetime import datetime
import os
import json

router = APIRouter(prefix="/api/session-info", tags=["session-info"])


def get_session_status(last_seen_str: str) -> str:
    """根据最后活动时间判断会话状态"""
    try:
        if last_seen_str:
            last_seen = datetime.fromisoformat(last_seen_str)
            diff = (datetime.now() - last_seen).total_seconds()
            if diff < 300:  # 5 分钟
                return "online"
            elif diff < 3600:  # 1 小时
                return "busy"
    except:
        pass
    return "offline"


def extract_session_info(session_data: dict) -> dict:
    """从 openclaw session 数据提取会话信息"""
    session_id = session_data.get("id", session_data.get("key", ""))
    
    # 解析 session key: agent:main:feishu:direct:xxx
    parts = session_id.split(":")
    agent_id = parts[1] if len(parts) > 1 else "unknown"
    channel = parts[2] if len(parts) > 2 else "unknown"
    
    # 渠道名称映射
    channel_names = {
        'qqbot': 'QQ Bot',
        'feishu': '飞书',
        'telegram': 'Telegram',
        'discord': 'Discord',
        'wecom': '企业微信',
        'slack': 'Slack',
        'direct': 'Direct',
    }
    channel_name = channel_names.get(channel, channel)
    
    # 获取 token 信息
    input_tokens = session_data.get("inputTokens", 0) or 0
    output_tokens = session_data.get("outputTokens", 0) or 0
    total_tokens = session_data.get("totalTokens", 0) or 0
    
    # 计算上下文使用率（假设默认上下文窗口为 200K）
    context_limit = 200000  # 可从模型配置获取
    context_usage_percent = round((total_tokens / context_limit) * 100, 1) if context_limit > 0 else 0
    
    # 获取状态
    last_seen = session_data.get("last_seen", "")
    status = get_session_status(last_seen)
    
    return {
        "id": session_id,
        "agent_id": agent_id,
        "agent_name": f"Agent {agent_id}" if agent_id != "main" else "Main Agent",
        "channel": channel_name,
        "status": status,
        "model": session_data.get("model", "unknown"),
        "thinking_level": session_data.get("thinkingLevel", "off"),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "context_limit": context_limit,
        "context_usage_percent": context_usage_percent,
        "last_activity": last_seen,
        "created_at": session_data.get("created_at", ""),
    }


@router.get("")
async def get_session_infos(
    agent_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """获取所有会话的详细信息，用于 Dashboard 卡片展示"""
    
    # 从 openclaw sessions 获取实时数据
    sessions_data = parse_openclaw_sessions()
    
    result = []
    for session_data in sessions_data:
        info = extract_session_info(session_data)
        
        # 筛选
        if agent_id and info["agent_id"] != agent_id:
            continue
        if status and info["status"] != status:
            continue
        
        result.append(info)
    
    # 按最后活动时间排序
    result.sort(key=lambda x: x.get("last_activity", ""), reverse=True)
    
    return result[:limit]


@router.get("/summary")
async def get_session_summary(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """获取会话统计摘要"""
    sessions_data = parse_openclaw_sessions()
    
    total = len(sessions_data)
    online = 0
    busy = 0
    offline = 0
    
    total_tokens = 0
    by_channel = {}
    by_agent = {}
    
    for session_data in sessions_data:
        info = extract_session_info(session_data)
        
        # 状态统计
        if info["status"] == "online":
            online += 1
        elif info["status"] == "busy":
            busy += 1
        else:
            offline += 1
        
        # Token 统计
        total_tokens += info["total_tokens"]
        
        # 按渠道统计
        channel = info["channel"]
        by_channel[channel] = by_channel.get(channel, 0) + 1
        
        # 按 agent 统计
        agent = info["agent_id"]
        by_agent[agent] = by_agent.get(agent, 0) + 1
    
    return {
        "total": total,
        "online": online,
        "busy": busy,
        "offline": offline,
        "total_tokens": total_tokens,
        "by_channel": by_channel,
        "by_agent": by_agent,
    }
