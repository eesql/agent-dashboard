"""数据聚合服务"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.agent import Agent
from app.models.session import Session
from app.models.tool_call import ToolCall
from app.models.metric import Metric
from app.services.openclaw_parser import parse_session_daily_stats, find_session_file
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List
from sqlalchemy.orm import selectinload
import logging
import os
import json
import glob

logger = logging.getLogger(__name__)


class DataAggregator:
    """数据聚合器"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def aggregate_metrics(
        self,
        agent_id: Optional[str] = None,
        target_date: Optional[date] = None,
    ) -> Metric:
        """聚合统计数据 - 从 session jsonl 文件统计每日实际增量
        
        request_count: 统计实际的 API 请求数（每次 assistant 响应算一次请求）
        token_count: 统计当日实际 token 使用量
        """
        if target_date is None:
            target_date = date.today()
        
        # 从 jsonl 文件统计每日实际增量
        token_count = 0
        request_count = 0
        input_tokens = 0
        output_tokens = 0
        
        # 获取所有 sessions.json 文件
        sessions_json_paths = glob.glob(os.path.expanduser('~/.openclaw/agents/*/sessions/sessions.json'))
        
        for sessions_json_path in sessions_json_paths:
            try:
                with open(sessions_json_path, 'r', encoding='utf-8') as f:
                    sessions_map = json.load(f)
                
                for session_key, session_info in sessions_map.items():
                    # 如果指定了 agent_id，只统计该 agent
                    if agent_id:
                        parts = session_key.split(':')
                        if len(parts) < 2 or parts[1] != agent_id:
                            continue
                    
                    # 获取 session 文件路径
                    session_file = session_info.get('sessionFile')
                    if not session_file or not os.path.exists(session_file):
                        continue
                    
                    # 统计指定日期的增量
                    daily_stats = parse_session_daily_stats(session_file, target_date)
                    token_count += daily_stats.get('token_count', 0)
                    request_count += daily_stats.get('request_count', 0)
                    input_tokens += daily_stats.get('input_tokens', 0)
                    output_tokens += daily_stats.get('output_tokens', 0)
                    
            except Exception as e:
                logger.debug(f"Failed to process {sessions_json_path}: {e}")
                continue
        
        # 估算成本（假设 $0.002/1K tokens）
        estimated_cost = token_count * 0.000002
        
        logger.info(f"Daily stats for {target_date}: tokens={token_count}, requests={request_count}")
        
        # 创建或更新 Metric 记录
        metric_query = select(Metric).where(
            and_(
                Metric.agent_id == agent_id,
                Metric.date == target_date,
            )
        )
        metric = (await self.db.execute(metric_query)).scalar_one_or_none()
        
        if metric:
            metric.token_count = token_count
            metric.request_count = request_count
            metric.estimated_cost = estimated_cost
        else:
            metric = Metric(
                agent_id=agent_id,
                date=target_date,
                token_count=token_count,
                request_count=request_count,
                avg_response_time_ms=0,
                estimated_cost=estimated_cost,
            )
            self.db.add(metric)
        
        await self.db.commit()
        logger.info(f"Aggregated metrics for {target_date}: tokens={token_count}, requests={request_count}")
        return metric
    
    async def get_metrics_summary(self) -> Dict:
        """获取统计汇总"""
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)
        
        # 今日统计
        today_query = select(
            func.sum(Metric.token_count),
            func.sum(Metric.request_count),
            func.sum(Metric.estimated_cost),
        ).where(Metric.date == today)
        today_result = await self.db.execute(today_query)
        today_row = today_result.first()
        
        # 本周统计
        week_query = select(
            func.sum(Metric.token_count),
            func.sum(Metric.request_count),
            func.sum(Metric.estimated_cost),
        ).where(Metric.date >= start_of_week)
        week_result = await self.db.execute(week_query)
        week_row = week_result.first()
        
        # 本月统计
        month_query = select(
            func.sum(Metric.token_count),
            func.sum(Metric.request_count),
            func.sum(Metric.estimated_cost),
        ).where(Metric.date >= start_of_month)
        month_result = await self.db.execute(month_query)
        month_row = month_result.first()
        
        # Agent 统计
        agents_query = select(
            func.count(Agent.id),
            func.count(Agent.id).filter(Agent.status.in_(["online", "busy"])),
        )
        agents_result = await self.db.execute(agents_query)
        agents_row = agents_result.first()
        
        return {
            "today": {
                "agent_id": None,
                "date": date.today(),
                "token_count": today_row[0] or 0,
                "request_count": today_row[1] or 0,
                "avg_response_time_ms": 0,
                "estimated_cost": float(today_row[2] or 0),
            },
            "this_week": {
                "token_count": week_row[0] or 0,
                "request_count": week_row[1] or 0,
                "estimated_cost": float(week_row[2] or 0),
            },
            "this_month": {
                "token_count": month_row[0] or 0,
                "request_count": month_row[1] or 0,
                "estimated_cost": float(month_row[2] or 0),
            },
            "total_agents": agents_row[0] or 0,
            "active_agents": agents_row[1] or 0,
        }
    
    async def get_trend_data(
        self,
        days: int = 7,
        agent_id: Optional[str] = None,
    ) -> List[Dict]:
        """获取趋势数据（过去 N 天）"""
        today = date.today()
        start_date = today - timedelta(days=days - 1)
        
        # 查询指定日期范围内的数据
        query = select(
            Metric.date,
            func.sum(Metric.token_count).label("token_count"),
            func.sum(Metric.request_count).label("request_count"),
            func.sum(Metric.estimated_cost).label("estimated_cost"),
        ).where(
            and_(
                Metric.date >= start_date,
                Metric.date <= today,
            )
        )
        
        if agent_id:
            query = query.where(Metric.agent_id == agent_id)
        
        query = query.group_by(Metric.date).order_by(Metric.date)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        # 构建完整的数据（包括没有数据的日期）
        trend_data = []
        date_map = {row.date: row for row in rows}
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            row = date_map.get(current_date)
            
            if row:
                trend_data.append({
                    "date": current_date.isoformat(),
                    "token_count": row.token_count or 0,
                    "request_count": row.request_count or 0,
                    "estimated_cost": float(row.estimated_cost or 0),
                })
            else:
                trend_data.append({
                    "date": current_date.isoformat(),
                    "token_count": 0,
                    "request_count": 0,
                    "estimated_cost": 0.0,
                })
        
        return trend_data
    
    async def get_tool_calls_by_session(
        self,
        session_id: str,
        limit: int = 50,
    ) -> list:
        """获取会话的工具调用记录"""
        query = select(ToolCall).where(
            ToolCall.session_id == session_id
        ).order_by(
            ToolCall.timestamp.desc()
        ).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
