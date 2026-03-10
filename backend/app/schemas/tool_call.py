"""Tool Call 相关 Schema"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import json


class ToolCallBase(BaseModel):
    """Tool Call 基础 Schema"""
    tool_name: str
    tool_args: Optional[Union[Dict[str, Any], str]] = None
    result_summary: Optional[str] = None
    duration_ms: Optional[int] = None
    
    @field_validator('tool_args', mode='before')
    @classmethod
    def parse_tool_args(cls, v):
        """将 JSON 字符串解析为字典"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {"raw": v}
        return v


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
