"""OpenClaw Session API 客户端"""
import httpx
from typing import Optional, List, Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class OpenClawClient:
    """OpenClaw API 客户端"""
    
    def __init__(self):
        self.base_url = settings.openclaw_api_url or "http://localhost:8080"
        self.api_key = settings.openclaw_api_key
        self.timeout = 30.0
        
    async def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def sessions_list(
        self,
        message_limit: int = 10,
        active_minutes: Optional[int] = None,
        limit: int = 50,
        kinds: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """列出会话"""
        url = f"{self.base_url}/api/sessions/list"
        params = {
            "messageLimit": message_limit,
            "limit": limit,
        }
        if active_minutes:
            params["activeMinutes"] = active_minutes
        if kinds:
            params["kinds"] = kinds
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    url,
                    headers=await self._get_headers(),
                    json=params,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to list sessions: {e}")
                return {"sessions": [], "error": str(e)}
    
    async def sessions_history(
        self,
        session_key: str,
        limit: int = 50,
        include_tools: bool = True,
    ) -> Dict[str, Any]:
        """获取会话历史"""
        url = f"{self.base_url}/api/sessions/history"
        params = {
            "sessionKey": session_key,
            "limit": limit,
            "includeTools": include_tools,
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    url,
                    headers=await self._get_headers(),
                    json=params,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to get session history: {e}")
                return {"messages": [], "error": str(e)}
    
    async def session_status(self, session_key: Optional[str] = None) -> Dict[str, Any]:
        """获取会话状态"""
        url = f"{self.base_url}/api/session/status"
        params = {}
        if session_key:
            params["sessionKey"] = session_key
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    url,
                    headers=await self._get_headers(),
                    json=params,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to get session status: {e}")
                return {"error": str(e)}
    
    async def subagents_list(self, recent_minutes: int = 60) -> Dict[str, Any]:
        """列出子 Agent"""
        url = f"{self.base_url}/api/subagents/list"
        params = {"recentMinutes": recent_minutes}
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    url,
                    headers=await self._get_headers(),
                    json=params,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to list subagents: {e}")
                return {"agents": [], "error": str(e)}
    
    async def health_check(self) -> bool:
        """健康检查"""
        url = f"{self.base_url}/api/status"
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(url)
                return response.status_code == 200
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return False


# 单例
openclaw_client = OpenClawClient()
