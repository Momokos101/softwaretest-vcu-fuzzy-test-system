#!/usr/bin/env python3
"""
启动FastAPI服务器
"""
import uvicorn
import os
import sys

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # 从环境变量读取配置，或使用默认值
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    
    print(f"启动VCU智能模糊测试系统API服务器...")
    print(f"访问地址: http://{host}:{port}")
    print(f"API文档: http://{host}:{port}/docs")
    print(f"自动重载: {reload}")
    
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
