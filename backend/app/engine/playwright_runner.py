"""Playwright UI Test Executor"""
import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page
from loguru import logger


class PlaywrightRunner:
    """Playwright UI测试执行引擎"""

    def __init__(self, workspace_dir: str = "test_workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True, parents=True)
        self.screenshots_dir = self.workspace_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
        self.videos_dir = self.workspace_dir / "videos"
        self.videos_dir.mkdir(exist_ok=True)

    async def execute_ui_test(
        self,
        test_code: str,
        test_case_id: int,
        url: str,
        headless: bool = True
    ) -> Dict[str, Any]:
        """执行UI测试用例"""
        try:
            start_time = datetime.utcnow()

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=headless)
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    record_video_dir=str(self.videos_dir) if not headless else None
                )
                page = await context.new_page()

                # 执行测试
                result = await self._execute_test_script(
                    page,
                    test_code,
                    url,
                    test_case_id
                )

                await browser.close()

            end_time = datetime.utcnow()
            duration = int((end_time - start_time).total_seconds())

            return {
                "status": result["status"],
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration": duration,
                "result": result,
                "screenshot_path": result.get("screenshot_path"),
                "error_message": result.get("error")
            }
        except Exception as e:
            logger.error(f"UI测试执行失败: {str(e)}")
            return {
                "status": "error",
                "error_message": str(e),
                "result": {}
            }

    async def _execute_test_script(
        self,
        page: Page,
        test_code: str,
        url: str,
        test_case_id: int
    ) -> Dict[str, Any]:
        """执行测试脚本"""
        try:
            # 导航到页面
            await page.goto(url, wait_until="networkidle")

            # 创建测试上下文
            test_context = {
                "page": page,
                "url": url,
                "results": []
            }

            # 执行测试代码（这里简化处理，实际应该更安全）
            # 在生产环境中应该使用更安全的方式执行用户代码
            exec(test_code, {"context": test_context, "asyncio": asyncio})

            # 截图
            screenshot_path = self.screenshots_dir / f"test_case_{test_case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)

            return {
                "status": "success",
                "screenshot_path": str(screenshot_path),
                "results": test_context.get("results", [])
            }
        except Exception as e:
            logger.error(f"测试脚本执行失败: {str(e)}")

            # 尝试截图
            screenshot_path = None
            try:
                screenshot_path = self.screenshots_dir / f"error_{test_case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await page.screenshot(path=str(screenshot_path))
            except:
                pass

            return {
                "status": "failed",
                "error": str(e),
                "screenshot_path": str(screenshot_path) if screenshot_path else None
            }

    async def analyze_page(self, url: str) -> Dict[str, Any]:
        """分析页面DOM结构"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto(url, wait_until="networkidle")

                # 获取页面信息
                title = await page.title()

                # 获取主要元素
                elements = await page.evaluate("""
                    () => {
                        const buttons = Array.from(document.querySelectorAll('button')).map(b => ({
                            type: 'button',
                            text: b.innerText,
                            id: b.id,
                            class: b.className
                        }));
                        const inputs = Array.from(document.querySelectorAll('input')).map(i => ({
                            type: 'input',
                            inputType: i.type,
                            name: i.name,
                            id: i.id,
                            placeholder: i.placeholder
                        }));
                        const links = Array.from(document.querySelectorAll('a')).map(a => ({
                            type: 'link',
                            text: a.innerText,
                            href: a.href
                        }));
                        return { buttons, inputs, links };
                    }
                """)

                # 截图
                screenshot_path = self.screenshots_dir / f"page_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await page.screenshot(path=str(screenshot_path), full_page=True)

                await browser.close()

                return {
                    "title": title,
                    "url": url,
                    "elements": elements,
                    "screenshot_path": str(screenshot_path)
                }
        except Exception as e:
            logger.error(f"页面分析失败: {str(e)}")
            raise


# 全局实例
playwright_runner = PlaywrightRunner()

