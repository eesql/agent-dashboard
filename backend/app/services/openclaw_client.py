"""OpenClaw Session API 客户端 - 使用 exec 调用 openclaw 命令"""
import asyncio
import json
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class OpenClawClient:
    """OpenClaw API 客户端（通过命令行调用）"""
    
    def __init__(self):
        self.timeout = 30.0
    
    async def _run_command(self, args: List[str]) -> Dict[str, Any]:
        """运行 openclaw 命令"""
        try:
            process = await asyncio.create_subprocess_exec(
                "openclaw",
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else f"Exit code: {process.returncode}"
                logger.error(f"Command failed: {error_msg}")
                return {"error": error_msg}
            
            # 尝试解析 JSON 输出
            output = stdout.decode()
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                # 非 JSON 输出，返回原始文本
                return {"output": output}
                
        except asyncio.TimeoutError:
            logger.error("Command timeout")
            return {"error": "Command timeout"}
        except Exception as e:
            logger.error(f"Command error: {e}")
            return {"error": str(e)}
    
    async def sessions_list(
        self,
        message_limit: int = 10,
        active_minutes: Optional[int] = None,
        limit: int = 50,
        kinds: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """列出会话"""
        # 使用 openclaw sessions 命令（需要解析输出）
        # 暂时返回模拟数据用于测试
        logger.info("Fetching sessions from OpenClaw...")
        
        # TODO: 解析 openclaw status 输出
        # 现在返回空数组，因为需要解析表格输出
        return {"sessions": [], "raw_output": "Use openclaw status command"}
    
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
