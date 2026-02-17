"""Test Case API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import TestCase, TestPoint, Interface, TestExecution, TestStatus
from app.models.schemas import TestCaseCreate, TestCaseResponse
from app.core.ai_orchestrator import ai_orchestrator
from app.engine.pytest_runner import pytest_runner
from datetime import datetime
from loguru import logger

router = APIRouter(prefix="/api/testcases", tags=["testcases"])


@router.post("/", response_model=TestCaseResponse)
def create_test_case(
    test_case: TestCaseCreate,
    db: Session = Depends(get_db)
):
    """创建测试用例"""
    db_test_case = TestCase(**test_case.model_dump())
    db.add(db_test_case)
    db.commit()
    db.refresh(db_test_case)
    return db_test_case


@router.get("/{test_case_id}", response_model=TestCaseResponse)
def get_test_case(test_case_id: int, db: Session = Depends(get_db)):
    """获取测试用例详情"""
    test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not test_case:
        raise HTTPException(status_code=404, detail="测试用例不存在")
    return test_case


@router.get("/", response_model=List[TestCaseResponse])
def list_test_cases(
    skip: int = 0,
    limit: int = 100,
    interface_id: int = None,
    db: Session = Depends(get_db)
):
    """获取测试用例列表"""
    query = db.query(TestCase)
    if interface_id:
        query = query.filter(TestCase.interface_id == interface_id)
    test_cases = query.offset(skip).limit(limit).all()
    return test_cases


@router.delete("/{test_case_id}")
def delete_test_case(test_case_id: int, db: Session = Depends(get_db)):
    """删除测试用例"""
    test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not test_case:
        raise HTTPException(status_code=404, detail="测试用例不存在")
    db.delete(test_case)
    db.commit()
    return {"message": "删除成功"}


@router.post("/generate/{test_point_id}")
def generate_test_case_from_point(
    test_point_id: int,
    db: Session = Depends(get_db)
):
    """根据测试点生成测试用例"""
    test_point = db.query(TestPoint).filter(TestPoint.id == test_point_id).first()
    if not test_point:
        raise HTTPException(status_code=404, detail="测试点不存在")

    try:
        # 获取接口信息
        interface = None
        if test_point.interface_id:
            interface = db.query(Interface).filter(
                Interface.id == test_point.interface_id
            ).first()

        if not interface:
            raise HTTPException(status_code=400, detail="未找到关联的接口信息")

        # 准备数据
        test_point_data = {
            "title": test_point.title,
            "description": test_point.description,
            "category": test_point.category,
            "risk_level": test_point.risk_level
        }

        interface_data = {
            "url": interface.url,
            "method": interface.method,
            "params": interface.params,
            "headers": interface.headers,
            "response_example": interface.response_example
        }

        # AI生成测试用例
        case_data = ai_orchestrator.generate_test_case(
            test_point_data,
            interface_data
        )

        # 保存测试用例
        test_case = TestCase(
            interface_id=interface.id,
            test_point_id=test_point_id,
            name=case_data["test_case_name"],
            description=case_data["description"],
            test_type="api",
            code=case_data["code"],
            test_data=case_data.get("test_data"),
            expected_result=case_data.get("test_data", {}).get("expected")
        )
        db.add(test_case)
        db.commit()
        db.refresh(test_case)

        return {
            "message": "测试用例生成成功",
            "test_case": {
                "id": test_case.id,
                "name": test_case.name,
                "description": test_case.description,
                "code": test_case.code,
                "test_data": test_case.test_data
            },
            "dependencies": case_data.get("dependencies", []),
            "notes": case_data.get("notes")
        }
    except Exception as e:
        logger.error(f"测试用例生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.post("/{test_case_id}/execute")
async def execute_test_case(
    test_case_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """执行测试用例"""
    test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not test_case:
        raise HTTPException(status_code=404, detail="测试用例不存在")

    # 创建执行记录
    execution = TestExecution(
        test_case_id=test_case_id,
        status=TestStatus.PENDING,
        start_time=datetime.utcnow()
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)

    # 在后台执行测试
    background_tasks.add_task(
        _execute_test_in_background,
        execution.id,
        test_case.code,
        test_case.id
    )

    return {
        "message": "测试已提交执行",
        "execution_id": execution.id,
        "status": "pending"
    }


def _execute_test_in_background(execution_id: int, test_code: str, test_case_id: int):
    """后台执行测试"""
    from app.database import SessionLocal
    db = SessionLocal()

    try:
        execution = db.query(TestExecution).filter(
            TestExecution.id == execution_id
        ).first()

        if not execution:
            return

        # 更新状态为运行中
        execution.status = TestStatus.RUNNING
        execution.start_time = datetime.utcnow()
        db.commit()

        # 执行测试
        result = pytest_runner.execute_test_case(
            test_code=test_code,
            test_case_id=test_case_id
        )

        # 更新执行结果
        execution.status = TestStatus.SUCCESS if result["status"] == "success" else TestStatus.FAILED
        execution.end_time = datetime.utcnow()
        execution.duration = result.get("duration")
        execution.result = result.get("result")
        execution.error_message = result.get("error_message")
        execution.log_path = result.get("log_path")

        db.commit()

        logger.info(f"测试执行完成: execution_id={execution_id}, status={execution.status}")
    except Exception as e:
        logger.error(f"测试执行失败: {str(e)}")
        if execution:
            execution.status = TestStatus.ERROR
            execution.error_message = str(e)
            execution.end_time = datetime.utcnow()
            db.commit()
    finally:
        db.close()


@router.get("/{test_case_id}/executions")
def get_test_case_executions(
    test_case_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取测试用例的执行历史"""
    executions = db.query(TestExecution).filter(
        TestExecution.test_case_id == test_case_id
    ).order_by(TestExecution.created_at.desc()).offset(skip).limit(limit).all()

    return [
        {
            "id": ex.id,
            "status": ex.status,
            "start_time": ex.start_time,
            "end_time": ex.end_time,
            "duration": ex.duration,
            "error_message": ex.error_message,
            "created_at": ex.created_at
        }
        for ex in executions
    ]

