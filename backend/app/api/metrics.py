"""Metrics 相关 API 端点"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.data_aggregator import DataAggregator
from app.services.agent_monitor import AgentMonitor
from app.schemas.metrics import MetricsResponse, MetricsSummary

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/summary", response_model=MetricsSummary)
async def get_metrics_summary(db: AsyncSession = Depends(get_db)):
    """获取统计汇总"""
    aggregator = DataAggregator(db)
    summary = await aggregator.get_metrics_summary()
    return summary


@router.get("/today", response_model=MetricsResponse)
async def get_today_metrics(db: AsyncSession = Depends(get_db)):
    """获取今日统计"""
    aggregator = DataAggregator(db)
    metric = await aggregator.aggregate_metrics()
    return metric
