"""消息相关 API 端点"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.database import get_db
from app.schemas.message import MessageResponse, MessageListResponse
from app.models.message import Message
from app.services.message_sync import MessageSyncService
from sqlalchemy import select, func

router = APIRouter(prefix="/api/sessions", tags=["messages"])


@router.get("/{session_id}/messages", response_model=MessageListResponse)
async def list_messages(
    session_id: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """获取会话消息列表（分页）"""
    # 先同步消息
    sync_service = MessageSyncService(db)
    await sync_service.sync_session_messages(session_id)
    
    # 查询消息
    query = (
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.timestamp.asc())
        .offset(offset)
        .limit(limit)
    )
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    # 获取总数
    count_query = (
        select(func.count(Message.id))
        .where(Message.session_id == session_id)
    )
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    return {
        "messages": messages,
        "total": total,
        "has_more": total > offset + limit,
    }


@router.post("/{session_id}/messages/sync")
async def sync_messages(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """手动触发消息同步"""
    sync_service = MessageSyncService(db)
    count = await sync_service.sync_session_messages(session_id)
    
    return {
        "status": "success",
        "message": f"Synced {count} messages",
        "count": count,
    }
