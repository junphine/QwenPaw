# 📝 代码编辑器（qwenpaw-code-editor）

基于 **Monaco Editor**（VSCode 同款编辑器核心）的 QwenPaw 在线代码编辑插件。

![qwenpaw-code-editor](https://raw.githubusercontent.com/chcsyf/qwenpaw-code-editor/main/qwenpaw-code-editor.png)

- 左侧文件树浏览目录（懒加载），点击文件在右侧打开编辑
- 按扩展名自动切换语法高亮（python / javascript / typescript / html / css / json / markdown / shell / go / rust / java / c/c++ / robot（Robot Framework）等 20+ 语言）
- **Ctrl+S** 保存（也可点工具栏保存按钮），未保存时显示 ● 标记
- 工具栏：刷新目录 / 新建文件 / 保存
- 深色主题（GitHub Dark 风格），与其它 QwenPaw 插件一致

## 安装

```bash
qwenpaw plugin install <项目路径> --force
```

安装后刷新平台页面，在 **应用 → 代码编辑器 📝** 打开。

> 首次打开需从 CDN（jsdelivr）加载 Monaco Editor（约 5MB），加载约 3~8 秒，
> 请确保浏览器可访问外网。加载失败时页面会给出明确提示。

## 界面

- 左侧文件树宽度可拖拽调整（180–640px），双击手柄恢复 280px，也可 Tab 聚焦后用 ←/→ 微调；
  宽度记忆在 localStorage，刷新保留。
- 右上角「⛶ 全屏」切换浏览器全屏（iframe 未授权时会提示改用 F11 / 窗口最大化）。
- 右上角「🔍 查找」「⇄ 替换」调用 Monaco 原生 Find Widget（与 VS Code 一致）：大小写 /
  整词 / 正则、匹配计数、逐个替换与全部替换，作用域仅当前打开的文件。快捷键 `Ctrl+F`、
  `Ctrl+H`，焦点不在编辑器内时也能唤起。
- 顶栏只放操作按钮；工作区路径与「已复制路径」等提示都在底部状态栏（「已保存」右侧），
  不会被宿主窗口右上角的默认关闭按钮遮挡。顶栏仍保留 76px 右侧安全区，窄屏换行也安全。

## 安全与文件操作

- 访问范围：工作区模式仅 `WORKING_DIR` 内；越界判定走 realpath，工作区内指向外部的
  符号链接同样被拒（读 / 写 / 下载 / 列表一致）。
- 符号链接：列表显示 🔗；重命名 / 删除只作用于链接本身，绝不跟随目标；失效链接列出并标注。
- 删除保护：`/`、HOME、`WORKING_DIR`、插件目录、`plugins/`、密钥目录及顶层系统目录
  （含其祖先）禁止删除 / 重命名。
- 保存为原子写入（临时文件 + `os.replace`），写到一半中断不会截断原文件。

## 认证与访问地址

插件接口挂载在 `/api/qwenpaw-code-editor/*`，受宿主认证中间件保护。宿主默认只对
`127.0.0.1` / `::1` 豁免认证，因此：

- 用 `localhost` 访问：无需登录也能直接用；
- 用局域网 IP、域名或反向代理访问：宿主要求 `Authorization: Bearer <token>`，
  插件已通过 `window.QwenPaw.host.getApiToken()` 自动注入，无需手动配置。

若二次修改后出现 `{"detail":"Not authenticated"}`，检查请求是否绕过了
`fetchJson` / `fetchWithAuth`。不要把网段加进 `security.allow_no_auth_hosts`，
也不要用 `?token=` 传参代替请求头。

## 使用

| 操作 | 方式 |
|---|---|
| 打开文件 | 点击左侧文件树中的文件 |
| 保存 | `Ctrl+S` 或工具栏 💾 保存 |
| 新建文件 | 工具栏 ➕ 新建文件，输入文件名（可带子路径），保存后创建 |
| 刷新目录 | 工具栏 ⟳ 刷新 |
| 切换目录 | 点击目录行展开/折叠（懒加载） |
| 文件操作 | 右键文件树条目：文件支持 打开 / 复制路径 / 下载 / 重命名 / 删除；目录支持 打开（展开）/ 添加到快捷访问 / 复制路径 / 重命名 / 删除 |
| 快捷访问 | 目录右键「添加到快捷访问」固定到 ⚡ 快捷访问区；自定义条目右侧 ✕ 可移除（刷新保留） |

## 接口

挂载于 `/api/qwenpaw-code-editor/`：

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/status` | 插件状态、版本、工作区、访问模式 |
| GET | `/ls?path=` | 列出目录（空 = 工作区根） |
| GET | `/read?path=` | 读取文本文件（二进制 / 超大文件安全拦截） |
| POST | `/write` | 保存文件 `{path, content}`（UTF-8，自动创建父目录） |
| POST | `/rename` | 重命名 `{path, new_name}`（仅同级改名，不可跨目录） |
| POST | `/delete` | 删除文件或目录 `{path}`（目录递归删除；前端需二次确认） |
| GET | `/download?path=` | 下载文件（attachment；目录拒绝） |

## 访问范围

- **工作区模式**（本地部署）：仅允许 `QWENPAW_WORKING_DIR` 内路径
- **平台模式**（NAS 平台部署，自动判定）：允许访问系统所有可读路径（遵循系统权限，与文件插件一致）；`access_root`（NAS 持久层根）仅作为默认文件树根
- 越界路径返回 403（工作区模式）；二进制 / 非 UTF-8 / 超过 2MB 的文件拒绝编辑（提示用文件浏览器下载）

## 功能

- **侧边栏入口**：注册于侧边栏最底部（与文件/终端插件并列，📝 代码编辑器），点击直达
- **快捷访问**：左侧 ⚡ 快捷访问区（WORKING_DIR、/tmp、/home、/root、各智能体工作区、NAS 根、/app、/），一键切换文件树根；目录右键「添加到快捷访问」可固定自定义目录（📌），右侧 ✕ 移除，刷新保留
- **位置记忆**：展开目录链、当前打开文件、编辑器滚动位置自动缓存，刷新页面后恢复

## 开发

```
qwenpaw-code-editor/
├── plugin.json    # 插件清单（应用中心 + 侧边栏最底部入口）
├── plugin.py      # 后端：FastAPI 路由 + 访问控制
├── ui/index.js    # 前端：Monaco Editor + 文件树 + 快捷访问 + 工具栏（无构建）
├── README.md
├── CHANGELOG.md
├── LICENSE
└── .gitignore
```

前端无构建：`ui/index.js` 运行时从 CDN 加载 Monaco AMD 版，通过
`React.createElement` + 样式对象渲染，与 file-browser / web-terminal 同一套开发范式。

## 变更记录

见 [CHANGELOG.md](https://github.com/chcsyf/qwenpaw-code-editor/blob/main/CHANGELOG.md)。

## License

Apache-2.0
