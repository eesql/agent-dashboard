"""日志配置模块 - 支持日志轮转防止磁盘空间被占满"""
import logging
import os
import gzip
import shutil
from logging.handlers import RotatingFileHandler
from typing import Optional
from pathlib import Path


class CompressedRotatingFileHandler(RotatingFileHandler):
    """支持压缩的日志轮转处理器"""
    
    def doRollover(self):
        """
        执行日志轮转，并压缩旧日志文件
        """
        # 调用父类的轮转方法
        super().doRollover()
        
        # 压缩轮转后的日志文件
        for i in range(1, self.backupCount + 1):
            log_file = f"{self.baseFilename}.{i}"
            gz_file = f"{log_file}.gz"
            
            if os.path.exists(log_file) and not os.path.exists(gz_file):
                try:
                    with open(log_file, 'rb') as f_in:
                        with gzip.open(gz_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    os.remove(log_file)
                except Exception as e:
                    # 压缩失败时保留原文件
                    pass


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "./logs",
    log_max_bytes: int = 50 * 1024 * 1024,  # 50 MB (减小以更频繁轮转)
    log_backup_count: int = 7,  # 增加到7个备份
    debug: bool = False,
    compress_logs: bool = True,  # 是否压缩旧日志
) -> None:
    """
    配置应用日志，支持日志轮转和压缩
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: 日志目录
        log_max_bytes: 单个日志文件最大大小（字节）
        log_backup_count: 保留的日志文件数量
        debug: 是否为调试模式（调试模式输出到控制台）
        compress_logs: 是否压缩旧日志文件
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
    
    # 文件处理器（带轮转和可选压缩）
    log_file = os.path.join(log_dir, "backend.log")
    
    if compress_logs:
        file_handler = CompressedRotatingFileHandler(
            log_file,
            maxBytes=log_max_bytes,
            backupCount=log_backup_count,
            encoding="utf-8",
        )
    else:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=log_max_bytes,
            backupCount=log_backup_count,
            encoding="utf-8",
        )
    
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 清理过期的压缩日志文件（超过 backupCount 的 .gz 文件）
    log_path = Path(log_dir)
    gz_files = sorted(log_path.glob("backend.log.*.gz"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old_gz in gz_files[log_backup_count:]:
        try:
            old_gz.unlink()
        except Exception:
            pass
    
    # 记录日志配置信息
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: level={log_level}, dir={log_dir}, max_bytes={log_max_bytes}, backup_count={log_backup_count}, compress={compress_logs}")
