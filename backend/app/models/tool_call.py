"""Tool Call 工具调用模型"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from datetime import datetime


class ToolCall(Base):
    """工具调用日志表"""
    __tablename__ = "tool_calls"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=True)
    tool_name: Mapped[str] = mapped_column(String, nullable=False)
    tool_args: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    result_summary: Mapped[str] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # 关系
    session = relationship("Session", backref="tool_calls")
    
    def __repr__(self) -> str:
        return f"<ToolCall(id={self.id}, tool={self.tool_name})>"
