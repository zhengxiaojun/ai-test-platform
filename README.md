# 🤖 AI 自动化测试平台

## ✨ 核心特性

- 🎯 **智能测试生成**: 用户输入接口信息或页面 URL，AI 自动生成测试点和用例
- 🔄 **多 LLM 支持**: 支持 OpenAI、Google Gemini、本地部署模型等多种AI提供商
- 🚀 **自动化执行**: 基于 pytest / Playwright 自动执行测试
- 📊 **智能报告**: AI 分析测试结果，提供优化建议
- 🛡️ **失败分析**: 自动识别失败原因，智能优化测试用例

---

## 🔥 新功能：多 LLM 提供商支持

平台现在支持灵活配置不同的 LLM 提供商：

| 提供商 | 优势 | 使用场景 |
|--------|------|----------|
| **OpenAI** | 最强性能，高质量输出 | 生产环境，追求最佳效果 |
| **Google Gemini** | 性价比高，响应快速 | 日常开发，成本优化 |
| **本地模型** (Ollama/LocalAI) | 完全免费，数据隐私 | 内网环境，敏感数据 |
| **自定义API** | 灵活定制 | 企业私有部署 |

**快速切换：** 只需修改 `.env` 配置即可切换，无需改动代码！

📖 [多 LLM 配置快速开始](./docs/MULTI_LLM_QUICKSTART.md)

---

## 一、项目目标

构建一个基于 AI 的自动化测试平台，实现：

* 用户输入接口信息或页面 URL
* AI 自动生成测试点
* AI 自动生成测试用例（pytest / Playwright）
* 自动执行测试
* AI 智能分析测试报告
* 支持失败分析与智能优化

---

# 二、整体架构设计

## 1. 系统架构分层

```
前端层 (React 18 + Umi Max + Ant Design Pro)
        ↓
API 网关层 (FastAPI)
        ↓
AI Orchestration Layer（AI调度层 - 支持多 LLM 提供商）
   ├── OpenAI (GPT-4, GPT-3.5)
   ├── Google Gemini (Gemini Pro, 1.5)
   ├── 本地模型 (Ollama, LocalAI)
   └── 自定义 API (Azure OpenAI, etc.)
        ↓
测试执行引擎层（pytest / Playwright）
        ↓
存储层（PostgreSQL / SQLite / Redis）
```

---

# 三、技术栈选择

## 前端

* React 18
* Umi Max
* Ant Design Pro
* Zustand（状态管理）
* SSE（流式 AI 响应）

---

## 后端

* FastAPI
* Pydantic
* Celery / RQ（异步任务）
* pytest
* Playwright

## AI/LLM

* **OpenAI SDK** - GPT 系列模型支持
* **Google Generative AI** - Gemini 系列支持
* **OpenAI 兼容接口** - 本地/自定义模型支持
* 灵活的适配层设计，易于扩展新提供商
---

## 存储层

* PostgreSQL（结构化数据）
* Redis（缓存 / 任务队列）

---

# 四、系统模块设计

---

## 1️⃣ 前端模块

### 功能模块划分

* 接口管理
* 页面 URL 测试
* 测试点生成
* 测试用例管理
* 测试计划
* 执行记录
* 测试报告
* AI 调试对话窗口

---

## 2️⃣ 后端模块结构

```
app/
 ├── api/
 │    ├── interface.py
 │    ├── testcase.py
 │    ├── plan.py
 │    ├── report.py
 │    └── ai.py
 ├── core/
 │    ├── ai_orchestrator.py
 │    ├── prompt_manager.py
 │    ├── agent_manager.py
 │    ├── mcp_manager.py
 │    └── skill_manager.py
 ├── engine/
 │    ├── pytest_runner.py
 │    ├── playwright_runner.py
 │    └── report_generator.py
 └── models/
```

---

# 五、AI 架构设计（核心）

平台的核心是：

> AI Orchestrator（AI 调度中心）

负责调度：

* Prompt 模板
* 多 Agent 协作
* MCP 上下文管理
* Skill 技能调用

---

# 六、Prompt 体系设计

采用“分层 Prompt 设计”：

---

