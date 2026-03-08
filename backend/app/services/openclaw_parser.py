"""OpenClaw 命令输出解析器"""
import re
import subprocess
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def parse_age_to_datetime(age_str: str) -> datetime:
    """将年龄字符串转换为 datetime"""
    age_str = age_str.strip()
    
    if age_str == "now":
        return datetime.now()
    
    match = re.match(r'(\d+)\s*(second|minute|hour|day)s?\s*ago', age_str)
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit == "second":
            return datetime.now() - timedelta(seconds=value)
        elif unit == "minute":
            return datetime.now() - timedelta(minutes=value)
        elif unit == "hour":
            return datetime.now() - timedelta(hours=value)
        elif unit == "day":
            return datetime.now() - timedelta(days=value)
    
    return datetime.now()


def parse_openclaw_status() -> List[Dict[str, Any]]:
    """解析 openclaw status 输出"""
    try:
        # 使用 PowerShell 调用 openclaw，使用 UTF-8 编码
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-OutputFormat", "Text", "-Command", "openclaw status"],
            capture_output=True,
            timeout=30,
            cwd="C:\\nvm4w\\nodejs",
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            return parse_status_table(result.stdout)
        else:
            logger.error(f"openclaw status failed: {result.stderr}")
            return []
        
    except Exception as e:
        logger.error(f"Failed to parse openclaw status: {e}")
        return []


def parse_status_table(output: str) -> List[Dict[str, Any]]:
    """解析 openclaw status 表格输出"""
    try:
        sessions = []
        
        # 解析表格行
        lines = output.split('\n')
        for line in lines:
            # 匹配表格行（包含 session key 的行）
            if '│' in line and 'agent:' in line:
                parts = line.split('│')
                if len(parts) >= 5:
                    try:
                        key = parts[1].strip()
                        kind = parts[2].strip()
                        age = parts[3].strip()
                        model = parts[4].strip()
                        
                        # 提取 session ID
                        session_id = key.split(':')[-1] if ':' in key else key
                        
                        sessions.append({
                            "id": session_id,
                            "key": key,
                            "kind": "direct" if "direct" in kind else kind,
                            "age": age,
                            "model": model,
                            "last_seen": parse_age_to_datetime(age).isoformat(),
                            "status": "online" if "ago" in age and ("1m" in age or "5m" in age or "10m" in age) else "offline",
                        })
                    except Exception as e:
                        logger.debug(f"Failed to parse line: {e}")
                        continue
        
        return sessions
        
    except Exception as e:
        logger.error(f"Failed to parse status table: {e}")
        return []


def get_active_sessions() -> List[Dict[str, Any]]:
    """获取活跃会话"""
    sessions = parse_openclaw_status()
    
    # 过滤活跃会话（最近 10 分钟内）
    now = datetime.now()
    active = []
    
    for session in sessions:
        try:
            last_seen = datetime.fromisoformat(session.get("last_seen", ""))
            if (now - last_seen).total_seconds() < 600:  # 10 分钟
                active.append(session)
        except:
            continue
    
    return active
