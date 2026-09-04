# 趣学习 (Daydayup) - QwenPaw 插件

## 概述

趣学习是一个基于 Deep Tutor 架构的 AI 学习陪伴插件，为 QwenPaw 提供完整的学习系统。该插件包含八大核心功能：

1. **Home** - 主页学习空间
2. **Partners** - AI 学习伙伴
3. **My Agents** - 我的智能体
4. **Co-Writer** - 协同写作
5. **Book** - 交互式书本
6. **Learning Space** - 学习空间
7. **Memory** - 三层记忆系统
8. **Knowledge Center** - 知识中心

## 项目结构

```
daydayup/
├── backend/                 # Python FastAPI 后端
│   ├── api/                 # API 端点
│   ├── core/                # 核心插件架构
│   ├── deep_tutor_bridge/   # Deep Tutor 集成层
│   ├── services/            # 业务逻辑服务
│   └── __init__.py
├── frontend/                # React 前端 (TypeScript)
│   ├── src/
│   │   ├── views/           # 页面组件
│   │   └── styles/          # CSS 样式
│   └── dist/                # 编译/打包的前端
├── plugin.json              # 插件元数据
├── plugin.py                # 插件入口点
├── package.json             # npm 配置
├── tsconfig.json            # TypeScript 配置
└── vite.config.ts           # Vite 构建配置
```

## 功能特点

### 前端功能
- 基于 React 18 和 TypeScript 构建
- 使用 Vite 进行快速构建和热模块替换
- 外部化 React 以复用 QwenPaw 宿主提供的 React 实例
- 响应式布局，支持深色/浅色主题
- 完整的八大功能模块，每个功能都有独立的视图

### 后端功能
- 基于 FastAPI 的 RESTful API
- 插件化架构，易于扩展
- 集成 Deep Tutor 三层记忆系统
- 支持 AI 学习伙伴、智能体、知识库等高级功能

## 开发与构建

### 前端开发

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build

# 预览构建结果
npm run preview
```

### 后端开发

后端使用 Python 开发，依赖项在 plugin.json 中声明：
- fastapi>=0.109.0
- pydantic>=2.5.0
- python-multipart>=0.0.6
- aiofiles>=23.0.0
- httpx>=0.27.0
- numpy>=1.24.0

## 插件安装

1. 确保 QwenPaw 处于离线状态
2. 将插件目录复制到 QwenPaw 插件目录：
   ```
   cp -r daydayup ~/.qwenpaw/plugins/
   ```
3. 或者使用 QwenPaw CLI：
   ```
   qwenpaw plugin install ./daydayup
   ```
4. 重启 QwenPaw 启用插件

## 技术细节

### 构建配置
- 使用 Vite 作为构建工具
- React 通过 `@vitejs/plugin-react` 插件处理
- 采用经典 JSX 运行时以复用宿主 React
- 通过 rollupOptions 外部化 react 和 react-dom 以避免重复打包

### TypeScript 配置
- 目标 ES2020
- 严格类型检查
- 模块解析使用 bundler 策略
- JSX 转换为 react-jsx

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

此项目采用 MIT 许可证。