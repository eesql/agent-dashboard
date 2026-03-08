"""Metrics 相关 Schema"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class MetricsResponse(BaseModel):
    """统计数据响应"""
    agent_id: Optional[str]
    date: date
    token_count: int
    request_count: int
    avg_response_time_ms: int
    estimated_cost: float
    
    class Config:
        from_attributes = True


class MetricsSummary(BaseModel):
    """统计汇总响应"""
    today: Optional[MetricsResponse] = None
    this_week: Optional[dict] = None
    this_month: Optional[dict] = None
    total_agents: int = 0
    active_agents: int = 0
