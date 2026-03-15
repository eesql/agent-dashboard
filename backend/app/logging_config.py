"""日志配置模块 - 支持日志轮转防止磁盘空间被占满"""
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "./logs",
    log_max_bytes: int = 100 * 1024 * 1024,  # 100 MB
    log_backup_count: int = 5,
    debug: bool = False,
) -> None:
    """
    配置应用日志，支持日志轮转
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: 日志目录
        log_max_bytes: 单个日志文件最大大小（字节）
        log_backup_count: 保留的日志文件数量
        debug: 是否为调试模式（调试模式输出到控制台）
    """
    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)
    
    # 确定日志级别
    level = logging.DEBUG if debug else getattr(logging, log_level.upper(), logging.INFO)
    
    # 日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)
    
    # 获取根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除现有的处理器（避免重复配置）
    root_logger.handlers.clear()
    
    # 控制台处理器（始终启用）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（带轮转）
    log_file = os.path.join(log_dir, "backend.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=log_max_bytes,
        backupCount=log_backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 记录日志配置信息
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: level={log_level}, dir={log_dir}, max_bytes={log_max_bytes}, backup_count={log_backup_count}")
