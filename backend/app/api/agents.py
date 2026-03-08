"""Agent 相关 API 端点"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.database import get_db
from app.services.agent_monitor import AgentMonitor
from app.schemas.agent import AgentResponse, AgentStatus
from app.models.agent import Agent

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("", response_model=List[AgentResponse])
async def list_agents(db: AsyncSession = Depends(get_db)):
    """获取所有 Agent 状态列表"""
    monitor = AgentMonitor(db)
    agents = await monitor.get_all_agents()
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """获取单个 Agent 详情"""
    monitor = AgentMonitor(db)
    agent = await monitor.get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent


@router.post("/sync")
async def sync_agents(db: AsyncSession = Depends(get_db)):
    """从 OpenClaw API 同步 Agent 状态"""
    monitor = AgentMonitor(db)
    agents = await monitor.sync_agents()
    return {"synced": len(agents), "agents": agents}
