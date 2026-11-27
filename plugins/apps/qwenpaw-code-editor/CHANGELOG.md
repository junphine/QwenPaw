# 变更记录

## v0.1.12 - 2026-11-26

### 界面与布局

- **左侧文件树宽度可调**：文件树与编辑器之间新增 6px 拖拽手柄（悬停高亮），拖动实时调整，
  范围 180–640px，并保证右侧编辑器至少保留 320px；双击手柄恢复默认 280px；手柄可 Tab 聚焦、
  ←/→ 每次 ±16px（`role="separator"` + `aria-valuenow`）。
  宽度写入 `localStorage["qwenpaw-code-editor:sidebarWidth"]`，刷新恢复；拖拽过程不落盘，
  松手才写。拖拽时覆盖透明遮罩，避免 Monaco / 文件树吞掉 mousemove 或误选中文本；
  Monaco 用 `automaticLayout` 自动重排。
- **动态提示与工作区信息移到底部状态栏**：复制路径 / 下载 / 重命名 / 删除失败等提示不再占用
  顶部整条横幅（原来插在工具栏与编辑器之间，会挤掉一行内容），改为在底部状态栏「已保存」
  右侧就地显示，3.5s 自动消失；超长省略号截断，悬停 `title` 看全文，颜色沿用成功绿 / 失败红 /
  普通黄。`工作区: <WORKING_DIR>`（含平台模式标记）也从顶栏移到底栏右侧。顶栏只保留操作按钮。
- **顶栏右侧 76px 安全区**：避开宿主窗口 / PawApp 右上角的默认关闭按钮；窄屏换行时按钮也
  不会落进该范围（与 file-browser 顶栏一致）。
- **全屏按钮**：顶栏「⛶ 全屏 / ⛶ 退出全屏」，调用
  `document.documentElement.requestFullscreen()`，监听 `fullscreenchange` 同步按钮状态，
  `Esc` 退出后自动复位。PawApp iframe 未授予 `allow="fullscreen"` 时浏览器会拒绝，此时给出
  提示并建议用 F11 或宿主窗口最大化，不会静默失败。

### 查找 / 替换（仅当前文件）

- 顶栏右上角 `🔍 查找` / `⇄ 替换`，直接调用 Monaco 原生 Find Widget
  （`actions.find` / `editor.action.startFindReplaceAction`），与 VS Code 同一套界面和行为：
  大小写敏感、整词匹配、正则、匹配计数「第 n / 共 m 项」、上一个 / 下一个、单个替换、
  全部替换、Esc 关闭。
- 作用域天然是当前 `editor` 的 model，即只查找当前打开的文件，不跨文件。
- 快捷键 `Ctrl/Cmd+F` 查找、`Ctrl/Cmd+H` 替换；焦点在编辑器内时交给 Monaco 处理，
  焦点在文件树 / 按钮等区域时由插件全局兜底唤起，不重复触发。
- 未打开文件时点击按钮只提示「请先打开一个文件再查找」，不弹空面板。

### 修复

- **查找框悬停提示跑到窗口外**：Monaco 0.56 的 `InputBox` 会把 placeholder 当 tooltip
  （`this.tooltip = options.tooltip ?? placeholder`），而 Find Widget 的 workbench hover
  在带偏移 / 滚动的容器里坐标计算错误，实测悬停搜索框时 `.monaco-hover` 的
  `getBoundingClientRect().top = -17`，整个提示位于窗口上边界之外。
  修复：`silenceFindTooltips()` 在编辑器创建和每次唤起查找后，清空 find / replace 输入框的
  `inputBox.tooltip`；placeholder（「查找」「替换」）仍然可见，查找 / 替换功能完全不受影响。
  内部字段访问做了 try/catch，若未来 Monaco 改名则退化为「提示照旧出现」，不会报错。

## v0.1.11 - 2026-11-26

> 对齐 file-browser v0.2.5 的同一批修复：符号链接语义、删除保护、原子写入、传输进度。

### 安全与文件操作

