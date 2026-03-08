"""OpenClaw 命令输出解析器"""
import subprocess
import re
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def parse_age_to_datetime(age_str: str) -> datetime:
    """将年龄字符串转换为 datetime"""
    age_str = age_str.strip()
    
    if age_str == "now":
        return datetime.now()
    
    match = re.match(r'(\d+)\s*(second|minute|hour|day|week)s?\s*ago', age_str)
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
        elif unit == "week":
            return datetime.now() - timedelta(weeks=value)
    
    return datetime.now()


def parse_openclaw_sessions() -> List[Dict[str, Any]]:
    """解析 openclaw sessions 输出"""
    try:
        # 使用 PowerShell 调用 openclaw sessions
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", "openclaw sessions"],
            capture_output=True,
            timeout=30,
            cwd="C:\\nvm4w\\nodejs",
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode != 0:
            logger.error(f"openclaw sessions failed: {result.stderr}")
            return []
        
        return parse_sessions_output(result.stdout)
        
    except Exception as e:
        logger.error(f"Failed to parse openclaw sessions: {e}")
        return []


def parse_sessions_output(output: str) -> List[Dict[str, Any]]:
    """解析 openclaw sessions 命令输出"""
    try:
        sessions = []
        lines = output.split('\n')
        seen_keys = set()
        
        for line in lines:
            # 匹配数据行（以 direct/other 开头的行）
            if line.strip().startswith('direct') or line.strip().startswith('other'):
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        # Kind = parts[0], Key = parts[1], Age = parts[2], Model = parts[3], Tokens = parts[4]
                        kind = parts[0]
                        key = parts[1]
                        age = parts[2]
                        model = parts[3]
                        tokens = parts[4] if len(parts) > 4 else ""
                        
                        # 跳过重复的 key（包含 ?| 的是乱码，跳过）
                        if '?|' in key or key in seen_keys:
                            continue
                        
                        seen_keys.add(key)
                        
                        # 解析 token 数（格式如 "85k/1000k (8%)"）
                        token_count = 0
                        if tokens and '/' in tokens:
                            try:
                                token_str = tokens.split('/')[0]  # "85k"
                                if 'k' in token_str:
                                    token_count = int(float(token_str.replace('k', '')) * 1000)
                                elif 'M' in token_str:
                                    token_count = int(float(token_str.replace('M', '')) * 1000000)
                                else:
                                    token_count = int(token_str)
                                logger.debug(f"Parsed token: {tokens} -> {token_count}")
                            except Exception as e:
                                logger.debug(f"Failed to parse token '{tokens}': {e}")
                        
                        sessions.append({
                            "id": key,
                            "key": key,
                            "kind": kind,
                            "age": age,
                            "model": model,
                            "tokens": token_count,
                            "last_seen": parse_age_to_datetime(age).isoformat(),
                            "status": "online" if age and ("now" in age or "1m" in age or "2m" in age or "3m" in age or "4m" in age or "5m" in age) else "offline",
                        })
                    except Exception as e:
                        logger.debug(f"Failed to parse line: {line}, error: {e}")
                        continue
        
        logger.info(f"Parsed {len(sessions)} unique sessions from openclaw sessions")
        return sessions
        
    except Exception as e:
        logger.error(f"Failed to parse sessions output: {e}")
        return []
