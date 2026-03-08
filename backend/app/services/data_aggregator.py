"""数据聚合服务"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.agent import Agent
from app.models.session import Session
from app.models.tool_call import ToolCall
from app.models.metric import Metric
from datetime import datetime, date, timedelta
from typing import Optional, Dict
import logging

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
        """聚合统计数据"""
        if target_date is None:
            target_date = date.today()
        
        # 计算当天的数据
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        # 查询工具调用统计
        query = select(
            func.count(ToolCall.id).label("request_count"),
            func.avg(ToolCall.duration_ms).label("avg_duration"),
        ).where(
            and_(
                ToolCall.timestamp >= start_datetime,
                ToolCall.timestamp <= end_datetime,
            )
        )
        
        if agent_id:
            # 需要通过 session 关联 agent
            query = query.join(Session).where(Session.agent_id == agent_id)
        
        result = await self.db.execute(query)
        row = result.first()
        
        request_count = row.request_count or 0
        avg_duration = int(row.avg_duration or 0)
        
        # 估算 token 和成本（简化版，实际需要从 API 获取）
        token_count = request_count * 1000  # 假设每次请求平均 1000 tokens
        estimated_cost = token_count * 0.000002  # 假设 $0.002/1K tokens
        
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
            metric.avg_response_time_ms = avg_duration
            metric.estimated_cost = estimated_cost
        else:
            metric = Metric(
                agent_id=agent_id,
                date=target_date,
                token_count=token_count,
                request_count=request_count,
                avg_response_time_ms=avg_duration,
                estimated_cost=estimated_cost,
            )
            self.db.add(metric)
        
        await self.db.flush()
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