## 1️⃣ 接口分析 Prompt

输入：

* URL
* 请求方法
* 参数结构
* 示例响应

输出：

* 测试点列表
* 风险点
* 边界值
* 异常场景

---

## 2️⃣ 页面测试 Prompt

输入：

* 页面 URL
* DOM 结构
* 页面截图

输出：

* UI 测试点
* 交互测试点
* 异常测试点
* 兼容性风险

---

## 3️⃣ 用例生成 Prompt

输出强约束：

* JSON 格式
* pytest 代码
* 参数化结构
* mock 数据

---

# 七、智能体（Agent）设计

采用多智能体协作架构。

---

## 1️⃣ 接口分析 Agent

功能：

* 解析接口结构
* 输出测试点
* 风险等级评估

---

## 2️⃣ 用例生成 Agent

功能：

* 根据测试点生成 pytest 代码
* 生成 mock 数据
* 生成参数化结构

---

## 3️⃣ 页面测试 Agent

功能：

* 分析 DOM
* 生成 Playwright 脚本
* 自动截图

---

## 4️⃣ 报告分析 Agent

功能：

* 分析执行结果
* 生成风险报告
* 提供优化建议

---

# 八、MCP 设计（模型上下文协议）

MCP 用于：

* 管理模型上下文
* 管理工具调用能力
* 管理函数调用接口

---

## MCP 架构组成

### 1️⃣ Context Builder

聚合：

* 当前接口信息
* 历史测试用例
* 历史执行记录
* 项目规则

构建统一上下文输入模型。

---

### 2️⃣ Tool Registry（工具注册）

注册可被模型调用的函数：

* run_pytest()
* run_playwright()
* save_testcase()
* get_interface_schema()
* get_previous_report()

模型通过 function call 调用工具。

---

# 九、Skill 技能体系设计

Skill 是可复用能力模块。

---

## Skill 1：Schema 解析 Skill

* 自动解析 OpenAPI
* 生成字段校验规则

---

## Skill 2：边界值生成 Skill

* 生成边界值
* 异常值
* 安全攻击测试数据

---

## Skill 3：Mock 生成 Skill

* 生成 pytest mock
* 生成 JSON mock 数据

---

## Skill 4：失败分析 Skill

* 分析 pytest 报错日志
* 输出修复建议

---

# 十、测试执行层设计

---

## 接口测试执行

* pytest
* requests
* pytest-html
* Allure（可选）

---

## 页面测试执行

* Playwright
* Headless Chrome
* 自动截图
* 自动录屏

---

## 执行机制

* 异步任务队列（Celery / RQ）
* 支持状态查询
* 支持重试机制

---

# 十一、测试报告设计

测试报告分三层：

---

## 1️⃣ 原始报告

* pytest 原始日志
* HTML 报告

---

## 2️⃣ AI 总结报告

* 通过率
* 覆盖率
* 风险等级

---

## 3️⃣ 优化建议报告

* 未覆盖测试点
* 潜在风险
* 优化建议

---

# 十二、数据库设计

---

## PostgreSQL

* 接口信息
* 测试计划
* 执行记录
* 报告索引
* 测试用例
* 测试报告

---

## Redis

* 任务队列
* 执行状态
* 缓存

---

# 十三、实施阶段规划

---

## 第一阶段（基础可运行）

目标：

* 支持配置OPENAI风格的模型
* 输入接口信息
* AI生成测试点
* AI生成 pytest 用例
* AI执行
* AI生成报告

---

## 第二阶段（智能体升级）

* 多 Agent 协作
* Skill 模块化
* MCP 工具调用
* 上下文记忆

---

## 第三阶段（智能闭环）

* 失败自动分析
* 自动修复用例
* 自动重跑
* 风险评分系统

---

# 十四、最终目标形态

打造：

> AI 自动测试工程师系统

具备能力：

* 自动生成测试资产
* 自动执行
* 自动分析
* 自动优化
* 自动回归

---

# 十五、核心价值总结

```
AI 测试大脑（Agent + MCP + Skill）
        ↓
自动生成测试资产
        ↓
自动执行
        ↓
自动分析
        ↓
自动优化
```
