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
    """解析 openclaw sessions 输出
    
    优先从 sessions.json 读取完整数据，回退到命令行解析
    """
    import os
    import glob
    
    sessions = []
    seen_keys = set()
    
    # 方法1: 直接从 sessions.json 读取（更准确）
    sessions_json_paths = glob.glob(os.path.expanduser('~/.openclaw/agents/*/sessions/sessions.json'))
    
    for sessions_json_path in sessions_json_paths:
        try:
            with open(sessions_json_path, 'r', encoding='utf-8') as f:
                sessions_map = json.load(f)
            
            for session_key, session_info in sessions_map.items():
                if session_key in seen_keys:
                    continue
                seen_keys.add(session_key)
                
                # 解析时间
                updated_at = session_info.get('updatedAt')
                if updated_at:
                    last_seen = datetime.fromtimestamp(updated_at / 1000)
                else:
                    last_seen = datetime.now()
                
                # 计算 age
                age_seconds = (datetime.now() - last_seen).total_seconds()
                if age_seconds < 60:
                    age = f"{int(age_seconds)}s"
                elif age_seconds < 3600:
                    age = f"{int(age_seconds / 60)}m"
                elif age_seconds < 86400:
                    age = f"{int(age_seconds / 3600)}h"
                else:
                    age = f"{int(age_seconds / 86400)}d"
                
                # 获取 token 数
                total_tokens = session_info.get('totalTokens', 0) or session_info.get('inputTokens', 0) + session_info.get('outputTokens', 0)
                
                # 判断状态
                if age_seconds < 300:  # 5 分钟内
                    status = "online"
                elif age_seconds < 3600:  # 1 小时内
                    status = "busy"
                else:
                    status = "offline"
                
                sessions.append({
                    "id": session_key,
                    "key": session_key,
                    "kind": session_info.get('chatType', 'direct'),
                    "age": f"{age} ago",
                    "model": session_info.get('model', 'unknown'),
                    "tokens": total_tokens,
                    "last_seen": last_seen.isoformat(),
                    "status": status,
                    "sessionFile": session_info.get('sessionFile'),
                })
                
        except Exception as e:
            logger.debug(f"Failed to read {sessions_json_path}: {e}")
            continue
    
    if sessions:
        logger.info(f"Loaded {len(sessions)} sessions from sessions.json")
        return sessions
    
    # 方法2: 回退到命令行解析
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
        session_key: 会话标识，格式如 "agent:main:feishu:direct:ou_xxx" 或 "direct:xxx"
    
    Returns:
        session jsonl 文件的完整路径，找不到返回 None
    """
    import os
    import glob
    
    # 从 session key 提取 agent 名称（如果存在）
    # 格式: "agent:main:feishu:direct:ou_xxx" 或 "agent:agent-feishu-pd:..."
    parts = session_key.split(':')
    agent_name = None
    if len(parts) >= 2 and parts[0] == 'agent':
        agent_name = parts[1]
    
    # 可能的 sessions.json 位置
    sessions_json_paths = []
    if agent_name:
        sessions_json_paths.append(os.path.expanduser(f'~/.openclaw/agents/{agent_name}/sessions/sessions.json'))
    
    # 如果没找到，搜索所有 agent 目录
    if not sessions_json_paths or not os.path.exists(sessions_json_paths[0]):
        sessions_json_paths = glob.glob(os.path.expanduser('~/.openclaw/agents/*/sessions/sessions.json'))
    
    for sessions_json_path in sessions_json_paths:
        try:
            with open(sessions_json_path, 'r', encoding='utf-8') as f:
                sessions_map = json.load(f)
            
            # 查找匹配的 session key
            if session_key in sessions_map:
                session_info = sessions_map[session_key]
                session_file = session_info.get('sessionFile')
                if session_file and os.path.exists(session_file):
                    return session_file
            
            # 尝试模糊匹配（session key 可能被截断）
            for key, info in sessions_map.items():
                if session_key in key or key in session_key:
                    session_file = info.get('sessionFile')
                    if session_file and os.path.exists(session_file):
                        return session_file
                    
        except Exception as e:
            logger.debug(f"Failed to read sessions.json: {e}")
            continue
    
    return None
