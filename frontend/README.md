# AI Test Platform Frontend

基于 React 18 + Umi Max + Ant Design Pro 的 AI 自动化测试平台前端。

## 安装依赖

```bash
npm install
```

## 开发

```bash
npm run dev
```

访问 http://localhost:8000

## 构建

```bash
npm run build
```

## 功能模块

### 1. 接口管理 (/interface)
- 创建和管理接口信息
- AI 分析接口生成测试点
- 查看接口测试点列表

### 2. 测试用例 (/testcase)
- 查看测试用例列表
- 执行测试用例
- 查看测试代码
- 查看执行历史

### 3. 测试执行 (/execution)
- 查看测试执行状态
- 查看执行历史记录

### 4. 测试报告 (/report)
- 查看测试报告列表
- AI 智能分析报告
- 风险分析
- 优化建议

## 项目结构

```
frontend/
├── src/
│   ├── pages/              # 页面组件
│   │   ├── Interface/      # 接口管理
│   │   ├── TestCase/       # 测试用例
│   │   ├── Execution/      # 测试执行
│   │   └── Report/         # 测试报告
│   ├── services/           # API 服务
│   │   └── api.ts          # API 定义
│   └── utils/              # 工具函数
│       └── request.ts      # HTTP 请求封装
├── .umirc.ts              # Umi 配置
├── package.json
└── tsconfig.json
```

## 技术栈

- React 18
- Umi Max 4.x
- Ant Design Pro Components
- Ant Design 5.x
- TypeScript
- Ahooks
- Axios

