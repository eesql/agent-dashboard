"""Tool Call 相关 API 端点"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta
from app.db.database import get_db
from app.services.data_aggregator import DataAggregator
from app.schemas.tool_call import ToolCallResponse, ToolCallListResponse
from app.models.tool_call import ToolCall
from sqlalchemy import select

router = APIRouter(prefix="/api/tool-calls", tags=["tool-calls"])


@router.get("", response_model=ToolCallListResponse)
async def list_tool_calls(
    session_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
):
    """获取工具调用日志"""
    query = select(ToolCall).order_by(ToolCall.timestamp.desc()).limit(limit)
    
    if session_id:
        query = query.where(ToolCall.session_id == session_id)
    
    # 时间范围过滤
    since = datetime.now() - timedelta(hours=hours)
    query = query.where(ToolCall.timestamp >= since)
    
    result = await db.execute(query)
    tool_calls = result.scalars().all()
    
    return {
        "tool_calls": tool_calls,
        "total": len(tool_calls),
    }


@router.get("/{tool_call_id}", response_model=ToolCallResponse)
async def get_tool_call(tool_call_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个工具调用详情"""
    result = await db.execute(
        select(ToolCall).where(ToolCall.id == tool_call_id)
    )
    tool_call = result.scalar_one_or_none()
    
    if not tool_call:
        raise HTTPException(status_code=404, detail="Tool call not found")
    
    return tool_call
