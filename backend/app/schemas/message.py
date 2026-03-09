"""Message 相关 Schema"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class MessageResponse(BaseModel):
    """消息响应"""
    id: int
    session_id: str
    role: str
    content: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_name: Optional[str] = None
    tool_args: Optional[dict] = None
    tool_result: Optional[str] = None
    is_tool_call: bool = False
    is_tool_result: bool = False
    timestamp: datetime
    
    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """消息列表响应"""
    messages: List[MessageResponse]
    total: int
    has_more: bool = False
