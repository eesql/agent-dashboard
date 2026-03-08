"""Session 会话模型"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from datetime import datetime


class Session(Base):
    """会话记录表"""
    __tablename__ = "sessions"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    agent_id: Mapped[str] = mapped_column(String, ForeignKey("agents.id"), nullable=True)
    label: Mapped[str] = mapped_column(String, nullable=True)
    kind: Mapped[str] = mapped_column(String, nullable=True)  # subagent, acp, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    last_activity: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # 关系
    agent = relationship("Agent", backref="sessions")
    
    def __repr__(self) -> str:
        return f"<Session(id={self.id}, agent_id={self.agent_id})>"
