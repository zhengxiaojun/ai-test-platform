"""Test Report API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import TestReport, TestExecution
from app.models.schemas import TestReportCreate, TestReportResponse
from app.core.ai_orchestrator import ai_orchestrator
from loguru import logger

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/", response_model=TestReportResponse)
def create_report(
    report: TestReportCreate,
    db: Session = Depends(get_db)
):
    """创建测试报告"""
    db_report = TestReport(**report.model_dump())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


@router.get("/{report_id}", response_model=TestReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db)):
    """获取测试报告详情"""
    report = db.query(TestReport).filter(TestReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    return report


@router.get("/", response_model=List[TestReportResponse])
def list_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取报告列表"""
    reports = db.query(TestReport).order_by(
        TestReport.created_at.desc()
    ).offset(skip).limit(limit).all()
    return reports


@router.post("/generate/{execution_id}")
def generate_report(execution_id: int, db: Session = Depends(get_db)):
    """AI生成测试报告"""
    execution = db.query(TestExecution).filter(
        TestExecution.id == execution_id
    ).first()
    if not execution:
        raise HTTPException(status_code=404, detail="执行记录不存在")

    try:
        # 准备执行结果数据
        execution_data = {
            "execution_id": execution.id,
            "test_case_id": execution.test_case_id,
            "status": execution.status.value if execution.status else "unknown",
            "start_time": execution.start_time.isoformat() if execution.start_time else None,
            "end_time": execution.end_time.isoformat() if execution.end_time else None,
            "duration": execution.duration,
            "result": execution.result,
            "error_message": execution.error_message
        }

        # AI分析生成报告
        analysis = ai_orchestrator.analyze_test_report(execution_data)

        # 计算统计数据
        total_cases = 1
        passed_cases = 1 if execution.status.value == "success" else 0
        failed_cases = 1 if execution.status.value == "failed" else 0
        error_cases = 1 if execution.status.value == "error" else 0
        pass_rate = f"{(passed_cases/total_cases*100):.2f}%"

        # 保存报告
        report = TestReport(
            execution_id=execution_id,
            title=f"测试报告 - {execution.test_case.name if execution.test_case else 'Unknown'}",
            summary=analysis.get("summary"),
            total_cases=total_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            error_cases=error_cases,
            pass_rate=pass_rate,
            coverage="N/A",
            risk_analysis=analysis.get("risk_analysis"),
            optimization_suggestions=analysis.get("optimization_suggestions"),
            html_path=execution.log_path
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        return {
            "message": "报告生成成功",
            "report_id": report.id,
            "summary": report.summary,
            "statistics": {
                "total": total_cases,
                "passed": passed_cases,
                "failed": failed_cases,
                "errors": error_cases,
                "pass_rate": pass_rate
            },
            "risk_analysis": report.risk_analysis,
            "optimization_suggestions": report.optimization_suggestions,
            "key_findings": analysis.get("key_findings"),
            "next_steps": analysis.get("next_steps")
        }
    except Exception as e:
        logger.error(f"报告生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.get("/execution/{execution_id}")
def get_report_by_execution(execution_id: int, db: Session = Depends(get_db)):
    """根据执行ID获取报告"""
    report = db.query(TestReport).filter(
        TestReport.execution_id == execution_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="该执行记录暂无报告")
    return report

