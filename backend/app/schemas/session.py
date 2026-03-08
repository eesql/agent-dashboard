"""Session 相关 Schema"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SessionBase(BaseModel):
    """Session 基础 Schema"""
    label: Optional[str] = None
    kind: Optional[str] = None


class SessionResponse(SessionBase):
    """Session 响应"""
    id: str
    agent_id: Optional[str]
    created_at: datetime
    last_activity: datetime
    message_count: int
    
    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """Session 列表响应"""
    sessions: List[SessionResponse]
    total: int
