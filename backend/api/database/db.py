"""
数据库操作
使用SQLite存储测试计划、任务、异常等数据
"""
import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from functools import wraps

def async_db_operation(func):
    """将同步数据库操作包装为异步"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return wrapper

class Database:
    """数据库操作类"""
    
    def __init__(self, db_path: str = "data/test_system.db"):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()
    
    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 测试计划表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_plans (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                test_mode TEXT,
                traditional_config TEXT,
                gan_config TEXT,
                constraint_config TEXT,
                baseline_log_path TEXT,
                created_at TEXT,
                updated_at TEXT,
                status TEXT
            )
        """)
        
        # 测试任务表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_tasks (
                id TEXT PRIMARY KEY,
                plan_id TEXT,
                status TEXT,
                traditional_stats TEXT,
                gan_stats TEXT,
                total_cases INTEGER,
                total_anomalies INTEGER,
                started_at TEXT,
                paused_at TEXT,
                completed_at TEXT,
                created_at TEXT,
                FOREIGN KEY (plan_id) REFERENCES test_plans(id)
            )
        """)
        
        # 异常记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anomalies (
                id TEXT PRIMARY KEY,
                task_id TEXT,
                anomaly_type TEXT,
                severity INTEGER,
                test_case TEXT,
                context TEXT,
                detected_at TEXT,
                source TEXT,
                reproducible INTEGER,
                min_reproduce_script TEXT,
                FOREIGN KEY (task_id) REFERENCES test_tasks(id)
            )
        """)
        
        # 约束统计表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS constraint_stats (
                task_id TEXT PRIMARY KEY,
                total_intercepted INTEGER,
                interception_reasons TEXT,
                enabled_rules TEXT,
                FOREIGN KEY (task_id) REFERENCES test_tasks(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    @async_db_operation
    def save_test_plan(self, plan_data: Dict[str, Any]):
        """保存测试计划"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO test_plans 
            (id, name, description, test_mode, traditional_config, gan_config, 
             constraint_config, baseline_log_path, created_at, updated_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            plan_data["id"],
            plan_data["name"],
            plan_data.get("description"),
            plan_data.get("test_mode"),
            json.dumps(plan_data.get("traditional_config")),
            json.dumps(plan_data.get("gan_config")),
            json.dumps(plan_data.get("constraint_config")),
            plan_data.get("baseline_log_path"),
            plan_data.get("created_at"),
            plan_data.get("updated_at"),
            plan_data.get("status", "draft")
        ))
        
        conn.commit()
        conn.close()
    
    @async_db_operation
    def get_test_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """获取测试计划"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM test_plans WHERE id = ?", (plan_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = dict(row)
            data["traditional_config"] = json.loads(data["traditional_config"]) if data["traditional_config"] else None
            data["gan_config"] = json.loads(data["gan_config"]) if data["gan_config"] else None
            data["constraint_config"] = json.loads(data["constraint_config"]) if data["constraint_config"] else None
            return data
        return None
    
    @async_db_operation
    def get_test_plans(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """获取测试计划列表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM test_plans ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, skip))
        rows = cursor.fetchall()
        conn.close()
        
        plans = []
        for row in rows:
            data = dict(row)
            data["traditional_config"] = json.loads(data["traditional_config"]) if data["traditional_config"] else None
            data["gan_config"] = json.loads(data["gan_config"]) if data["gan_config"] else None
            data["constraint_config"] = json.loads(data["constraint_config"]) if data["constraint_config"] else None
            plans.append(data)
        
        return plans
    
    @async_db_operation
    def update_test_plan(self, plan_id: str, plan_data: Dict[str, Any]):
        """更新测试计划"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE test_plans 
            SET name = ?, description = ?, test_mode = ?, traditional_config = ?, 
                gan_config = ?, constraint_config = ?, baseline_log_path = ?, 
                updated_at = ?, status = ?
            WHERE id = ?
        """, (
            plan_data["name"],
            plan_data.get("description"),
            plan_data.get("test_mode"),
            json.dumps(plan_data.get("traditional_config")),
            json.dumps(plan_data.get("gan_config")),
            json.dumps(plan_data.get("constraint_config")),
            plan_data.get("baseline_log_path"),
            plan_data.get("updated_at"),
            plan_data.get("status", "draft"),
            plan_id
        ))
        
        conn.commit()
        conn.close()
    
    @async_db_operation
    def delete_test_plan(self, plan_id: str) -> bool:
        """删除测试计划"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM test_plans WHERE id = ?", (plan_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    @async_db_operation
    def save_test_task(self, task_data: Dict[str, Any]):
        """保存测试任务"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO test_tasks 
            (id, plan_id, status, traditional_stats, gan_stats, total_cases, 
             total_anomalies, started_at, paused_at, completed_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_data["id"],
            task_data["plan_id"],
            task_data.get("status"),
            json.dumps(task_data.get("traditional_stats", {})),
            json.dumps(task_data.get("gan_stats", {})),
            task_data.get("total_cases", 0),
            task_data.get("total_anomalies", 0),
            task_data.get("started_at"),
            task_data.get("paused_at"),
            task_data.get("completed_at"),
            task_data.get("created_at")
        ))
        
        conn.commit()
        conn.close()
    
    @async_db_operation
    def get_test_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取测试任务"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM test_tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = dict(row)
            data["traditional_stats"] = json.loads(data["traditional_stats"]) if data["traditional_stats"] else {}
            data["gan_stats"] = json.loads(data["gan_stats"]) if data["gan_stats"] else {}
            return data
        return None
    
    @async_db_operation
    def update_test_task(self, task_id: str, task_data: Dict[str, Any]):
        """更新测试任务"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE test_tasks SET
                status = ?,
                traditional_stats = ?,
                gan_stats = ?,
                total_cases = ?,
                total_anomalies = ?,
                started_at = ?,
                paused_at = ?,
                completed_at = ?
            WHERE id = ?
        """, (
            task_data.get("status"),
            json.dumps(task_data.get("traditional_stats", {})),
            json.dumps(task_data.get("gan_stats", {})),
            task_data.get("total_cases", 0),
            task_data.get("total_anomalies", 0),
            task_data.get("started_at"),
            task_data.get("paused_at"),
            task_data.get("completed_at"),
            task_id
        ))
        
        conn.commit()
        conn.close()
    
    @async_db_operation
    def get_test_tasks(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """获取测试任务列表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM test_tasks ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, skip))
        rows = cursor.fetchall()
        conn.close()
        
        tasks = []
        for row in rows:
            data = dict(row)
            data["traditional_stats"] = json.loads(data["traditional_stats"]) if data["traditional_stats"] else {}
            data["gan_stats"] = json.loads(data["gan_stats"]) if data["gan_stats"] else {}
            tasks.append(data)
        
        return tasks
    
    @async_db_operation
    def get_task_anomalies(
        self, 
        task_id: str, 
        top_n: int = 10,
        source: Optional[str] = None,
        min_severity: int = 1
    ) -> List[Dict[str, Any]]:
        """获取任务的异常列表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM anomalies WHERE task_id = ? AND severity >= ?"
        params = [task_id, min_severity]
        
        if source:
            query += " AND source = ?"
            params.append(source)
        
        query += " ORDER BY severity DESC, detected_at DESC LIMIT ?"
        params.append(top_n)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        anomalies = []
        for row in rows:
            data = dict(row)
            data["test_case"] = json.loads(data["test_case"]) if data["test_case"] else {}
            data["context"] = json.loads(data["context"]) if data["context"] else {}
            data["min_reproduce_script"] = json.loads(data["min_reproduce_script"]) if data["min_reproduce_script"] else None
            data["reproducible"] = bool(data["reproducible"])
            anomalies.append(data)
        
        return anomalies
    
    @async_db_operation
    def get_constraint_stats(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取约束统计"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM constraint_stats WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = dict(row)
            data["interception_reasons"] = json.loads(data["interception_reasons"]) if data["interception_reasons"] else {}
            data["enabled_rules"] = json.loads(data["enabled_rules"]) if data["enabled_rules"] else []
            return data
        return None



