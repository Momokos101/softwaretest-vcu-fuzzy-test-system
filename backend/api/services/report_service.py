"""
测试报告服务
"""
import os
from typing import Optional
from datetime import datetime
import json

from api.models.schemas import TestReportRequest, TestReportResponse, MethodComparison
from api.database.db import Database
from api.services.test_task_service import TestTaskService

class ReportService:
    def __init__(self):
        self.db = Database()
        self.task_service = TestTaskService()
        self.reports_dir = "data/reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    async def generate_report(self, request: TestReportRequest) -> TestReportResponse:
        """生成测试报告"""
        task = await self.task_service.get_task(request.task_id)
        if not task:
            raise ValueError(f"测试任务 {request.task_id} 不存在")
        
        # 生成报告内容
        report_content = await self._generate_report_content(task, request.include_comparison)
        
        # 保存报告文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{request.task_id}_{timestamp}.{request.format}"
        file_path = os.path.join(self.reports_dir, filename)
        
        if request.format == "json":
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(report_content, f, ensure_ascii=False, indent=2)
        elif request.format == "markdown":
            # report_content是dict，需要转换为markdown格式
            markdown_content = self._dict_to_markdown(report_content)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
        else:  # pdf
            # TODO: 使用WeasyPrint或Jinja2生成PDF
            markdown_content = self._dict_to_markdown(report_content)
            with open(file_path.replace(".pdf", ".md"), "w", encoding="utf-8") as f:
                f.write(markdown_content)
            file_path = file_path.replace(".pdf", ".md")
        
        return TestReportResponse(
            task_id=request.task_id,
            report_path=file_path,
            format=request.format,
            generated_at=datetime.now(),
            comparison=report_content.get("comparison")
        )
    
    def _dict_to_markdown(self, data: dict) -> str:
        """将字典转换为Markdown格式"""
        lines = []
        lines.append("# 测试报告\n")
        
        if "task_id" in data:
            lines.append(f"**任务ID**: {data['task_id']}\n")
        if "generated_at" in data:
            lines.append(f"**生成时间**: {data['generated_at']}\n")
        lines.append("\n")
        
        if "comparison" in data:
            lines.append("## 方法对比\n")
            comp = data["comparison"]
            if "traditional" in comp:
                lines.append("### 传统测试\n")
                lines.append(f"- 用例数: {comp['traditional'].get('cases', 0)}\n")
                lines.append(f"- 异常数: {comp['traditional'].get('anomalies', 0)}\n")
                lines.append(f"- 异常率: {comp['traditional'].get('anomaly_rate', 0)*100:.2f}%\n")
            if "gan" in comp:
                lines.append("### GAN测试\n")
                lines.append(f"- 用例数: {comp['gan'].get('cases', 0)}\n")
                lines.append(f"- 异常数: {comp['gan'].get('anomalies', 0)}\n")
                lines.append(f"- 异常率: {comp['gan'].get('anomaly_rate', 0)*100:.2f}%\n")
        
        return "\n".join(lines)
    
    async def _generate_report_content(self, task, include_comparison: bool) -> dict:
        """生成报告内容"""
        content = {
            "task_id": task.id,
            "plan_id": task.plan_id,
            "status": task.status,
            "total_cases": task.total_cases,
            "total_anomalies": task.total_anomalies,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "traditional_stats": task.traditional_stats,
            "gan_stats": task.gan_stats
        }
        
        if include_comparison:
            content["comparison"] = await self._generate_comparison(task)
        
        return content
    
    async def _generate_comparison(self, task) -> MethodComparison:
        """生成方法对比"""
        traditional = task.traditional_stats
        gan = task.gan_stats
        
        summary = f"""
传统测试方法: 生成{traditional.get('cases', 0)}个用例，发现{traditional.get('anomalies', 0)}个异常，异常率{traditional.get('anomaly_rate', 0.0):.2%}
GAN测试方法: 生成{gan.get('cases', 0)}个用例，发现{gan.get('anomalies', 0)}个异常，异常率{gan.get('anomaly_rate', 0.0):.2%}
        """.strip()
        
        return MethodComparison(
            traditional=traditional,
            gan=gan,
            summary=summary
        )
    
    async def get_report_file_path(self, task_id: str, format: str) -> Optional[str]:
        """获取报告文件路径"""
        # 查找最新的报告文件
        if not os.path.exists(self.reports_dir):
            return None
        
        pattern = f"report_{task_id}_*.{format}"
        import glob
        files = glob.glob(os.path.join(self.reports_dir, pattern))
        
        if files:
            # 返回最新的文件
            return max(files, key=os.path.getmtime)
        
        return None
    
    async def get_method_comparison(self, task_id: str) -> MethodComparison:
        """获取方法对比数据"""
        task = await self.task_service.get_task(task_id)
        if not task:
            raise ValueError(f"测试任务 {task_id} 不存在")
        
        return await self._generate_comparison(task)