- **符号链接语义（安全修复）**：`_resolve` 改为只做词法规范化（`normpath`），不再
  `resolve()` 末级链接。此前「删除一个指向外部的链接」会顺着链接删掉**目标**；
  现在列表、重命名、删除、下载都作用于链接本身，删除目录链接只 `unlink()` 链接。
- **删除 / 重命名保护**：新增 `_check_deletable`，保护 `/`、HOME、WORKING_DIR、
  插件自身目录、`plugins/` 目录、密钥目录（`QWENPAW_SECRET_DIR` / `COPAW_SECRET_DIR`）
  及 `/bin` `/etc` `/usr` `/app` `/workspace` 等顶层系统目录，并校验**祖先关系**
  （删 WORKING_DIR 的父目录、rename 掉 WORKING_DIR 都会被 400 拒绝）。
- **越界判定仍用 realpath**：`_check_access` 对 `wd/../etc`、工作区内指向外部的
  符号链接一律 403，不能靠软链接绕过（读 / 写 / 下载 / 列表同一条通道）。
- **非法路径**：含 NUL 字节等 `Path` 解析异常返回 400 而不是 500。
- **悬空链接**：仍然列出（可删除），带 `link` / `broken` 标志；读取 / 下载返回 404。

### 读写健壮性

- **保存改为原子写入**：同目录 `mkstemp` → 写入 → 保留原权限位 → `os.replace`，
  避免写到一半崩溃 / 断连把原文件截断；失败自动清理临时文件。
- **读取只读前缀**：`stat` 后 `fh.read(MAX_READ_BYTES + 1)`，不再把超限大文件整个读进内存，
  同时消除 check 与 read 之间文件变大（TOCTOU）的窗口。

### 前端

- **下载进度与取消**：流式 `response.body.getReader()`，显示百分比 / 已收字节 / 速度，
  文件树头部出现 ✕ 可取消；无 `Content-Length` 时显示不定进度。取消与读完后同时发生也能收尾。
- **符号链接标识**：文件树显示 🔗；失效链接显示「🔗失效」并置灰，悬停有说明。
- **401 提示**：统一 `httpError()`，认证失效时提示「刷新页面重新登录」，不再只显示
  `Not authenticated`。

## v0.1.10 - 2026-11-26

- **修复：非 localhost 访问时插件全部接口 401**
  - 根因：宿主 AuthMiddleware 对 `/api/*` 强制 Bearer，唯一豁免是
    `security.allow_no_auth_hosts`（默认仅 `127.0.0.1` / `::1`）；用局域网 IP、域名或
    反向代理访问时，插件裸 `fetch` 不带凭证 → `{"detail":"Not authenticated"}`。
  - 修复：新增 `hostToken()` / `authHeaders()` / `fetchWithAuth()`，通过
    `window.QwenPaw.host.getApiToken()` 取 token 注入 `Authorization: Bearer`
    （PawApp iframe 下优先读 `window.parent` 的宿主），写法与官方插件
    agent-kanban（`apiFetch`）、qwenpaw-creator（`creatorHeaders`）一致。
  - 说明：宿主 2.3.0.post1 的 `window.QwenPaw.host` 实际不提供 `fetch`
    （文档有、bundle 未导出），故不依赖 `host.fetch`。
  - 下载改用 `fetch` + `blob`：`<a href>` 无法携带 Authorization；token 只走请求头，
    不再拼进 URL / 访问日志。
  - localhost 场景无变化（`getApiToken()` 为空时不加 Authorization 头）。

## v0.1.9 - 2026-09-17

- **修复：6 个文件 I/O 处理器阻塞事件循环**
  - 受影响：`/ls`、`/read`、`/write`、`/rename`、`/delete`、`/download`
    （`iterdir`/`stat`/`read_text`/`write_text`/`rename`/`rmtree` 均为阻塞式 I/O）。
  - 修复：由 `async def` 改为同步 `def`，交给 FastAPI 线程池执行，不再占用事件循环线程。

## v0.1.8（2026-08-16）

