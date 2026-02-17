# AI Test Platform Backend

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置环境变量

复制 `.env.example` 到 `.env` 并配置：

```bash
cp .env.example .env
```

必须配置的环境变量：
- `OPENAI_API_KEY`: OpenAI API密钥
- `SECRET_KEY`: JWT密钥
- `DATABASE_URL`: 数据库连接URL

## 安装 Playwright

```bash
playwright install chromium
```

## 运行应用

```bash
python main.py
```

或使用 uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API 文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
backend/
├── app/
│   ├── api/              # API路由
│   │   ├── interface.py  # 接口管理
│   │   ├── testcase.py   # 测试用例
│   │   └── report.py     # 测试报告
│   ├── core/             # 核心模块
│   │   └── ai_orchestrator.py  # AI调度中心
│   ├── engine/           # 测试执行引擎
│   │   ├── pytest_runner.py    # Pytest执行器
│   │   └── playwright_runner.py # Playwright执行器
│   ├── models/           # 数据模型
│   │   ├── models.py     # ORM模型
│   │   └── schemas.py    # Pydantic模型
│   ├── config.py         # 配置
│   └── database.py       # 数据库连接
├── main.py              # 应用入口
└── requirements.txt     # 依赖列表
```

## 主要功能

### 1. 接口管理
- 创建/查询/删除接口
- AI分析接口生成测试点

### 2. 测试用例
- 根据测试点AI生成测试用例
- 执行测试用例
- 查看执行历史

### 3. 测试报告
- AI智能分析测试结果
- 生成优化建议
- 风险评估

## 开发说明

### 数据库迁移

使用 Alembic 进行数据库迁移：

```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 添加新的API端点

1. 在 `app/api/` 创建新的路由文件
2. 在 `main.py` 中注册路由
3. 更新文档

