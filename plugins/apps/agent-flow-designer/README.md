# Agent Flow Designer - 智能体工作流设计器

> Agent Flow Designer 是一款面向 QwenPaw 平台的可视化智能体工作流编排插件，支持通过拖拽方式快速构建、发布、部署和管理多节点协作的 Agent 工作流。

---

## 目录

- [一、插件概述](#一插件概述)
- [二、核心能力](#二核心能力)
- [三、支持的节点类型](#三支持的节点类型)
- [四、技术架构](#四技术架构)
- [五、安装方法](#五安装方法)
- [六、使用方法](#六使用方法)
- [七、后端 API 一览](#七后端-api-一览)
- [八、持久化存储](#八持久化存储)
- [九、项目结构](#九项目结构)
- [十、构建与打包](#十构建与打包)
- [十一、常见问题](#十一常见问题)
- [十二、未来演进](#十二未来演进)

---

## 一、插件概述

**Agent Flow Designer** 是一款面向 QwenPaw 平台的可视化智能体工作流编排插件。

### 基本信息

| 属性 | 值 |
|------|---|
| **插件 ID** | `agent-flow-designer` |
| **当前版本** | v2.4.1（以 `plugin.json` 的 `version` 为准；变更明细见 [`CHANGELOG.md`](CHANGELOG.md)） |
| **类型** | PawApp 应用插件 (`app`) |
| **兼容性** | QwenPaw / QzAgent ≥ 2.0.0 |
| **图标** | 🧩 |
| **分类** | automation |

### 核心定位

- **简化版工作流设计器**：轻量、核心功能聚焦，适合快速原型和简单编排场景
- **基石版本**：当前版本为二次开发的坚实起点，未来持续迭代，诚邀各位开发者共同参与，携手繁荣 QwenPaw 生态

---

## 二、核心能力

### 1. 可视化工作流编排

| 能力 | 说明 |
|------|------|
| **拖拽式画布** | 基于 AntV X6 图编辑引擎，支持节点拖拽、四向连线、自动吸附与对齐辅助线 |
| **多节点类型** | 开始、Agent、工具、路由决策、人工介入、结束 6 种节点 |
| **工具节点三来源** | 宿主内置工具（受治理策略约束，需审批时暂停等待人工批准）/ MCP 服务 / 外部 HTTP；HTTP 凭证只存环境变量名，运行时解析 |
| **条件分支** | 路由决策节点支持规则匹配 / LLM 智能路由 / 混合模式三种路由方式 |
| **画布交互** | 支持缩放、适应视图、缩略图预览、属性面板折叠、框选/多选、复制粘贴、一键自动布局（入口在「⋯」菜单） |
| **执行态可视化** | 只有正在执行的那条连线有蓝色流光，走过的路径保持浅蓝，未走到的仍是灰色；判定口径与引擎分发规则一致（见「执行语义」） |
| **撤销/重做** | 支持 Ctrl+Z / Ctrl+Shift+Z，历史栈上限 50 步 |
| **自动保存** | 3 秒 debounce 自动保存，脏标记 + beforeunload 保护 |
| **连接点按需显示** | 上下左右四个方向的出入口默认透明，鼠标移到节点上或拖线时才淡入，避免十几个圆点铺满画布 |

### 2. 版本化发布（配置快照）

- 每次发布生成不可变的配置快照，保留完整版本历史
- 支持按版本追溯、对比与一键回滚
- 编辑态与发布态完全隔离，线上稳定版本不受草稿修改影响

### 3. 部署与对外服务

- 一键部署工作流，自动生成对外 API 端点
- 部署后执行完全隔离：使用部署版本快照，编辑态修改不影响线上服务
- 支持一键下线，灵活控制服务生命周期

### 4. 统一对外执行接口

- 提供 `/run` 统一执行接口，支持 cURL、JavaScript、Python 等多语言调用
- 自动检测部署状态，未部署拒绝执行，保障服务稳定性

### 5. 设计期校验与运行取消

- 「校验」按钮调用 `POST /workflows/{id}/validate`，把只能在运行时暴露的问题（悬空连线、不可达节点、引用不存在/非上游的变量、开始节点非法字段、delta 缺基线、`onError=branch` 未连错误出边、环路）提前列出来，点击条目可定位到节点
- 发布与部署前强制校验，存在错误时返回 422 并在前端展示问题清单，不会产生一个跑不通的版本快照
- 「停止」调用 `POST /workflows/{id}/executions/{execution_id}/cancel`：取消标记在**节点之间**检查，正在执行的节点会跑完（不切断进行中的 LLM 请求），其后节点全部记为 `skipped`，执行结果为 `cancelled` 而不是"完成"
- 归属隔离：`user_id` 绑定到登录主体（`get_scoped_ctx`），列表/读写/执行/发布/部署/取消/恢复均按 owner 校验，越权返回 403。改造前创建、没有 owner 字段的工作流保持共享，升级不会让既有工作流库消失

---

## 三、支持的节点类型

| 节点 | 类型标识 | 说明 | 典型用途 |
|------|---------|------|---------|
| **开始** | `start` | 工作流入口节点，接收用户输入 | 作为工作流的起始点 |
| **Agent** | `agent` | 调用真实 LLM/Agent，支持配置 Agent ID 和额外提示词 | 实现智能对话、推理等核心能力 |
| **工具** | `tool` | 调用真实工具，支持宿主内置工具、MCP 服务、外部 HTTP 三种来源 | 集成外部工具/API；宿主工具受治理策略约束，需审批时流程暂停等待人工批准 |
| **路由决策** | `router` | 根据条件分支路由到不同下游节点 | 实现条件判断、流程分支 |
| **结束** | `end` | 工作流终点，汇总上游输出作为最终结果 | 作为工作流的终止点 |
| **询问** | `ask` | 向用户发起询问并收集输入 | 交互式人机对话（HITL，开发中） |

### 路由决策节点支持的运算符

- **基础比较**：`eq`、`ne`、`gt`、`lt`、`ge`、`le`
- **文本匹配**：`contains`、`starts_with`、`ends_with`、`regex`
- **Delta/Diff 运算**：`delta_gt`、`delta_lt`、`delta_ge`、`delta_le`、`change_rate_gt`、`change_rate_lt`、`text_diff_ratio_gt`、`text_diff_contains`

> ⚠ Delta/Diff 运算必须显式提供基线：**固定基准值**（手填一个数）或**引用基准节点**（选择某个上游节点的输出字段）。
> 引擎每个节点单次执行只运行一次，没有"上一次/初始值"的历史可读；未配置基线时条件不会命中，并会在执行轨迹里报出原因（早期版本会静默按 0 计算）。

### 执行语义

- **汇聚（fan-in）**：合并节点等待**所有**入边到达后才执行一次，不会因某条分支先跑完就提前触发。
- **分支隔离**：路由未命中的分支整条记为 `skipped`，其输出不会进入下游节点的提示词。
- **失败处理**：Agent / 工具节点可配置 `onError`
  - `abort`（默认）：失败即停止，下游全部记为 `skipped`，结果报告为执行失败；
  - `branch`：只沿 `sourceHandle === "error"` 的"错误"出边继续（画布上从节点的红色错误端口拉线）；未连错误出边时等同 `abort`；
  - `continue`：忽略失败继续执行下游。
- **变量引用**：`{{节点ID.字段}}`。引用不到（节点未执行 / 字段不存在）时报"未定义"，不再与"变量值为空"混为一谈。
- **画布流光的判定**：连线只在「源节点确实把令牌送了出去」且「目标节点正在执行」时才流动。端点被 `skipped`、路由未命中的分支、失败节点的普通出边（除非 `onError: continue`）都不算走过；「错误」出边只在 `onError: branch` 且源节点失败时才算。已走过的线保持浅蓝实线，执行结束（`wf_done`）后全部静止。
- **环路**：引擎先用 DFS 标出回边并把它们排除出入度屏障，再按单次执行遍历——因此图中可以存在回边（不会死锁），但回边不会被再次触发。需要真正的迭代请等 Phase B 的循环容器。

### Agent 节点的提示词来源

优先级：`promptTemplate` → `inputs` 绑定（`[{name, ref}]`）→ 命中路径上的上游输出 + 当前输入。
不再无条件把所有历史输出拼进提示词。

---

## 四、技术架构

| 层级 | 技术选型 | 版本 |
|------|----------|------|
| **前端框架** | React + TypeScript | React 18.3 |
| **构建工具** | Vite | 5.4 |
| **图编辑引擎** | AntV X6 + `@antv/x6-react-shape` | 3.1.8 |
| **后端框架** | FastAPI (Python) | — |
| **插件框架** | PawApp (qwenpaw / qzagent) | ≥2.0.0 |
| **通信协议** | REST API / HTTP | — |
| **Markdown 渲染** | `react-markdown` + `remark-gfm` + `react-syntax-highlighter` | — |
| **持久化** | JSON 文件（原子写入） | — |

---

## 五、安装方法

### 方式一：命令行安装（推荐）

```bash
# 在 qzagent 项目根目录执行
qzagent plugin install plugins/apps/agent-flow-designer
```

> 旧版平台命令为 `qwenpaw plugin install plugins/apps/agent-flow-designer`

### 方式二：控制台图形化安装

1. 打开 qzagent / qwenpaw Web 控制台
2. 进入「插件管理」页面
3. 点击「安装插件」
4. 选择 `plugins/apps/agent-flow-designer` 目录
5. 等待安装完成

---

## 六、使用方法

### 启动插件

安装完成后：

1. 打开 qzagent / qwenpaw Web 控制台
2. 在左侧边栏或「应用中心」中找到 **Agent Flow Designer**（图标：🧩）
3. 点击进入插件页面

### 基本操作流程

1. **创建工作流**：点击「+ 新建工作流」，输入名称后进入编辑器
2. **编排工作流**：
   - 从左侧节点面板拖拽节点到画布
   - 节点四向都有连接点：上、下、左、右各一个入口与出口，横向排列的流程可以直接「右侧 → 左侧」连线；连线的出入口位置随工作流一起保存。路由分支与「错误」出边仍固定在底边，那里才有位置显示分支名
   - 连接点默认不显示，鼠标移到节点上（或按住节点拖线时）才淡入，避免十几个圆点同时铺在画布上；隐藏只影响观感，透明热区仍可命中，连线不受影响。**形状区分方向：实心节点色圆点 = 出口（从这里起手拉线），白底灰环 = 入口（只接收，按下去只会拖动节点）**；画布底部提示条带同款图例
   - 单击选中节点，在右侧属性面板配置参数
3. **预览调试**：在右侧「预览与调试」面板中输入指令，按 Enter 发送
   - 执行时只有**正在跑的那条连线**有蓝色流光（白色亮头 + 浅蓝拖尾，沿数据流向移动）；已经走过的连线保持浅蓝实线，未走到的仍是灰色。路由分支、「错误」出边与 `onError` 策略都按引擎真实的分发规则判定，不会整图一起亮
4. **发布与部署**：
   - 点击「发布」按钮，将当前工作流快照为不可变版本
   - 点击「部署」按钮，使工作流可通过外部 API 调用
   - 部署后可通过 `POST /workflows/{id}/run` 外部端点调用

---

## 七、后端 API 一览

### 工作流 CRUD

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/workflows` | 创建工作流 |
| GET | `/workflows/{id}` | 获取工作流 |
| PUT | `/workflows/{id}` | 更新工作流 |
| DELETE | `/workflows/{id}` | 删除工作流 |
| GET | `/workflows` | 列出所有工作流 |

### 执行 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/workflows/{id}/execute` | 执行工作流（开发态，支持预览） |
| POST | `/workflows/{id}/run` | 外部调用（仅已部署工作流） |
| POST | `/workflows/{id}/execute/resume` | 恢复 HITL 暂停的执行 |
| POST | `/workflows/{id}/executions/{execution_id}/cancel` | 取消正在执行的运行（节点之间生效） |
| GET | `/workflows/{id}/executions` | 执行历史列表：当前账号在本工作流的执行记录，按开始时间倒序；`limit`（钳到 100）/ `offset` / `status`（仅接受已知状态，否则 422） |
| GET | `/workflows/{id}/executions/{execution_id}` | 单次执行详情：run 行 + trace + 逐节点行（`inputs` / `output` 已解码）；不属于你的执行与不存在的执行都是 404 |

### 校验 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/workflows/{id}/validate` | 静态校验图结构与变量引用；请求体可带 `workflow` 以校验未保存的画布内容 |

### 工具目录 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/tools-catalog` | 列出工具节点可选的真实调用目标：宿主内置工具（与 Agent 实际可调用集合同源）+ 各启用 MCP client 的白名单工具；单个 MCP 服务不可达时跳过该 client 而不使整个目录失败。工作区未就绪返回 503 |

### 版本管理 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/workflows/{id}/publish` | 发布版本快照（校验不通过返回 422） |
| GET | `/workflows/{id}/versions` | 列出所有版本 |
| POST | `/workflows/{id}/rollback/{version_id}` | 回滚到指定版本 |
| GET | `/workflows/{id}/published` | 获取最新发布版本 |

### 部署管理 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/workflows/{id}/deploy` | 部署工作流 |
| POST | `/workflows/{id}/undeploy` | 取消部署 |
| GET | `/workflows/{id}/deployed` | 获取已部署版本 |

---

## 八、持久化存储

### 存储路径

工作流数据统一存储在 qzagent / qwenpaw 主应用数据目录下：

| 环境 | 数据文件路径 |
|------|-------------|
| 设置了 `QZAGENT_HOME` | `<QZAGENT_HOME>/data/agent-flow-designer/workflows.json` |
| 未设置（默认） | `~/.qzagent/data/agent-flow-designer/workflows.json` |

### 存储特性

| 特性 | 实现方式 |
|------|----------|
| **写入方式** | 原子写入（`tempfile.mkstemp` + `os.replace`），确保写入完整性 |
| **并发安全** | `asyncio.Lock()` 协程级锁保护读写操作 |
| **数据迁移** | 首次访问时自动从旧版路径无损迁移 |
| **旧数据备份** | 迁移后将原文件重命名为 `.migrated` 作为备份 |

### 数据安全说明

- **插件卸载/重装**：数据保留（存储在插件目录之外）
- **插件版本更新**：数据保留，自动兼容
- **平台升级**：数据保留（除非手动清理 `~/.qzagent`）

---

## 九、项目结构

```
plugins/apps/agent-flow-designer/
├── plugin.json              # 插件声明文件（ID、入口、版本、权限等）
├── _package.py              # 构建 + 版本自增 + 分发打包脚本（见「十、构建与打包」）
├── backend/
│   ├── main.py              # PawApp 后端 API（Workflow CRUD + 执行引擎 + 版本管理）
│   └── engine/              # 图执行引擎
│       ├── runner.py        # 图遍历 + 事件驱动执行
│       ├── registry.py      # 节点处理器注册表
│       ├── state.py         # 执行状态管理
│       ├── events.py        # 事件类型定义（SSE 帧）
│       ├── log_context.py   # 执行级日志上下文（execution_id 打标）
│       ├── recorder.py      # 执行历史写入（脱敏 + 后台串行落库）
│       ├── run_db.py        # 执行历史存储层（execution_runs / execution_nodes）
│       └── paused_db.py     # HITL 暂停态存储
├── ui/
│   ├── package.json         # NPM 依赖声明
│   ├── vite.config.ts       # Vite 构建配置
│   ├── index.html           # React 应用 HTML 入口
│   ├── plugin-entry.js      # PawApp 路由注册脚本（iframe 嵌入）
│   ├── dist/                # 前端构建产物（打包进分发 zip）
│   └── src/
│       ├── App.tsx          # 主组件（首页列表 + 编辑器双视图）
│       ├── api.ts           # 后端 API 封装层
│       ├── types/flow.ts    # TypeScript 类型定义
│       ├── hooks/           # 自定义 Hooks
│       ├── contexts/        # React Context
│       └── components/      # UI 组件
│           ├── FlowCanvas.tsx      # 画布编排组件（AntV X6：节点/连线同步、执行态高亮）
│           ├── edgeConfig.ts       # 连线 markup、流光动画与连接点样式
│           ├── FlowNodeShape.tsx   # 节点卡片渲染（状态、时长、连接点）
│           ├── NodePanel.tsx       # 左侧节点面板
│           ├── PropertyPanel.tsx   # 属性/系统提示词面板
│           ├── PreviewDebug.tsx    # 预览与调试聊天界面
│           ├── ValidationPanel.tsx # 校验问题清单
│           ├── CanvasHelpModal.tsx # 画布快捷键与交互说明
│           └── MarkdownContent.tsx # 结果 Markdown 渲染
├── README.md                # 本说明文档
├── INTRODUCTION.md          # 功能介绍与 API 文档
├── PERSISTENCE_GUIDE.md     # 持久化存储与部署指南
└── Agent_Flow_对照增强方案.md # 与 nuwax / Google ADK 的差距分析与演进方案
```

---

## 十、构建与打包

分发用 zip 由插件目录下的 `_package.py` 生成。**必须在插件目录内执行**（脚本用的是相对路径）：

```bash
cd plugins/apps/agent-flow-designer
python _package.py
```

脚本按三步走：

1. **按需构建前端**：比较 `ui/dist` 与 `ui/src`、`ui/package.json`、`vite.config.ts` 等文件的修改时间；产物缺失或落后于源码时，自动在 `ui/` 下执行 `npm run build`（需要 Node.js 与 npm 在 PATH 中）。构建失败会中断打包，不会产出一个装着旧前端的包。
2. **版本号自增**：把 `plugin.json` 的 `version` 末位 +1 并回写（如 `2.0.10` → `2.0.11`），因此每跑一次就是一个新包，不会覆盖上一次的分发件。
   - **升次版本时不要走这一步**：先在 `plugin.json` 手工写定目标版本（如 `2.5.0`），再只调用收集与压缩两步，
     不让自增把版本改掉：

     ```bash
     cd plugins/apps/agent-flow-designer
     python -c "import importlib.util, json; s=importlib.util.spec_from_file_location('pkg','_package.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); v=json.load(open('plugin.json',encoding='utf-8'))['version']; m.create_package('agent-flow-designer'+v+'.zip', m.collect_files())"
     ```

     这样 `plugin.json` 与 zip 名保持一致（自增会同时回写 `plugin.json`，包内版本号和包名就对不上了）。
3. **收集并压缩**：写入 `agent-flow-designer<版本号>.zip`，内容只有运行所需文件——

| 打包内容 | 说明 |
|----------|------|
| `plugin.json` | 插件声明（含自增后的版本号） |
| `README.md` | 本说明文档，随包分发 |
| `backend/main.py` | 后端入口 |
| `backend/engine/*.py` | 执行引擎，按目录自动发现，新增模块不会漏 |
| `ui/plugin-entry.js` | PawApp 前端路由注册脚本 |
| `ui/dist/index.html` + `ui/dist/assets/*` | 前端构建产物 |

`ui/src`、`node_modules`、`_package.py` 本身与各类设计文档不进包。

拿到 zip 后的安装方式：在控制台「插件管理」里上传安装，或解压到 `plugins/apps/agent-flow-designer` 后执行 `qzagent plugin install plugins/apps/agent-flow-designer`。

---

## 十一、常见问题

### Q: 如何与现有的 orchestrator 插件共存？

A: 本插件使用独立的插件 ID (`agent-flow-designer`)，与 `orchestrator` 插件完全隔离，可以同时安装使用。

### Q: 工作流数据存储在哪里？

A: 工作流数据持久化存储在 qzagent 数据目录下的 `data/agent-flow-designer/workflows.json` 文件中（旧版插件目录下的数据会自动迁移）。采用原子写入（tempfile + os.replace）机制，确保数据安全。重启 qzagent 后数据不会丢失。

### Q: 支持哪些节点类型？

A: 当前支持 6 种节点：开始、Agent、工具（宿主内置 / MCP / 外部 HTTP 三种来源）、路由决策、人工介入（ask）、结束。

### Q: 构建时报 `Rollup failed to resolve import "tslib"` 错误？

A: `tslib` 已声明为显式依赖。如果仍遇到问题，请执行：

```bash
npm install tslib --save --legacy-peer-deps
```

### Q: 新克隆 / 新 worktree 里 `npm install` 或 `npm ci` 报 ERESOLVE？

A: 2.5.2 之前会。原因是 `@antv/x6-plugin-minimap@2.0.7` 的 peer 还写着 `@antv/x6@^2.x`，而 x6 锁在 3.1.8；
这个包**只在 `package.json` 里声明、`ui/src` 从未 import**（画布用的是 `@antv/x6` 自带的 `MiniMap`，v3 已并入核心，
见 `FlowCanvas.tsx` 的 import），所以它已从依赖里删除。现在直接装即可，不需要任何 peer 绕过参数：

```bash
cd plugins/apps/agent-flow-designer/ui
npm ci
```

若你在旧版本 worktree 上仍撞上 ERESOLVE，临时用 `npm ci --legacy-peer-deps`（它不会改动 `package-lock.json`；
`npm install` 可能会，别用它）。

### Q: 跑了 `python _package.py`，但 zip 里的前端还是旧的？

A: 脚本只在 `ui/dist` 落后于 `ui/src`（或产物缺失）时才重新构建。如果手工改过 `dist`、或构建被中断，先删掉 `ui/dist` 再跑一次即可强制重建。

### Q: 打包时报 `[Build FAILED] npm command not found`？

A: 说明 PATH 里找不到 Node.js。Windows 上脚本已按 `npm.cmd` 调用（`CreateProcess` 不会把裸 `npm` 解析成 `.cmd`），所以这一步仍失败就是 Node.js 未安装或未加入 PATH。

---

## 十二、未来演进

当前版本仅为基石，未来仍有广阔的提升空间。我们希望通过这个项目，为大家提供一个坚实的二次开发起点，诚邀各位开发者共同参与，携手繁荣 QwenPaw 生态。

完整的差距分析与排期见 [`Agent_Flow_对照增强方案.md`](Agent_Flow_对照增强方案.md)（对照 nuwax 与 Google ADK）。P0 部分——遍历语义、失败传播、汇聚屏障、变量寻址、设计期校验、归属隔离与运行取消——已在本版本落地。

**下一步（Phase B：执行语义）**：

- **并行 fan-out**：同一层多个就绪节点并发执行，并受工作流级 `max_concurrency` 限流
- **循环容器**：分组容器 + `max_iterations` + 回边重触发（当前回边只会被标记，不会被再次执行）
- **执行历史**：落库（v2.2.10）与逐 run/逐节点 token 用量（v2.3.0）已就绪，v2.5.0 补上读取接口与画布里的历史抽屉（列表 + 逐节点详情），v2.5.2 让保留策略真正跑起来（每次 run 收尾后按节流排队清理）。仍未做：从历史重放与一键重跑、跨工作流执行总览、成本换算。注意保留是 **TTL 与"每工作流最新 N 条"的交集**，单条工作流不满 `keep_per_workflow` 时 TTL 那一半不触发
- **~~节点级超时与重试~~**（已实现）：agent/tool/router 逐节点可配置超时与指数退避重试（2.6.x，见 CHANGELOG）；start/end/ask 不适用
- **引擎回调钩子**：before/after node，供外部插短路逻辑与埋点

**再往后（Phase C：变量与节点生态）**：

- 前端 `NodeTypeDef` 注册表 + 属性面板按 schema 渲染，新增节点类型不再需要改多处
- 统一变量引用模型（拓扑可达校验、变量芯片插值、类型/默认值/必填）
- LLM 节点、Code 节点（子进程/容器沙箱 + 超时，不使用 `eval()`）、变量/条件节点
- 工具节点已接真实实现（v2.2.0：platform / mcp / http 三来源）。HTTP 凭证只保存**环境变量名**、运行时解析，值不进 `workflows.json`、执行轨迹与导出；可引用的变量名硬约束在 `AFD_HTTP_SECRET_` 命名空间内（"只存变量名"本身挡不住填任意变量名）。接宿主 secret 存储仍是后续项
- 结构化输出（`output_schema` → 解析 + 校验 + 失败重试）
- SQLite 存储迁移、插件节点

---

## 许可证

MIT License
