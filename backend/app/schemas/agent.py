"""Agent 相关 Schema"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AgentBase(BaseModel):
    """Agent 基础 Schema"""
    name: Optional[str] = None
    status: str = "offline"
    current_task: Optional[str] = None


class AgentCreate(AgentBase):
    """创建 Agent"""
    id: str


class AgentUpdate(BaseModel):
    """更新 Agent"""
    name: Optional[str] = None
    status: Optional[str] = None
    current_task: Optional[str] = None


class AgentResponse(AgentBase):
    """Agent 响应"""
    id: str
    last_seen: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AgentStatus(BaseModel):
    """Agent 状态（简化版，用于实时推送）"""
    id: str
    name: Optional[str]
    status: str
    current_task: Optional[str]
    last_seen: datetime
