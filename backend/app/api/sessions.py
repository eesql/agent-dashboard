"""Session 相关 API 端点"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.database import get_db
from app.services.agent_monitor import AgentMonitor
from app.schemas.session import SessionResponse, SessionListResponse
from app.models.session import Session
from sqlalchemy import select

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    limit: int = Query(50, ge=1, le=500),
    agent_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取会话列表"""
    query = select(Session).order_by(Session.last_activity.desc()).limit(limit)
    
    if agent_id:
        query = query.where(Session.agent_id == agent_id)
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    return {
        "sessions": sessions,
        "total": len(sessions),
    }


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """获取会话详情"""
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session
