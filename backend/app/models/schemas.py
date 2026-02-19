from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TestType(str, Enum):
    API = "api"
    UI = "ui"


class TestStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ERROR = "error"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Interface Schemas
class InterfaceBase(BaseModel):
    name: str = Field(..., description="接口名称")
    url: str = Field(..., description="接口URL")
    method: str = Field(..., description="请求方法")
    headers: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, Any]] = None
    response_example: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class InterfaceCreate(InterfaceBase):
    pass


class InterfaceResponse(InterfaceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Test Point Schemas
class TestPointBase(BaseModel):
    title: str
    description: Optional[str] = None
    test_type: TestType
    risk_level: RiskLevel = RiskLevel.MEDIUM
    category: Optional[str] = None


class TestPointCreate(TestPointBase):
    interface_id: Optional[int] = None
    page_id: Optional[int] = None


class TestPointResponse(TestPointBase):
    id: int
    interface_id: Optional[int]
    page_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Test Case Schemas
class TestCaseBase(BaseModel):
    name: str
    description: Optional[str] = None
    test_type: TestType
    code: str
    test_data: Optional[Dict[str, Any]] = None
    expected_result: Optional[str] = None
    tags: Optional[List[str]] = None


class TestCaseCreate(TestCaseBase):
    interface_id: Optional[int] = None
    page_id: Optional[int] = None
    test_point_id: Optional[int] = None


class TestCaseResponse(TestCaseBase):
    id: int
    interface_id: Optional[int]
    page_id: Optional[int]
    test_point_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Test Plan Schemas
class TestPlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    test_case_ids: Optional[List[int]] = None
    schedule: Optional[str] = None
    is_active: bool = True


class TestPlanCreate(TestPlanBase):
    pass


class TestPlanResponse(TestPlanBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Test Execution Schemas
class TestExecutionBase(BaseModel):
    test_case_id: Optional[int] = None
    test_plan_id: Optional[int] = None
    status: TestStatus = TestStatus.PENDING


class TestExecutionCreate(TestExecutionBase):
    pass


class TestExecutionResponse(TestExecutionBase):
    id: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration: Optional[int]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    log_path: Optional[str]
    screenshot_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Test Report Schemas
class OptimizationSuggestion(BaseModel):
    title: str
    description: str
    priority: str


class TestReportBase(BaseModel):
    title: str
    summary: Optional[str] = None
    total_cases: int = 0
    passed_cases: int = 0
    failed_cases: int = 0
    error_cases: int = 0
    pass_rate: Optional[str] = None
    coverage: Optional[str] = None
    risk_analysis: Optional[Dict[str, Any]] = None
    optimization_suggestions: Optional[List[Dict[str, Any]]] = None
    html_path: Optional[str] = None


class TestReportCreate(TestReportBase):
    execution_id: int


class TestReportResponse(TestReportBase):
    id: int
    execution_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# AI Request/Response Schemas
class AIAnalyzeInterfaceRequest(BaseModel):
    interface_id: int


class AIGenerateTestPointsRequest(BaseModel):
    interface_id: int


class AIGenerateTestCaseRequest(BaseModel):
    test_point_id: int


class AIAnalyzeReportRequest(BaseModel):
    execution_id: int