- **工具栏标题**：图标与文字间去掉空格（📝代码编辑器），与宿主侧栏菜单入口视觉一致
- **跳转定位**：从文件浏览器「编辑」一键跳转打开文件时，左侧文件树自动定位并展开到
  目标文件所在目录——目标目录在当前树根链上则逐级展开整条链；不在链上则自动切换树根
  展开该目录，并同步最近访问目录（刷新后保持）

## v0.1.7（2026-08-15）

- **自定义快捷访问**：目录右键菜单新增「添加到快捷访问」——把任意目录固定到左侧 ⚡ 快捷访问区
  （📌 图标 + 目录名），点击一键切换文件树根；已添加的目录菜单项置灰显示「已在快捷访问」
- **快捷访问移除**：自定义条目右侧新增 ✕ 删除叉号，悬停变红，点击从快捷访问移除（不会误触
  跳转）；自定义条目与系统根以分隔线区隔，系统根不显示 ✕
- 自定义快捷访问通过 localStorage 持久化（键 `qwenpaw-code-editor:quickCustom`），刷新页面保留

## v0.1.6（2026-08-15）

- **文件树右键菜单**：侧边栏文件/目录支持右键操作——
  - 文件：打开 / 复制路径 / 下载 / 重命名 / 删除
  - 目录：打开（展开）/ 复制路径 / 重命名 / 删除
  - 下载走后端 `GET /download`（attachment）；删除前二次确认，删除的是当前打开文件时自动清空编辑器；重命名/删除后父目录自动刷新（保持原展开状态）；重命名的是当前打开文件时同步更新打开状态
- **新增后端接口**：`POST /rename`（仅同级改名）、`POST /delete`（目录递归删除）、`GET /download`（文件下载，目录拒绝）；均复用现有 `_resolve` 访问控制
- 右键菜单样式与编辑器主题一致（深色浮层，红色危险项），点击其他区域 / 滚轮 / Esc / 右键其它位置自动关闭

## v0.1.5（2026-08-14）

- **Robot Framework 语法高亮**：新增 `.robot` / `.resource` 扩展名支持（语言 id
  `robotframework`，Monarch tokenizer 自定义实现）——覆盖 `*** 区块标题 ***`（Settings/
  Variables/Test Cases/Tasks/Keywords 等）、`[Documentation]` `[Tags]` 等方括号设置、
  `${var}` `@{list}` `&{dict}` `%{env}` 变量、`#` 注释与表格 `|` 分隔符，并对关键字调用
  着色。与 QwenPaw 2.1.0 官方 Files Workspace 的 Robot Framework 支持（#6519）对齐
- **OS Shell 窗口化声明**：`launch_scope` 由 `page` 改为 `window`——2.1.0 OS 桌面中作为
  可移动/可调整大小窗口打开；2.0.1 不识别 `window` 值时自动回退 page 内嵌（功能不受影响，
  渐进增强，无需改动其他代码）
- **同步修复 plugin.py 版本号滞后**：`PLUGIN_VERSION` 原为 0.1.2（v0.1.3/v0.1.4 仅更新了
  plugin.json 与前端），现统一为 0.1.5，与 plugin.json 一致

## v0.1.4（2026-08-12）

- **修复 v0.1.3 引入的加载卡死（严重 bug）**：直接配置 `vs/nls.availableLanguages['*']='zh-cn'`
  会导致 Monaco AMD loader 永久挂起、编辑器一直停在「正在加载 Monaco Editor」——这是
  monaco-editor 官方已知 bug（microsoft/monaco-editor#5402）：语言包 `vs/nls/lang/zh-cn.js`
  只设置 `_VSCODE_NLS_MESSAGES` 全局变量、不调用 `define()`，而 `nls.messages-loader` 用 AMD
  require 加载它，模块永远无法就绪。现改为：先把语言包当普通 `<script>` 预加载（全局变量生效），
  再手动 `define("vs/nls/lang/zh-cn", ...)` 注册该模块，使 nls 插件链正常完成——右键菜单中文
  汉化保留，同时编辑器加载恢复与英文版一致的速度。语言包加载失败时自动退回英文并用手动
  label 兜底，任何情况下都不再阻塞加载

