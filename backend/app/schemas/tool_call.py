"""Tool Call 相关 Schema"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ToolCallBase(BaseModel):
    """Tool Call 基础 Schema"""
    tool_name: str
    tool_args: Optional[Dict[str, Any]] = None
    result_summary: Optional[str] = None
    duration_ms: Optional[int] = None


class ToolCallResponse(ToolCallBase):
    """Tool Call 响应"""
    id: int
    session_id: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ToolCallListResponse(BaseModel):
    """Tool Call 列表响应"""
    tool_calls: List[ToolCallResponse]
    total: int
