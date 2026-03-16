"""FastAPI 应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.db.database import init_db, close_db
from app.api import agents_router, sessions_router, tool_calls_router, metrics_router, messages_router, session_info_router
from app.api.websocket import router as websocket_router
from app.logging_config import setup_logging
import logging

# 配置日志（支持轮转和压缩，防止磁盘空间被占满）
setup_logging(
    log_level=settings.log_level,
    log_dir=settings.log_dir,
    log_max_bytes=settings.log_max_bytes,
    log_backup_count=settings.log_backup_count,
    debug=settings.debug,
    compress_logs=getattr(settings, 'compress_logs', True),
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    from app.services.sync_service import SyncService
    from app.db.database import async_session_maker
    
    # 启动时
    logger.info("Starting Agent Dashboard API...")
    await init_db()
    logger.info("Database initialized")
    
    # 启动定时同步服务（使用独立的会话工厂，而不是单个会话）
    sync_svc = SyncService(async_session_maker)
    await sync_svc.start()
    logger.info("Sync service started")
    
    yield
    
    # 关闭时
    logger.info("Shutting down Agent Dashboard API...")
    
    # 停止同步服务
    await sync_svc.stop()
    
    await close_db()


# 创建 FastAPI 应用
app = FastAPI(
    title="Agent Dashboard API",
    description="OpenClaw Agent 状态和行为监控 API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(agents_router)
app.include_router(sessions_router)
app.include_router(tool_calls_router)
app.include_router(metrics_router)
app.include_router(messages_router)
app.include_router(session_info_router)
app.include_router(websocket_router)


@app.get("/")
async def root():
    """根端点"""
    return {
        "name": "Agent Dashboard API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug,
    )
