"""Agent 状态模型"""
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from datetime import datetime


class Agent(Base):
    """Agent 状态表"""
    __tablename__ = "agents"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="offline")  # online, offline, busy, error
    current_task: Mapped[str] = mapped_column(String, nullable=True)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, status={self.status})>"
