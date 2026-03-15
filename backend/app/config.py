"""应用配置管理"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 服务配置
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    debug: bool = True
    
    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./agent_dashboard.db"
    
    # OpenClaw API 配置
    openclaw_api_url: Optional[str] = None
    openclaw_api_key: Optional[str] = None
    
    # 轮询间隔（秒）
    agent_status_poll_interval: int = 5
    metrics_aggregate_interval: int = 60
    
    # 前端配置
    frontend_url: str = "http://localhost:5173"
    
    # WebSocket 配置
    ws_heartbeat_interval: int = 30
    
    # 日志配置
    log_level: str = "INFO"
    log_dir: str = "./logs"
    log_max_bytes: int = 100 * 1024 * 1024  # 100 MB
    log_backup_count: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