## v0.1.3（2026-08-12）

- **右键菜单汉化改为官方 nls 语言包机制**：v0.1.2 的手动改 action label 方案无法覆盖
  Cut/Copy/Paste/更改所有匹配项/命令面板 等固定菜单项（由 ContextMenuController 内部创建），
  实际仍显示英文。现通过 `require.config` 配置 `vs/nls.availableLanguages['*']='zh-cn'`，
  让 Monaco 加载官方中文语言包（min/vs/nls/lang/zh-cn.js），右键菜单、命令面板、查找替换框等
  全部内置文本一次性汉化；手动改 label 仅作 CDN 语言包异常时的兜底

## v0.1.2（2026-08-12）

- **右键菜单汉化**：Monaco 内置右键菜单（剪切 / 复制 / 粘贴 / 全选 / 复制（带语法高亮）/
  命令面板 / 格式化 / 查找 / 替换 / 行注释 / 转到定义 等 60+ 项）改为中文——创建编辑器后
  遍历 action 修改 label，右键菜单实时读取生效
- **修复竞态：外部跳转目标偶尔被旧文件覆盖**——Monaco 就绪的 useEffect 原来无条件从
  `LS_FILE` 恢复文件，与初始化流程的 externalFile 打开并发时，后完成的 fetch 会覆盖先
  完成的（表现为从文件浏览器跳转过来打开的是上次的文件）。现引入 `externalTargetRef`，
  两个打开路径统一优先外部目标，消除并发冲突

## v0.1.1（2026-08-12）

- **外部跳转打开文件（文件浏览器「✏️ 编辑」联动）**：读取 `qwenpaw-code-editor:externalFile`
  localStorage 键（文件浏览器跳转前写入，读完即删），优先打开该文件并自动定位文件树到
  其所在目录；不再使用 `?file=` query（宿主 SPA 路由重写会丢弃 query）

## v0.1.0（2026-08-09）

- 侧边栏入口移入「插件」分组（parentId: plugins-group），点击直达编辑器
- 快捷访问区标题可折叠/展开，状态记忆；agent 条目不再重复显示 🤖 图标
- 文件树目录折叠箭头加大（▸/▾ fontSize 10→14）
- 新建文件保存后立即出现在文件树（无需手动刷新）；父目录未加载时自动加载展开
- 平台模式访问范围放宽：与 file-browser 一致，遵循系统权限（access_root 仅作默认树根）
- 文件树滚动条统一为暗色细条风格（与 Monaco 编辑器 / 平台其它面板一致）

## v0.0.1（2026-08-09）

首个正式版本：

- 基于 Monaco Editor（VSCode 同款编辑器核心，CDN 加载，无构建）
- 左侧文件树懒加载浏览目录，点击打开文件；目录折叠箭头清晰易点
- 20+ 语言语法高亮自动识别（按扩展名）
- Ctrl+S 保存 / 工具栏保存，未保存 ● 标记
- 新建文件（可带子路径）、目录刷新
- 侧边栏入口：注册于侧边栏最底部（与文件/终端插件并列，📝 代码编辑器），点击直达
- 快捷访问：左侧 ⚡ 快捷访问区（与文件插件一致）——WORKING_DIR、/tmp、/home、/root、各智能体工作区、NAS 根、/app、/，点击一键切换文件树根
- 打开位置缓存：展开目录链 / 当前打开文件 / 编辑器滚动位置 全部持久化，刷新页面后自动恢复
- 后端：/status /ls /read /write 四个接口，UTF-8 无损读写
- 访问控制：工作区模式仅限 WORKING_DIR；平台模式遵循系统权限（与 file-browser 一致），access_root 仅作默认树根；二进制 / 非 UTF-8 / 超大文件（>2MB）安全拦截
- 深色 GitHub Dark 主题，与其它 QwenPaw 插件一致
