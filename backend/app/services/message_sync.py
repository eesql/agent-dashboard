"""消息同步服务 - 从 OpenClaw session 文件解析消息历史"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.message import Message
from app.models.session import Session

logger = logging.getLogger(__name__)


class MessageSyncService:
    """消息同步服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sessions_dir = self._find_sessions_dir()
    
    def _find_sessions_dir(self) -> Optional[str]:
        """查找 OpenClaw sessions 目录"""
        # 可能的路径列表
        possible_paths = [
            os.path.expanduser("~/.openclaw/agents/main/sessions"),
            os.path.expanduser("~/.openclaw/workspace/agents/main/sessions"),
            os.path.expanduser("~/.openclaw/sessions"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found sessions directory: {path}")
                return path
        
        logger.warning("Sessions directory not found")
        return None
    
    async def sync_session_messages(self, session_id: str) -> int:
        """同步单个 session 的消息历史"""
        if not self.sessions_dir:
            logger.warning("No sessions directory available")
            return 0
        
        # 查找对应的 jsonl 文件
        session_file = os.path.join(self.sessions_dir, f"{session_id}.jsonl")
        
        if not os.path.exists(session_file):
            logger.debug(f"Session file not found: {session_file}")
            return 0
        
        try:
            messages = self._parse_jsonl(session_file, session_id)
            await self._save_messages(session_id, messages)
            logger.info(f"Synced {len(messages)} messages for session {session_id}")
            return len(messages)
        except Exception as e:
            logger.error(f"Failed to sync messages for session {session_id}: {e}")
            return 0
    
    def _parse_jsonl(self, file_path: str, session_id: str) -> List[Dict[str, Any]]:
        """解析 jsonl 文件，提取消息"""
        messages = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        entry = json.loads(line)
                        parsed = self._parse_entry(entry, session_id)
                        if parsed:
                            messages.extend(parsed)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Failed to parse jsonl file {file_path}: {e}")
        
        return messages
    
    def _parse_entry(self, entry: Dict[str, Any], session_id: str) -> List[Dict[str, Any]]:
        """解析单个 entry，返回消息列表"""
        messages = []
        
        if entry.get('type') != 'message':
            return messages
        
        msg = entry.get('message', {})
        content_list = msg.get('content', [])
        role = msg.get('role', 'assistant')
        timestamp = entry.get('timestamp', datetime.now().isoformat())
        
        # 处理文本内容
        text_content = ""
        for item in content_list:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    text_content += item.get('text', '')
                elif item.get('type') == 'toolCall':
                    # 工具调用
                    messages.append({
                        "session_id": session_id,
                        "role": role,
                        "content": None,
                        "content_json": item,
                        "tool_call_id": item.get('id'),
                        "tool_name": item.get('name', 'unknown'),
                        "tool_args": item.get('arguments', {}),
                        "tool_result": None,
                        "is_tool_call": True,
                        "is_tool_result": False,
                        "timestamp": timestamp,
                    })
                elif item.get('type') == 'toolResult':
                    # 工具结果
                    content_text = ''
                    if isinstance(item.get('content'), list):
                        for c in item['content']:
                            if isinstance(c, dict) and c.get('type') == 'text':
                                content_text = c.get('text', '')[:2000]
                                break
                    
                    messages.append({
                        "session_id": session_id,
                        "role": "tool",
                        "content": content_text,
                        "content_json": item,
                        "tool_call_id": item.get('toolCallId'),
                        "tool_name": item.get('toolName', 'unknown'),
                        "tool_args": None,
                        "tool_result": content_text,
                        "is_tool_call": False,
                        "is_tool_result": True,
                        "timestamp": timestamp,
                    })
        
        # 如果有纯文本内容，添加文本消息
        if text_content.strip():
            messages.append({
                "session_id": session_id,
                "role": role,
                "content": text_content,
                "content_json": None,
                "tool_call_id": None,
                "tool_name": None,
                "tool_args": None,
                "tool_result": None,
                "is_tool_call": False,
                "is_tool_result": False,
                "timestamp": timestamp,
            })
        
        return messages
    
    async def _save_messages(self, session_id: str, messages: List[Dict[str, Any]]) -> None:
        """保存消息到数据库"""
        # 先检查 session 是否存在
        result = await self.db.execute(
            select(Session).where(Session.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            logger.warning(f"Session {session_id} not found, skipping message sync")
            return
        
        # 去重并保存消息
        for msg_data in messages:
            # 检查是否已存在（基于 tool_call_id 或 timestamp）
            existing = None
            if msg_data.get('tool_call_id'):
                result = await self.db.execute(
                    select(Message).where(
                        Message.session_id == session_id,
                        Message.tool_call_id == msg_data['tool_call_id'],
                        Message.is_tool_call == msg_data['is_tool_call']
                    )
                )
                existing = result.scalar_one_or_none()
            
            if not existing:
                message = Message(**msg_data)
                self.db.add(message)
        
        await self.db.commit()
