"""Metric 统计数据模型"""
from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from datetime import datetime, date


class Metric(Base):
    """统计数据表"""
    __tablename__ = "metrics"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[str] = mapped_column(String, ForeignKey("agents.id"), nullable=True)
    date: Mapped[date] = mapped_column(Date, default=date.today())
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    request_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_response_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # 关系
    agent = relationship("Agent", backref="metrics")
    
    def __repr__(self) -> str:
        return f"<Metric(agent_id={self.agent_id}, date={self.date})>"
