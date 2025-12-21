"""
WebSocket管理器
用于实时推送测试任务状态更新
"""
from fastapi import WebSocket
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 存储每个任务的WebSocket连接
        # 格式: {task_id: [websocket1, websocket2, ...]}
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, task_id: str):
        """接受WebSocket连接"""
        await websocket.accept()
        
        if task_id not in self.active_connections:
            self.active_connections[task_id] = []
        
        self.active_connections[task_id].append(websocket)
        logger.info(f"WebSocket连接已建立: task_id={task_id}, 当前连接数={len(self.active_connections[task_id])}")
    
    def disconnect(self, websocket: WebSocket, task_id: str):
        """断开WebSocket连接"""
        if task_id in self.active_connections:
            if websocket in self.active_connections[task_id]:
                self.active_connections[task_id].remove(websocket)
                logger.info(f"WebSocket连接已断开: task_id={task_id}, 剩余连接数={len(self.active_connections[task_id])}")
            
            # 如果没有连接了，删除该任务的记录
            if len(self.active_connections[task_id]) == 0:
                del self.active_connections[task_id]
    
    async def broadcast_to_task(self, task_id: str, message: dict):
        """向指定任务的所有连接广播消息"""
        if task_id not in self.active_connections:
            return
        
        disconnected = []
        for websocket in self.active_connections[task_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"发送WebSocket消息失败: {str(e)}")
                disconnected.append(websocket)
        
        # 移除断开的连接
        for websocket in disconnected:
            self.disconnect(websocket, task_id)



