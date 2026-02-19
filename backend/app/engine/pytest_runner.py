"""Pytest Test Executor"""
import subprocess
import json
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger


class PytestRunner:
    """Pytest执行引擎"""

    def __init__(self, workspace_dir: str = "test_workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True, parents=True)
        self._check_pytest_plugins()

    def _check_pytest_plugins(self):
        """检查必需的pytest插件是否已安装"""
        required_plugins = {
            'pytest-json-report': 'pytest_jsonreport',
            'pytest-html': 'pytest_html'
        }

        missing_plugins = []
        for plugin_name, module_name in required_plugins.items():
            try:
                __import__(module_name)
                logger.info(f"✓ {plugin_name} 已安装")
            except ImportError:
                missing_plugins.append(plugin_name)
                logger.warning(f"✗ {plugin_name} 未安装")

        if missing_plugins:
            logger.warning(f"缺少以下pytest插件: {', '.join(missing_plugins)}")
            logger.info("正在尝试自动安装...")
            self._install_dependencies(missing_plugins)
        else:
            logger.info("所有必需的pytest插件已就绪")

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
        if not dependencies:
            return

        failed_dep = None
        try:
            for dep in dependencies:
                failed_dep = dep
                logger.info(f"安装依赖: {dep}")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", dep],
                    check=True,
                    capture_output=True,
                    text=True
                )
                logger.info(f"✓ {dep} 安装成功")
        except subprocess.CalledProcessError as e:
            logger.error(f"依赖安装失败: {failed_dep}")
            logger.error(f"错误信息: {e.stderr}")
            raise Exception(f"无法安装依赖 {failed_dep}: {e.stderr}")

    def _run_pytest(self, test_file: Path) -> Dict[str, Any]:
        """运行pytest"""
        # 生成报告路径
        report_dir = self.workspace_dir / "reports"
        report_dir.mkdir(exist_ok=True)

        html_report = report_dir / f"{test_file.stem}_report.html"
        json_report = report_dir / f"{test_file.stem}_report.json"
        log_file = report_dir / f"{test_file.stem}_log.txt"

        # 使用相对于workspace的文件名，因为cwd会设置为workspace_dir
        test_file_name = test_file.name

        # 报告路径也使用相对路径
        html_report_rel = f"reports/{test_file.stem}_report.html"
        json_report_rel = f"reports/{test_file.stem}_report.json"

        # 构建pytest命令
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            test_file_name,  # 使用文件名而不是完整路径
            f"--html={html_report_rel}",
            "--self-contained-html",
            f"--json-report",
            f"--json-report-file={json_report_rel}",
            "-v",
            "-s"
        ]

        try:
            logger.info(f"工作目录: {self.workspace_dir}")
            logger.info(f"测试文件: {test_file_name}")
            logger.info(f"执行命令: {' '.join(cmd)}")

            # 执行pytest
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.workspace_dir),
                timeout=300  # 5分钟超时
            )

            # 保存日志
            log_content = f"=== STDOUT ===\n{result.stdout}\n\n=== STDERR ===\n{result.stderr}\n\n=== RETURN CODE ===\n{result.returncode}"
            log_file.write_text(log_content, encoding="utf-8")
            logger.info(f"日志已保存到: {log_file}")

            # 检查是否有插件相关错误
            if "UsageError" in result.stderr or "unrecognized arguments" in result.stderr:
                error_msg = "pytest插件配置错误，请确保 pytest-json-report 和 pytest-html 已正确安装"
                logger.error(error_msg)
                logger.error(f"错误详情: {result.stderr}")
                return {
                    "status": "error",
                    "error": error_msg,
                    "stderr": result.stderr,
                    "log_path": str(log_file)
                }

            # 解析结果
            if result.returncode == 0:
                status = "success"
            elif result.returncode == 1:
                status = "failed"  # 测试失败
            else:
                status = "error"  # 其他错误

            # 读取JSON报告（如果存在）
            test_results = {}
            if json_report.exists():
                try:
                    test_results = json.loads(json_report.read_text(encoding="utf-8"))
                    logger.info(f"JSON报告已生成: {json_report}")
                except Exception as e:
                    logger.warning(f"解析JSON报告失败: {str(e)}")

            # 检查HTML报告
            if html_report.exists():
                logger.info(f"HTML报告已生成: {html_report}")
            else:
                logger.warning(f"HTML报告未生成: {html_report}")

            return {
                "status": status,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "html_report": str(html_report) if html_report.exists() else None,
                "json_report": str(json_report) if json_report.exists() else None,
                "log_path": str(log_file),
                "test_results": test_results
            }
        except subprocess.TimeoutExpired:
            error_msg = "测试执行超时（超过5分钟）"
            logger.error(error_msg)
            log_file.write_text(f"ERROR: {error_msg}", encoding="utf-8")
            return {
                "status": "error",
                "error": error_msg,
                "log_path": str(log_file)
            }
        except Exception as e:
            error_msg = f"Pytest执行失败: {str(e)}"
            logger.error(error_msg)
            log_file.write_text(f"ERROR: {error_msg}", encoding="utf-8")
            return {
                "status": "error",
                "error": error_msg,
                "log_path": str(log_file)
            }


# 全局实例
pytest_runner = PytestRunner()

