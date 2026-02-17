"""Pytest Test Executor"""
import os
import subprocess
import json
import tempfile
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger


class PytestRunner:
    """Pytest执行引擎"""

    def __init__(self, workspace_dir: str = "test_workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True, parents=True)

    def execute_test_case(
        self,
        test_code: str,
        test_case_id: int,
        dependencies: Optional[list] = None
    ) -> Dict[str, Any]:
        """执行单个测试用例"""
        try:
            # 创建测试文件
            test_file = self._create_test_file(test_code, test_case_id)

            # 安装依赖
            if dependencies:
                self._install_dependencies(dependencies)

            # 执行测试
            start_time = datetime.utcnow()
            result = self._run_pytest(test_file)
            end_time = datetime.utcnow()

            duration = int((end_time - start_time).total_seconds())

            return {
                "status": result["status"],
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration": duration,
                "result": result,
                "log_path": result.get("log_path"),
                "error_message": result.get("error")
            }
        except Exception as e:
            logger.error(f"测试执行失败: {str(e)}")
            return {
                "status": "error",
                "error_message": str(e),
                "result": {}
            }

    def execute_test_plan(
        self,
        test_cases: list,
        plan_id: int
    ) -> Dict[str, Any]:
        """执行测试计划（多个用例）"""
        results = []
        total = len(test_cases)
        passed = 0
        failed = 0
        errors = 0

        for test_case in test_cases:
            result = self.execute_test_case(
                test_code=test_case["code"],
                test_case_id=test_case["id"],
                dependencies=test_case.get("dependencies")
            )

            results.append({
                "test_case_id": test_case["id"],
                "test_case_name": test_case["name"],
                "result": result
            })

            if result["status"] == "success":
                passed += 1
            elif result["status"] == "failed":
                failed += 1
            else:
                errors += 1

        return {
            "plan_id": plan_id,
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "pass_rate": f"{(passed/total*100):.2f}%" if total > 0 else "0%",
            "results": results
        }

    def _create_test_file(self, test_code: str, test_case_id: int) -> Path:
        """创建测试文件"""
        test_file = self.workspace_dir / f"test_case_{test_case_id}.py"
        test_file.write_text(test_code, encoding="utf-8")
        logger.info(f"创建测试文件: {test_file}")
        return test_file

    def _install_dependencies(self, dependencies: list):
        """安装测试依赖"""
        try:
            for dep in dependencies:
                logger.info(f"安装依赖: {dep}")
                subprocess.run(
                    ["pip", "install", dep],
                    check=True,
                    capture_output=True,
                    text=True
                )
        except subprocess.CalledProcessError as e:
            logger.warning(f"依赖安装失败: {e.stderr}")

    def _run_pytest(self, test_file: Path) -> Dict[str, Any]:
        """运行pytest"""
        # 生成报告路径
        report_dir = self.workspace_dir / "reports"
        report_dir.mkdir(exist_ok=True)

        html_report = report_dir / f"{test_file.stem}_report.html"
        json_report = report_dir / f"{test_file.stem}_report.json"
        log_file = report_dir / f"{test_file.stem}_log.txt"

        # 构建pytest命令
        cmd = [
            "pytest",
            str(test_file),
            f"--html={html_report}",
            "--self-contained-html",
            f"--json-report",
            f"--json-report-file={json_report}",
            "-v",
            "-s"
        ]

        try:
            # 执行pytest
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.workspace_dir)
            )

            # 保存日志
            log_file.write_text(result.stdout + "\n" + result.stderr, encoding="utf-8")

            # 解析结果
            status = "success" if result.returncode == 0 else "failed"

            # 读取JSON报告（如果存在）
            test_results = {}
            if json_report.exists():
                try:
                    test_results = json.loads(json_report.read_text(encoding="utf-8"))
                except:
                    pass

            return {
                "status": status,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "html_report": str(html_report),
                "json_report": str(json_report),
                "log_path": str(log_file),
                "test_results": test_results
            }
        except Exception as e:
            logger.error(f"Pytest执行失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "log_path": str(log_file)
            }


# 全局实例
pytest_runner = PytestRunner()

