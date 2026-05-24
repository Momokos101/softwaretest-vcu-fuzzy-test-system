"""AutoTestDesign Tool V2 — FastAPI 入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.routers import requirements, risk_analysis, test_design, export, autotest_review

app = FastAPI(
    title="AutoTestDesign Tool API",
    description="VCU 模糊测试自动化设计工具后端（V2）",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(requirements.router, prefix="/api", tags=["需求管理"])
app.include_router(risk_analysis.router, prefix="/api", tags=["风险分析"])
app.include_router(test_design.router, prefix="/api", tags=["测试设计"])
app.include_router(autotest_review.router, prefix="/api", tags=["交互式评审"])
app.include_router(export.router, prefix="/api", tags=["导出"])


@app.get("/")
async def root():
    return {"message": "AutoTestDesign Tool API", "version": "2.0.0", "docs": "/docs"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
