"""定时同步服务"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.services.agent_monitor import AgentMonitor
from app.services.data_aggregator import DataAggregator
from app.config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SyncService:
    """数据同步服务"""
    
    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory
        self._running = False
        self._task = None
    
    async def start(self):
        """启动定时同步"""
        if self._running:
            logger.warning("Sync service already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._sync_loop())
        logger.info(f"Sync service started (interval: {settings.agent_status_poll_interval}s)")
    
    async def stop(self):
        """停止定时同步"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Sync service stopped")
    
    async def _sync_loop(self):
        """同步循环"""
        while self._running:
            try:
                await self._sync_once()
            except Exception as e:
                logger.error(f"Sync error: {e}")
            
            await asyncio.sleep(settings.agent_status_poll_interval)
    
    async def _sync_once(self):
        """执行一次同步"""
        logger.debug("Starting sync...")
        
        async with self.session_factory() as db:
            # 同步 Agent 状态
            monitor = AgentMonitor(db)
            agents = await monitor.sync_agents()
            logger.info(f"Synced {len(agents)} agents")
            
            # 聚合统计数据
            aggregator = DataAggregator(db)
            await aggregator.aggregate_metrics()
            logger.debug("Metrics aggregated")
    
    async def sync_now(self) -> dict:
        """立即执行同步"""
        logger.info("Manual sync triggered")
        
        try:
            async with self.session_factory() as db:
                # 同步 Agent 状态
                monitor = AgentMonitor(db)
                agents = await monitor.sync_agents()
                
                # 聚合统计数据
                aggregator = DataAggregator(db)
                await aggregator.aggregate_metrics()
                
                return {
                    "success": True,
                    "synced_agents": len(agents),
                    "timestamp": datetime.now().isoformat(),
                }
        except Exception as e:
            logger.error(f"Manual sync failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }


# 全局同步服务实例
sync_service: SyncService = None


def get_sync_service(session_factory: async_sessionmaker) -> SyncService:
    """获取同步服务实例"""
    global sync_service
    if sync_service is None:
        sync_service = SyncService(session_factory)
    return sync_service
