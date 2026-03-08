"""WebSocket 实时推送"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        # 存储所有活跃连接
        self.active_connections: List[WebSocket] = []
        # 存储订阅信息
        self.subscriptions: Dict[WebSocket, List[str]] = {}
    
    async def connect(self, websocket: WebSocket):
        """接受新连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscriptions[websocket] = ["*"]  # 默认订阅所有
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """断开连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict, channels: List[str] = None):
        """广播消息"""
        disconnected = []
        
        for connection in self.active_connections:
            # 检查订阅
            subs = self.subscriptions.get(connection, ["*"])
            if channels and not any(ch in subs for ch in ["*", *channels]):
                continue
            
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to connection: {e}")
                disconnected.append(connection)
        
        # 清理断开的连接
        for conn in disconnected:
            self.disconnect(conn)
    
    async def send_to(self, websocket: WebSocket, message: dict):
        """发送消息到指定连接"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.disconnect(websocket)
    
    def subscribe(self, websocket: WebSocket, channels: List[str]):
        """订阅频道"""
        self.subscriptions[websocket] = channels


# 全局管理器实例
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点"""
    await manager.connect(websocket)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                
                # 处理订阅请求
                if msg_type == "subscribe":
                    channels = message.get("channels", ["*"])
                    manager.subscribe(websocket, channels)
                    await websocket.send_json({
                        "type": "subscribed",
                        "channels": channels,
                    })
                
                # 处理心跳
                elif msg_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat(),
                    })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON",
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def notify_agent_status(agent_data: dict):
    """通知 Agent 状态变化"""
    await manager.broadcast({
        "type": "agent:status",
        "data": agent_data,
        "timestamp": datetime.now().isoformat(),
    }, channels=["agents"])


async def notify_new_session(session_data: dict):
    """通知新会话"""
    await manager.broadcast({
        "type": "session:new",
        "data": session_data,
        "timestamp": datetime.now().isoformat(),
    }, channels=["sessions"])


async def notify_tool_call(tool_call_data: dict):
    """通知工具调用"""
    await manager.broadcast({
        "type": "tool:call",
        "data": tool_call_data,
        "timestamp": datetime.now().isoformat(),
    }, channels=["tools"])


async def notify_metrics_update(metrics_data: dict):
    """通知统计数据更新"""
    await manager.broadcast({
        "type": "metrics:update",
        "data": metrics_data,
        "timestamp": datetime.now().isoformat(),
    }, channels=["metrics"])
