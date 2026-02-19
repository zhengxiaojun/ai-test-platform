"""Test Case API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import json
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
    test_type: str = None,
    name: str = None,
    tags: str = None,
    db: Session = Depends(get_db)
):
    """获取测试用例列表（支持多条件筛选）"""
    query = db.query(TestCase)

    # 筛选条件
    if interface_id:
        query = query.filter(TestCase.interface_id == interface_id)
    if test_type:
        query = query.filter(TestCase.test_type == test_type)
    if name:
        query = query.filter(TestCase.name.contains(name))
    if tags:
        # 标签筛选（假设tags是JSON数组）
        query = query.filter(TestCase.tags.contains(tags))

    test_cases = query.order_by(TestCase.created_at.desc()).offset(skip).limit(limit).all()
    return test_cases


@router.put("/{test_case_id}", response_model=TestCaseResponse)
def update_test_case(
    test_case_id: int,
    test_case: TestCaseCreate,
    db: Session = Depends(get_db)
):
    """更新测试用例"""
    db_test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not db_test_case:
        raise HTTPException(status_code=404, detail="测试用例不存在")

    # 更新字段
    for key, value in test_case.model_dump(exclude_unset=True).items():
        setattr(db_test_case, key, value)

    db_test_case.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_test_case)
    return db_test_case


@router.delete("/{test_case_id}")
def delete_test_case(test_case_id: int, db: Session = Depends(get_db)):
    """删除测试用例"""
    test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not test_case:
        raise HTTPException(status_code=404, detail="测试用例不存在")
    db.delete(test_case)
    db.commit()
    return {"message": "删除成功"}


@router.post("/batch-delete")
def batch_delete_test_cases(
    test_case_ids: List[int],
    db: Session = Depends(get_db)
):
    """批量删除测试用例"""
    try:
        deleted_count = db.query(TestCase).filter(
            TestCase.id.in_(test_case_ids)
        ).delete(synchronize_session=False)
        db.commit()
        return {
            "message": f"成功删除 {deleted_count} 个测试用例",
            "deleted_count": deleted_count
        }
    except Exception as e:
        db.rollback()
        logger.error(f"批量删除失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量删除失败: {str(e)}")


@router.post("/batch-execute")
async def batch_execute_test_cases(
    test_case_ids: List[int],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """批量执行测试用例"""
    test_cases = db.query(TestCase).filter(
        TestCase.id.in_(test_case_ids)
    ).all()

    if not test_cases:
        raise HTTPException(status_code=404, detail="未找到任何测试用例")

    execution_ids = []
    for test_case in test_cases:
        # 创建执行记录
        execution = TestExecution(
            test_case_id=test_case.id,
            status=TestStatus.PENDING,
            start_time=datetime.utcnow()
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
        execution_ids.append(execution.id)

        # 在后台执行测试
        background_tasks.add_task(
            _execute_test_in_background,
            execution.id,
            test_case.code,
            test_case.id
        )

    return {
        "message": f"已提交 {len(execution_ids)} 个测试用例执行",
        "execution_ids": execution_ids
    }


@router.post("/{test_case_id}/clone", response_model=TestCaseResponse)
def clone_test_case(
    test_case_id: int,
    db: Session = Depends(get_db)
):
    """克隆测试用例"""
    original = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="测试用例不存在")

    # 创建副本
    cloned = TestCase(
        interface_id=original.interface_id,
        page_id=original.page_id,
        test_point_id=original.test_point_id,
        name=f"{original.name} (副本)",
        description=original.description,
        test_type=original.test_type,
        code=original.code,
        test_data=original.test_data,
        expected_result=original.expected_result,
        tags=original.tags
    )
    db.add(cloned)
    db.commit()
    db.refresh(cloned)

    return cloned


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

        # 处理test_data和expected_result
        # SQLite需要JSON字段手动序列化
        test_data = case_data.get("test_data")
        expected_result = case_data.get("test_data", {}).get("expected")

        # 如果expected_result是dict，转为JSON字符串（因为字段类型是Text）
        if expected_result and isinstance(expected_result, dict):
            expected_result = json.dumps(expected_result, ensure_ascii=False)

        # 保存测试用例
        test_case = TestCase(
            interface_id=interface.id,
            test_point_id=test_point_id,
            name=case_data["test_case_name"],
            description=case_data["description"],
            test_type="api",
            code=case_data["code"],
            test_data=test_data,  # JSON字段会自动处理
            expected_result=expected_result
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

        # 更新执行结果 - 存储完整的result对象
        execution.status = TestStatus.SUCCESS if result["status"] == "success" else TestStatus.FAILED
        execution.end_time = datetime.utcnow()
        execution.duration = result.get("duration")
        # 存储完整的result字典，包含所有执行详情
        execution.result = result
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

    return JSONResponse(content=[
        {
            "id": ex.id,
            "test_case_id": ex.test_case_id,
            "status": ex.status.value if hasattr(ex.status, 'value') else str(ex.status),
            "start_time": ex.start_time.isoformat() if ex.start_time else None,
            "end_time": ex.end_time.isoformat() if ex.end_time else None,
            "duration": ex.duration,
            "result": ex.result,
            "error_message": ex.error_message,
            "created_at": ex.created_at.isoformat() if ex.created_at else None
        }
        for ex in executions
    ])


@router.get("/export/json")
def export_test_cases_json(
    interface_id: int = None,
    test_type: str = None,
    db: Session = Depends(get_db)
):
    """导出测试用例（JSON格式）"""
    query = db.query(TestCase)

    if interface_id:
        query = query.filter(TestCase.interface_id == interface_id)
    if test_type:
        query = query.filter(TestCase.test_type == test_type)

    test_cases = query.all()

    # 转换为可导出的格式
    export_data = []
    for tc in test_cases:
        export_data.append({
            "id": tc.id,
            "name": tc.name,
            "description": tc.description,
            "test_type": tc.test_type,
            "code": tc.code,
            "test_data": tc.test_data,
            "expected_result": tc.expected_result,
            "interface_id": tc.interface_id,
            "test_point_id": tc.test_point_id,
            "tags": tc.tags,
            "created_at": tc.created_at.isoformat() if tc.created_at else None,
            "updated_at": tc.updated_at.isoformat() if tc.updated_at else None,
        })

    return JSONResponse(
        content={
            "total": len(export_data),
            "data": export_data,
            "export_time": datetime.utcnow().isoformat()
        },
        headers={
            "Content-Disposition": f"attachment; filename=test_cases_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        }
    )


@router.post("/import/json")
def import_test_cases_json(
    test_cases: List[dict],
    db: Session = Depends(get_db)
):
    """导入测试用例（JSON格式）"""
    try:
        imported_count = 0
        skipped_count = 0
        errors = []

        for tc_data in test_cases:
            try:
                # 检查是否存在相同名称的测试用例
                existing = db.query(TestCase).filter(
                    TestCase.name == tc_data.get("name")
                ).first()

                if existing:
                    skipped_count += 1
                    continue

                # 创建新测试用例
                test_case = TestCase(
                    name=tc_data.get("name"),
                    description=tc_data.get("description"),
                    test_type=tc_data.get("test_type", "api"),
                    code=tc_data.get("code", ""),
                    test_data=tc_data.get("test_data"),
                    expected_result=tc_data.get("expected_result"),
                    interface_id=tc_data.get("interface_id"),
                    test_point_id=tc_data.get("test_point_id"),
                    tags=tc_data.get("tags")
                )
                db.add(test_case)
                imported_count += 1
            except Exception as e:
                errors.append(f"导入 '{tc_data.get('name', 'unknown')}' 失败: {str(e)}")

        db.commit()

        return {
            "message": "导入完成",
            "imported_count": imported_count,
            "skipped_count": skipped_count,
            "errors": errors
        }
    except Exception as e:
        db.rollback()
        logger.error(f"导入失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")



