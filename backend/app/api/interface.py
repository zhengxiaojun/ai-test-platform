"""Interface API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import Interface, TestPoint
from app.models.schemas import (
    InterfaceCreate,
    InterfaceResponse,
    TestPointResponse
)
from app.core.ai_orchestrator import ai_orchestrator
from loguru import logger

router = APIRouter(prefix="/api/interfaces", tags=["interfaces"])


@router.post("/", response_model=InterfaceResponse)
def create_interface(
    interface: InterfaceCreate,
    db: Session = Depends(get_db)
):
    """创建接口"""
    db_interface = Interface(**interface.model_dump())
    db.add(db_interface)
    db.commit()
    db.refresh(db_interface)
    return db_interface


@router.get("/{interface_id}", response_model=InterfaceResponse)
def get_interface(interface_id: int, db: Session = Depends(get_db)):
    """获取接口详情"""
    interface = db.query(Interface).filter(Interface.id == interface_id).first()
    if not interface:
        raise HTTPException(status_code=404, detail="接口不存在")
    return interface


@router.get("/", response_model=List[InterfaceResponse])
def list_interfaces(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取接口列表"""
    interfaces = db.query(Interface).offset(skip).limit(limit).all()
    return interfaces


@router.delete("/{interface_id}")
def delete_interface(interface_id: int, db: Session = Depends(get_db)):
    """删除接口"""
    interface = db.query(Interface).filter(Interface.id == interface_id).first()
    if not interface:
        raise HTTPException(status_code=404, detail="接口不存在")
    db.delete(interface)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{interface_id}/analyze")
def analyze_interface(interface_id: int, db: Session = Depends(get_db)):
    """AI分析接口，生成测试点"""
    interface = db.query(Interface).filter(Interface.id == interface_id).first()
    if not interface:
        raise HTTPException(status_code=404, detail="接口不存在")

    try:
        # 准备接口数据
        interface_data = {
            "name": interface.name,
            "url": interface.url,
            "method": interface.method,
            "headers": interface.headers,
            "params": interface.params,
            "response_example": interface.response_example,
            "description": interface.description
        }

        # AI分析
        analysis_result = ai_orchestrator.analyze_interface(interface_data)

        # 保存测试点
        test_points = []
        for tp_data in analysis_result.get("test_points", []):
            test_point = TestPoint(
                interface_id=interface_id,
                title=tp_data["title"],
                description=tp_data["description"],
                test_type="api",
                risk_level=tp_data["risk_level"],
                category=tp_data["category"]
            )
            db.add(test_point)
            test_points.append(test_point)

        db.commit()

        return {
            "message": "分析完成",
            "test_points_count": len(test_points),
            "risk_summary": analysis_result.get("risk_summary"),
            "suggestions": analysis_result.get("suggestions"),
            "test_points": [
                {
                    "id": tp.id,
                    "title": tp.title,
                    "description": tp.description,
                    "risk_level": tp.risk_level,
                    "category": tp.category
                }
                for tp in test_points
            ]
        }
    except Exception as e:
        logger.error(f"接口分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/{interface_id}/test-points", response_model=List[TestPointResponse])
def get_interface_test_points(interface_id: int, db: Session = Depends(get_db)):
    """获取接口的测试点列表"""
    test_points = db.query(TestPoint).filter(
        TestPoint.interface_id == interface_id
    ).all()
    return test_points

