"""
FastAPI主应用入口
提供REST API和WebSocket支持
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import List, Dict
import asyncio
import json

from api.routers import test_plans, test_tasks, reports, constraints, monitoring, gan
from api.routers import requirements, risk_analysis, test_design, export
from api.websocket_manager import WebSocketManager

app = FastAPI(
    title="VCU智能模糊测试系统API",
    description="基于GAN的唤醒-休眠场景智能模糊测试系统后端API",
    version="1.0.0"
)

# CORS配置 - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(test_plans.router, prefix="/api", tags=["测试计划"])
app.include_router(test_tasks.router, prefix="/api", tags=["测试任务"])
app.include_router(reports.router, prefix="/api", tags=["测试报告"])
app.include_router(constraints.router, prefix="/api", tags=["约束管理"])
app.include_router(monitoring.router, prefix="/api", tags=["监控"])
app.include_router(gan.router, prefix="/api", tags=["GAN测试"])
app.include_router(requirements.router, prefix="/api", tags=["需求管理"])
app.include_router(risk_analysis.router, prefix="/api", tags=["风险分析"])
app.include_router(test_design.router, prefix="/api", tags=["测试设计"])
app.include_router(export.router, prefix="/api", tags=["导出"])

# WebSocket管理器
ws_manager = WebSocketManager()

@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "VCU智能模糊测试系统API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

# WebSocket端点 - 实时监控
@app.websocket("/ws/test-tasks/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket连接，用于实时推送测试任务状态"""
    await ws_manager.connect(websocket, task_id)
    try:
        while True:
            # 保持连接活跃，等待服务器推送消息
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, task_id)

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)

