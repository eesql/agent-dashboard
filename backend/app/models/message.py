"""Message 消息模型"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from datetime import datetime


class Message(Base):
    """消息记录表"""
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String, nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=True)  # 文本内容
    content_json: Mapped[dict] = mapped_column(JSON, nullable=True)  # 结构化内容（支持 toolCall/toolResult）
    tool_call_id: Mapped[str] = mapped_column(String, nullable=True, index=True)  # 工具调用 ID
    tool_name: Mapped[str] = mapped_column(String, nullable=True, index=True)  # 工具名称
    tool_args: Mapped[dict] = mapped_column(JSON, nullable=True)  # 工具参数
    tool_result: Mapped[str] = mapped_column(Text, nullable=True)  # 工具执行结果
    is_tool_call: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_tool_result: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now(), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # 关系
    session = relationship("Session", backref="messages")
    
    def __repr__(self) -> str:
        return f"<Message(id={self.id}, session_id={self.session_id}, role={self.role})>"
