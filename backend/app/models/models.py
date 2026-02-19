from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


class TestType(str, enum.Enum):
    API = "api"
    UI = "ui"


class TestStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ERROR = "error"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Interface(Base):
    """接口信息表"""
    __tablename__ = "interfaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="接口名称")
    url = Column(String(512), nullable=False, comment="接口URL")
    method = Column(String(10), nullable=False, comment="请求方法")
    headers = Column(JSON, comment="请求头")
    params = Column(JSON, comment="请求参数结构")
    response_example = Column(JSON, comment="响应示例")
    description = Column(Text, comment="接口描述")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_points = relationship("TestPoint", back_populates="interface", cascade="all, delete-orphan")
    test_cases = relationship("TestCase", back_populates="interface", cascade="all, delete-orphan")


class PageInfo(Base):
    """页面信息表"""
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="页面名称")
    url = Column(String(512), nullable=False, comment="页面URL")
    description = Column(Text, comment="页面描述")
    screenshot_path = Column(String(512), comment="截图路径")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    test_points = relationship("TestPoint", back_populates="page", cascade="all, delete-orphan")
    test_cases = relationship("TestCase", back_populates="page", cascade="all, delete-orphan")


class TestPoint(Base):
    """测试点表"""
    __tablename__ = "test_points"

    id = Column(Integer, primary_key=True, index=True)
    interface_id = Column(Integer, ForeignKey("interfaces.id"), nullable=True)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=True)
    title = Column(String(255), nullable=False, comment="测试点标题")
    description = Column(Text, comment="测试点描述")
    test_type = Column(Enum(TestType), nullable=False, comment="测试类型")
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.MEDIUM, comment="风险等级")
    category = Column(String(100), comment="测试分类：边界值/异常/安全等")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    interface = relationship("Interface", back_populates="test_points")
    page = relationship("PageInfo", back_populates="test_points")
    test_cases = relationship("TestCase", back_populates="test_point", cascade="all, delete-orphan")


class TestCase(Base):
    """测试用例表"""
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    interface_id = Column(Integer, ForeignKey("interfaces.id"), nullable=True)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=True)
    test_point_id = Column(Integer, ForeignKey("test_points.id"), nullable=True)
    name = Column(String(255), nullable=False, comment="用例名称")
    description = Column(Text, comment="用例描述")
    test_type = Column(Enum(TestType), nullable=False, comment="测试类型")
    code = Column(Text, nullable=False, comment="测试代码")
    test_data = Column(JSON, comment="测试数据")
    expected_result = Column(Text, comment="预期结果")
    tags = Column(JSON, comment="标签列表")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    interface = relationship("Interface", back_populates="test_cases")
    page = relationship("PageInfo", back_populates="test_cases")
    test_point = relationship("TestPoint", back_populates="test_cases")
    executions = relationship("TestExecution", back_populates="test_case", cascade="all, delete-orphan")


class TestPlan(Base):
    """测试计划表"""
    __tablename__ = "test_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="计划名称")
    description = Column(Text, comment="计划描述")
    test_case_ids = Column(JSON, comment="测试用例ID列表")
    schedule = Column(String(100), comment="定时执行配置")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    executions = relationship("TestExecution", back_populates="test_plan", cascade="all, delete-orphan")


class TestExecution(Base):
    """测试执行记录表"""
    __tablename__ = "test_executions"

    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=True)
    test_plan_id = Column(Integer, ForeignKey("test_plans.id"), nullable=True)
    status = Column(Enum(TestStatus), default=TestStatus.PENDING, comment="执行状态")
    start_time = Column(DateTime, comment="开始时间")
    end_time = Column(DateTime, comment="结束时间")
    duration = Column(Integer, comment="执行时长（秒）")
    result = Column(JSON, comment="执行结果详情")
    error_message = Column(Text, comment="错误信息")
    log_path = Column(String(512), comment="日志文件路径")
    screenshot_path = Column(String(512), comment="截图路径")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_case = relationship("TestCase", back_populates="executions")
    test_plan = relationship("TestPlan", back_populates="executions")
    reports = relationship("TestReport", back_populates="execution", cascade="all, delete-orphan")


class TestReport(Base):
    """测试报告表"""
    __tablename__ = "test_reports"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("test_executions.id"), nullable=False)
    title = Column(String(255), nullable=False, comment="报告标题")
    summary = Column(Text, comment="AI总结")
    total_cases = Column(Integer, default=0, comment="总用例数")
    passed_cases = Column(Integer, default=0, comment="通过数")
    failed_cases = Column(Integer, default=0, comment="失败数")
    error_cases = Column(Integer, default=0, comment="错误数")
    pass_rate = Column(String(10), comment="通过率")
    coverage = Column(String(10), comment="覆盖率")
    risk_analysis = Column(JSON, comment="风险分析")
    optimization_suggestions = Column(JSON, comment="优化建议")
    html_path = Column(String(512), comment="HTML报告路径")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    execution = relationship("TestExecution", back_populates="reports")

