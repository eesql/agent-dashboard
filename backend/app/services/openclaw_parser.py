"""OpenClaw 命令输出解析器"""
import subprocess
import re
import json
from typing import List, Dict, Any, Optional
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
    import platform
    
    try:
        system = platform.system()
        
        if system == "Windows":
            # Windows: 使用 PowerShell
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", "openclaw sessions"],
                capture_output=True,
                timeout=30,
                cwd="C:\\nvm4w\\nodejs",
                encoding='utf-8',
                errors='ignore'
            )
        else:
            # Linux/macOS: 使用 bash，加载 nvm 环境
            # 先尝试加载 nvm 并使用 node 22
            cmd = """
source ~/.nvm/nvm.sh 2>/dev/null || true
nvm use 22 2>/dev/null || true
openclaw sessions
"""
            result = subprocess.run(
                ["bash", "-c", cmd],
                capture_output=True,
                timeout=30,
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
                        # Kind = parts[0], Key = parts[1], Age = parts[2], Age unit = parts[3], Model = parts[4], Tokens = parts[5]
                        kind = parts[0]
                        key = parts[1]
                        age = parts[2] + " " + parts[3]  # "8h ago"
                        model = parts[4]
                        tokens = parts[5] if len(parts) > 5 else ""  # "85k/1000k"
                        
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


def parse_session_jsonl(session_file: str, session_key: str) -> List[Dict[str, Any]]:
    """解析 session 的 jsonl 文件，提取工具调用"""
    import os
    tool_calls = []
    
    try:
        if not os.path.exists(session_file):
            logger.debug(f"Session file not found: {session_file}")
            return []
        
        with open(session_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    entry = json.loads(line)
                    
                    # 检查是否是工具调用消息
                    if entry.get('type') == 'message':
                        msg = entry.get('message', {})
                        content = msg.get('content', [])
                        
                        # 查找 toolCall 类型的内容
                        for item in content:
                            if isinstance(item, dict) and item.get('type') == 'toolCall':
                                tool_call = {
                                    "session_id": session_key,
                                    "tool_name": item.get('name', 'unknown'),
                                    "tool_args": item.get('arguments', {}),
                                    "result_summary": None,
                                    "timestamp": entry.get('timestamp', datetime.now().isoformat()),
                                    "duration_ms": None,
                                    "tool_call_id": item.get('id'),
                                }
                                tool_calls.append(tool_call)
                            
                            # 查找工具返回结果
                            elif isinstance(item, dict) and item.get('type') == 'toolResult':
                                # 查找对应的 toolCall
                                tool_call_id = item.get('toolCallId')
                                content_text = ''
                                if isinstance(item.get('content'), list):
                                    for c in item['content']:
                                        if isinstance(c, dict) and c.get('type') == 'text':
                                            content_text = c.get('text', '')[:200]
                                            break
                                
                                tool_call = {
                                    "session_id": session_key,
                                    "tool_name": item.get('toolName', 'unknown'),
                                    "tool_args": None,
                                    "result_summary": content_text,
                                    "timestamp": entry.get('timestamp', datetime.now().isoformat()),
                                    "duration_ms": None,
                                    "tool_call_id": tool_call_id,
                                }
                                tool_calls.append(tool_call)
                    
                except json.JSONDecodeError:
                    continue
        
        logger.info(f"Parsed {len(tool_calls)} tool calls from {session_file}")
        return tool_calls
        
    except Exception as e:
        logger.error(f"Failed to parse session jsonl: {e}")
        return []


def parse_session_stats(session_file: str) -> Dict[str, int]:
    """解析 session 的 jsonl 文件，统计API请求数和token数
    
    Returns:
        Dict with keys: request_count (API请求数), token_count (总token数)
    """
    import os
    
    result = {
        "request_count": 0,
        "token_count": 0,
        "input_tokens": 0,
        "output_tokens": 0,
    }
    
    try:
        if not os.path.exists(session_file):
            logger.debug(f"Session file not found: {session_file}")
            return result
        
        with open(session_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    entry = json.loads(line)
                    
                    # 统计 assistant 消息（每次 assistant 响应代表一次 API 请求）
                    if entry.get('type') == 'message':
                        msg = entry.get('message', {})
                        role = msg.get('role', '')
                        
                        if role == 'assistant':
                            result['request_count'] += 1
                            
                            # 提取 token 使用量
                            usage = msg.get('usage', {})
                            if usage:
                                result['input_tokens'] += usage.get('input', 0)
                                result['output_tokens'] += usage.get('output', 0)
                                result['token_count'] += usage.get('totalTokens', 0)
                    
                except json.JSONDecodeError:
                    continue
        
        logger.debug(f"Parsed session stats: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to parse session stats: {e}")
        return result


def find_session_file(session_key: str) -> Optional[str]:
    """根据 session key 查找对应的 jsonl 文件路径
    
    Args:
        session_key: 会话标识，格式如 "agent:main:feishu...xxx" 或 "direct:xxx"
    
    Returns:
        session jsonl 文件的完整路径，找不到返回 None
    """
    import os
    import glob
    
    # 从 session key 提取可能的 session id
    # 格式可能是 "agent:main:feishu...xxx" 或 "direct:xxx"
    parts = session_key.split(':')
    session_id = parts[-1] if len(parts) > 1 else session_key
    
    # 可能的 session 目录位置
    session_dirs = [
        os.path.expanduser('~/.openclaw/agents/main/sessions'),
        os.path.expanduser('~/.openclaw/agents/agent-feishu-pd/sessions'),
        os.path.expanduser('~/.openclaw/agents/*/sessions'),
    ]
    
    for pattern in session_dirs:
        # 使用 glob 处理通配符
        for session_dir in glob.glob(pattern):
            session_file = os.path.join(session_dir, f'{session_id}.jsonl')
            if os.path.exists(session_file):
                return session_file
    
    return None
