/**
 * QwenPaw 代码编辑器 v0.1.8 — 前端 GUI
 * 基于 Monaco Editor（VSCode 同款编辑器核心，CDN AMD 加载，无构建）：
 *   - 左侧文件树：懒加载目录、点击打开文件（仅访问当前工作区 / 平台 NAS 根）
 *   - 文件树右键菜单：打开 / 复制路径 / 下载（文件）/ 重命名 / 删除；目录可「添加到快捷访问」
 *   - 快捷访问：系统根 + 用户自定义（📌，右侧 ✕ 可移除，localStorage 持久化）
 *   - 右侧编辑区：语法高亮自动识别（20+ 语言）、Ctrl+S 保存、未保存标记
 *   - 工具栏：刷新 / 新建文件 / 保存
 * 开发范式同 file-browser / web-terminal：React.createElement + 样式对象 + GitHub Dark。
 */
(function () {
  "use strict";

  if (!window.QwenPaw || !window.QwenPaw.host) {
    console.error("[qwenpaw-code-editor] QwenPaw not ready");
    return;
  }

  var QP = window.QwenPaw;
  var React = QP.host.React;
  var h = React.createElement;

  var PLUGIN_ID = "qwenpaw-code-editor";
  var PLUGIN_NAME = "代码编辑器";
  var VERSION = "0.1.12";
  var API_BASE = "/api/qwenpaw-code-editor";

  // localStorage 键
  var LS_LAST_DIR = "qwenpaw-code-editor:lastDir";   // 最后访问目录（快捷跳转记忆）
  var LS_EXPANDED = "qwenpaw-code-editor:expanded";  // 展开的目录路径链（刷新恢复）
  var LS_FILE = "qwenpaw-code-editor:file";          // 当前打开文件（刷新恢复）
  var LS_SCROLL = "qwenpaw-code-editor:scroll";      // 编辑器滚动位置（刷新恢复）
  var LS_QUICK = "qwenpaw-code-editor:quick";        // 快捷访问折叠状态（刷新恢复）
  var LS_QUICK_CUSTOM = "qwenpaw-code-editor:quickCustom"; // 用户自定义快捷访问 [{path,label}]（刷新恢复）
  var LS_SIDEBAR = "qwenpaw-code-editor:sidebarWidth"; // 左侧栏宽度（px，刷新恢复）
  var SIDEBAR_DEFAULT = 280;

  // 左侧栏宽度钳制：最小 180，最大 640，且给右侧编辑区至少留 320px
  function clampSidebarWidth(w, viewportW) {
    var vw = viewportW || (typeof window !== "undefined" && window.innerWidth) || 1200;
    var maxW = Math.max(240, Math.min(640, vw - 320));
    var n = (w === null || w === undefined || w === "") ? NaN : Number(w);
    if (!isFinite(n)) n = SIDEBAR_DEFAULT;
    return Math.max(180, Math.min(maxW, Math.round(n)));
  }

  // ---------- 认证 ----------
  // 宿主不会替插件请求注入凭证：AuthMiddleware 只豁免 security.allow_no_auth_hosts
  // （默认 127.0.0.1 / ::1），用局域网 IP、域名或反代访问时插件必须自带 Bearer，
  // 否则所有 /api/* 返回 {"detail":"Not authenticated"}（401）。
  // 写法对齐官方插件（agent-kanban 的 apiFetch / qwenpaw-creator 的 creatorHeaders）：
  // host.getApiToken() → Authorization；PawApp iframe 下宿主挂在 window.parent。
  // 注意：2.3.0.post1 的 window.QwenPaw.host 并没有 fetch 方法（文档有、bundle 未导出），
  // 不能依赖 host.fetch，只能自行注入请求头。
  function tokenFromHost(host) {
    try {
      return (host && typeof host.getApiToken === "function" && host.getApiToken()) || "";
    } catch (e) { return ""; }
  }

  function hostToken() {
    var t = "";
    // 跨域 iframe 读 window.parent 会抛 SecurityError，单独兜住，避免连当前宿主也不查
    try {
      t = tokenFromHost(window.parent && window.parent.QwenPaw && window.parent.QwenPaw.host);
    } catch (e) { t = ""; }
    if (t) return t;
    return tokenFromHost(window.QwenPaw && window.QwenPaw.host);
  }

  // 合并鉴权头与调用方自定义头（自定义头优先）
  function authHeaders(extra) {
    var headers = {};
    var token = hostToken();
    if (token) headers["Authorization"] = "Bearer " + token;
    if (extra) {
      for (var k in extra) {
        if (Object.prototype.hasOwnProperty.call(extra, k)) headers[k] = extra[k];
      }
    }
    return headers;
  }

  // 带鉴权的原始请求（下载等非 JSON 场景）
  function fetchWithAuth(url, opts) {
    var o = opts || {};
    return fetch(url, {
      method: o.method || "GET",
      headers: authHeaders(o.headers),
      body: o.body,
    });
  }

  // 统一错误对象：401 给出可操作提示（登录失效），其余透传后端 detail
  function httpError(status, body) {
    var detail = (body && (body.detail || body.error || body.message)) || ("HTTP " + status);
    var e = new Error(status === 401 ? "登录状态已失效（401），请刷新页面重新登录" : detail);
    e.status = status;
    e.detail = detail;
    return e;
  }

  // 带进度的下载：流式读取 response.body，边收边回调 onProgress(loaded, total)。
  // Content-Length 缺失（chunked/反代压缩）时 total=0，由 UI 显示不定进度。
  function fetchBlobWithProgress(url, onProgress, signal) {
    return fetchWithAuth(url, signal ? { signal: signal } : {}).then(function (r) {
      if (!r.ok) {
        return r.json().catch(function () { return {}; }).then(function (body) {
          throw httpError(r.status, body);
        });
      }
      var total = parseInt(r.headers.get("Content-Length") || "", 10);
      if (!(total > 0)) total = 0;
      onProgress(0, total);
      var ctype = r.headers.get("Content-Type") || "application/octet-stream";
      if (!r.body || typeof r.body.getReader !== "function") return r.blob();
      var reader = r.body.getReader();
      var chunks = [];
      var loaded = 0;
      function pump() {
        return reader.read().then(function (res) {
          if (res.done) return new Blob(chunks, { type: ctype });
          chunks.push(res.value);
          loaded += res.value.length;
          onProgress(loaded, total);
          return pump();
        });
      }
      return pump();
    });
  }

  // fetch 封装
  function fetchJson(url, opts) {
    var o = opts || {};
    var headers = o.body ? { "Content-Type": "application/json" } : undefined;
    return fetchWithAuth(url, {
      method: o.method || "GET",
      headers: headers,
      body: o.body ? JSON.stringify(o.body) : undefined,
    }).then(function (r) {
      return r.json().then(function (j) {
        if (!r.ok) throw httpError(r.status, j);
        return j;
      });
    });
  }

  // ---------- 通用工具 ----------
  function basename(p) {
    if (!p) return "";
    var parts = String(p).replace(/\/+$/, "").split("/");
    return parts[parts.length - 1] || p;
  }

  function dirname(p) {
    var parts = String(p).replace(/\/+$/, "").split("/");
    parts.pop();
    return parts.join("/") || "/";
  }

  function extname(p) {
    var b = basename(p);
    var i = b.lastIndexOf(".");
    return i > 0 ? b.slice(i + 1).toLowerCase() : "";
  }

  function fmtSize(n) {
    if (typeof n !== "number" || n < 0) return "-";
    if (n < 1024) return n + " B";
    var units = ["KB", "MB", "GB"];
    var v = n;
    for (var i = 0; i < units.length; i++) {
      v /= 1024.0;
      if (v < 1024) return v.toFixed(1) + " " + units[i];
    }
    return v.toFixed(1) + " TB";
  }

  function fmtTime(ts) {
    if (!ts) return "-";
    var d = new Date(ts * 1000);
    var pad = function (x) { return (x < 10 ? "0" : "") + x; };
    return (
      d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()) +
      " " + pad(d.getHours()) + ":" + pad(d.getMinutes())
    );
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  // 扩展名 → Monaco language id
  var LANG_BY_EXT = {
    py: "python", js: "javascript", mjs: "javascript", cjs: "javascript",
    jsx: "javascript", ts: "typescript", tsx: "typescript", mts: "typescript",
    html: "html", htm: "html", css: "css", scss: "scss", less: "less",
    json: "json", jsonc: "json", md: "markdown", markdown: "markdown",
    sh: "shell", bash: "shell", zsh: "shell",
    yml: "yaml", yaml: "yaml", xml: "xml", svg: "xml",
    sql: "sql", java: "java", c: "c", h: "c", cpp: "cpp", cc: "cpp",
    hpp: "cpp", cs: "csharp", go: "go", rs: "rust", php: "php",
    rb: "ruby", swift: "swift", kt: "kotlin", scala: "scala",
    lua: "lua", toml: "ini", ini: "ini", conf: "ini",
    txt: "plaintext", log: "plaintext", diff: "diff",
    dockerfile: "dockerfile", makefile: "makefile",
    robot: "robotframework", resource: "robotframework",
  };
  function langForPath(p) {
    var b = basename(p).toLowerCase();
    if (b === "dockerfile") return "dockerfile";
    if (b === "makefile" || b === "gnumakefile") return "makefile";
    if (b === "requirements.txt") return "plaintext";
    if (b === ".gitignore" || b === ".dockerignore") return "plaintext";
    return LANG_BY_EXT[extname(p)] || "plaintext";
  }

  // 文件类型图标（emoji 简化）
  function iconFor(item) {
    if (item.type === "dir") return "📁";
    var e = extname(item.name);
    if (["py", "js", "ts", "jsx", "tsx", "html", "css", "json", "md", "sh", "yml", "yaml", "go", "rs", "java", "c", "cpp"].indexOf(e) >= 0) return "📄";
    if (["png", "jpg", "jpeg", "gif", "svg", "webp", "ico"].indexOf(e) >= 0) return "🖼️";
    if (["zip", "tar", "gz", "7z", "rar"].indexOf(e) >= 0) return "🗜️";
    return "📄";
  }

  // ---------- Monaco 加载（CDN AMD） ----------
  var monacoPromise = null;
  function loadMonaco() {
    if(!window.monaco)
      window.monaco = window.QwenPaw.host.monaco;
    if (window.monaco && window.monaco.editor) return Promise.resolve(window.monaco);
    if (monacoPromise) return monacoPromise;
    monacoPromise = window.QwenPaw.host.getMonaco();
    return monacoPromise;
  }

  // ---------- Robot Framework 语法高亮（Monarch tokenizer） ----------
  // 官方 2.1.0 Files Workspace 已支持 Robot Framework 高亮（#6519），此处为编辑器补齐。
  // 覆盖 .robot / .resource 文件：表格语法（*** 区块标题 ***、[标签]、| 分隔）、
  // 关键字/变量/注释高亮。语言 id 用 "robotframework"，避免与第三方 robot 语言包冲突。
  function registerRobotFrameworkLanguage(monaco) {
    try {
      if (monaco.languages.getLanguages().some(function (l) { return l.id === "robotframework"; })) {
        return; // 已注册
      }
      monaco.languages.register({
        id: "robotframework",
        extensions: [".robot", ".resource"],
        aliases: ["Robot Framework", "robot", "robotframework"],
        mimetypes: ["text/x-robot"],
      });
      monaco.languages.setMonarchTokensProvider("robotframework", {
        defaultToken: "",
        ignoreCase: true,
        tokenPostfix: ".robot",
        tokenizer: {
          root: [
            // 区块标题：*** Settings *** / *** Variables *** / *** Test Cases *** / *** Keywords ***
            // 注意：token 必须用字符串（数组映射在 Monarch 中会因带点号 token 名整条失败回退默认色）
            [/^\s*(\*{3,})\s*(Settings|Variables|Test Cases|Tasks|Keywords|Comments|Documentation)\s*(\*{3,})\s*$/, "keyword"],
            // 单元内方括号设置：[Documentation] [Tags] [Setup] [Teardown] [Template] [Arguments] 等
            [/^\s*\[[^\]]*\]/, "tag"],
            // 赋值：${var}= / @{list}= / &{dict}= / %{env}=
            [/^\s*(\$\{|\@\{|&\{|%\{)[^}\n]*\}/, "variable.predefined"],
            // 行内变量：${var} @{list} &{dict} %{env}
            [/(\$\{|\@\{|&\{|%\{)[^}\n]*\}/, "variable"],
            // 注释（# 开头或行尾的 # 注释）
            [/^\s*#.*$/, "comment"],
            [/#.*$/, "comment"],
            // 表格分隔符
            [/[|]/, "delimiter"],
            // 关键字调用 / 普通文本：第一列大写开头的识别为关键字
            [/^\s*([A-Za-z_][A-Za-z0-9_ .]*)(\s{2,}|$)/, "keyword"],
            [/[A-Za-z_][A-Za-z0-9_ .]*/, "identifier"],
          ],
        },
      });
    } catch (e) { /* 注册失败不影响编辑器 */ }
  }

  // ---------- Monaco 右键菜单汉化（兜底） ----------
  // 主要汉化走官方 nls 语言包（loadMonaco 中 require.config 配置 vs/nls availableLanguages=zh-cn），
  // 覆盖全部内置文本（含 Cut/Copy/Paste 等 ContextMenuController 内部创建的固定菜单项）。
  // 此处遍历 editor.getActions() 改 label 仅作兜底：nls 语言包因 CDN 异常未加载时仍能汉化大部分可枚举项。
  var CTX_MENU_ZH = {
    "editor.action.clipboardCutAction": "剪切",
    "editor.action.clipboardCopyAction": "复制",
    "editor.action.clipboardPasteAction": "粘贴",
    "editor.action.selectAll": "全选",
    "editor.action.clipboardCopyWithSyntaxHighlightingAction": "复制（带语法高亮）",
    "editor.action.quickCommand": "命令面板",
    "editor.action.formatDocument": "格式化文档",
    "editor.action.formatSelection": "格式化所选内容",
    "editor.action.toggleComment": "切换行注释",
    "editor.action.addCommentLine": "添加行注释",
    "editor.action.removeCommentLine": "删除行注释",
    "editor.action.blockComment": "切换块注释",
    "editor.action.revealDefinition": "转到定义",
    "editor.action.peekDefinition": "查看定义",
    "editor.action.revealDeclaration": "转到声明",
    "editor.action.peekDeclaration": "查看声明",
    "editor.action.rename": "重命名符号",
    "editor.action.changeAll": "更改所有匹配项",
    "editor.action.addSelectionToNextFindMatch": "将选中项添加到下一个查找匹配项",
    "editor.action.addSelectionToPreviousFindMatch": "将选中项添加到上一个查找匹配项",
    "editor.action.moveSelectionToNextFindMatch": "将上次选择移动到下一个查找匹配项",
    "editor.action.moveSelectionToPreviousFindMatch": "将上次选择移动到上一个查找匹配项",
    "editor.action.selectHighlights": "选择所有匹配项",
    "editor.action.startFindWidget": "查找",
    "editor.action.startFindReplaceAction": "替换",
    "editor.action.toggleTabFocusMode": "切换 Tab 键移动焦点",
    "editor.action.toggleWordHighlight": "切换单词高亮",
    "editor.action.unicodeHighlight": "显示/隐藏 Unicode 高亮",
    "editor.action.referenceSearch.trigger": "查找所有引用",
    "editor.action.sourceAction": "源代码操作",
    "editor.action.refactor": "重构",
    "editor.action.organizeImports": "整理导入",
    "editor.action.quickFix": "快速修复",
    "editor.action.inlineSuggest.trigger": "触发内联建议",
    "editor.action.triggerSuggest": "触发建议",
    "editor.action.triggerParameterHints": "触发参数提示",
    "editor.action.emmet.expandAbbreviation": "展开缩写",
    "editor.action.toggleColumnSelection": "切换列选择",
    "editor.action.toggleMultiCursorModifier": "切换多光标修改键",
    "editor.action.insertCursorAbove": "在上方插入光标",
    "editor.action.insertCursorBelow": "在下方插入光标",
    "editor.action.copyLinesUpAction": "向上复制行",
    "editor.action.copyLinesDownAction": "向下复制行",
    "editor.action.moveLinesUpAction": "向上移动行",
    "editor.action.moveLinesDownAction": "向下移动行",
    "editor.action.deleteLines": "删除行",
    "editor.action.indentLines": "缩进行",
    "editor.action.outdentLines": "减少缩进行",
    "editor.action.insertLineAfter": "在下方插入行",
    "editor.action.insertLineBefore": "在上方插入行",
    "editor.action.joinLines": "合并行",
    "editor.action.transpose": "交换字符",
    "editor.action.toggleWordWrap": "切换自动换行",
    "editor.action.showHover": "显示悬停信息",
    "editor.action.showContextMenu": "显示编辑器上下文菜单",
    "editor.action.showAccessibilityHelp": "显示辅助功能帮助",
    "editor.action.openLink": "打开链接",
    "editor.action.selectToBracket": "选择到括号",
    "editor.action.smartSelect.grow": "扩大选区",
    "editor.action.smartSelect.shrink": "缩小选区",
    "editor.action.formatDocument.none": "格式化文档",
    "editor.action.forceFormatDocument": "强制格式化文档",
    "editor.action.forceFormatSelection": "强制格式化所选内容",
    "editor.action.codeLens": "切换 CodeLens",
    "editor.action.toggleRenderWhitespace": "切换空白字符渲染",
    "editor.action.toggleMinimap": "切换缩略图",
    "editor.action.toggleStickyScroll": "切换粘性滚动",
  };
  function localizeMonacoMenu(editor) {
    try {
      var actions = editor.getActions();
      if (!actions) return;
      for (var i = 0; i < actions.length; i++) {
        var a = actions[i];
        if (a && a.id && CTX_MENU_ZH[a.id] && a.label !== CTX_MENU_ZH[a.id]) {
          try { a.label = CTX_MENU_ZH[a.id]; } catch (e) { /* ignore */ }
        }
      }
    } catch (e) { /* ignore */ }
  }

  // ---------- 主题样式 ----------
  var C = {
    bg: "#0d1117", panel: "#161b22", border: "#30363d",
    text: "#e6edf3", muted: "#8b949e", accent: "#58a6ff",
    green: "#3fb950", red: "#f85149", yellow: "#d29922",
    hover: "#1f2630", active: "#1f6feb", treeBg: "#0d1117",
  };

  // ---------- App 组件 ----------
  function App() {
    var self = React.useRef({}).current;
    var [status, setStatus] = React.useState(null);
    var [treeNodes, setTreeNodes] = React.useState({}); // path -> {item, children: [], loaded, expanded}
    var [rootPath, setRootPath] = React.useState("");
    var [openFile, setOpenFile] = React.useState(null);   // {path, name, content, isNew}
    var [dirty, setDirty] = React.useState(false);
    var [saving, setSaving] = React.useState(false);
    var [monacoReady, setMonacoReady] = React.useState(false);
    var [monacoErr, setMonacoErr] = React.useState("");
    var [busy, setBusy] = React.useState("");
    // 下载传输进度 {label, loaded, total, startedAt}；null = 无传输
    var [transfer, setTransfer] = React.useState(null);
    // 左侧栏宽度（可拖拽 / 键盘调整，刷新恢复）
    var [sidebarW, setSidebarW] = React.useState(function () {
      try { return clampSidebarWidth(localStorage.getItem(LS_SIDEBAR), window.innerWidth); }
      catch (e) { return SIDEBAR_DEFAULT; }
    });
    var [resizing, setResizing] = React.useState(false);
    var [isFullscreen, setIsFullscreen] = React.useState(false);
    var [notice, setNotice] = React.useState(null); // {type, text}
    var [selectedDir, setSelectedDir] = React.useState("");
    var [quickCollapsed, setQuickCollapsed] = React.useState(function () {
      try { return localStorage.getItem(LS_QUICK) === "1"; } catch (e) { return false; }
    });
    var [ctxMenu, setCtxMenu] = React.useState(null); // {x, y, item} 文件树右键菜单
    var [customQuick, setCustomQuick] = React.useState(function () {
      try {
        var arr = JSON.parse(localStorage.getItem(LS_QUICK_CUSTOM) || "[]");
        return Array.isArray(arr) ? arr : [];
      } catch (e) { return []; }
    });

    var editorRef = React.useRef(null);
    var editorElRef = React.useRef(null);
    var suppressChange = React.useRef(false);
    var nodesRef = React.useRef(treeNodes);
    nodesRef.current = treeNodes;
    var treeRootRef = React.useRef(null); // 当前文件树根（快捷访问跳转后切换）
    var pendingOpen = null; // editor 就绪前缓存的待打开文件（刷新恢复）
    var externalTargetRef = React.useRef(null); // 外部跳转（文件浏览器「编辑」）目标路径
    var downloadAbort = React.useRef(null);     // 进行中的下载 AbortController
    var openFileRef = React.useRef(null);       // 当前打开文件（供全局快捷键闭包读取）
    openFileRef.current = openFile;

    // 通知（3.5s 自动消失）
    function showNotice(type, text) {
      setNotice({ type: type, text: text });
      if (self._noticeTimer) clearTimeout(self._noticeTimer);
      self._noticeTimer = setTimeout(function () { setNotice(null); }, 3500);
    }

    // 左侧栏宽度：拖拽结束后写入 localStorage（拖拽过程中不写，避免每个像素都落盘）
    React.useEffect(function () {
      if (resizing) return;
      try { localStorage.setItem(LS_SIDEBAR, String(sidebarW)); } catch (e) { /* ignore */ }
    }, [sidebarW, resizing]);

    function startResize(e) {
      if (e.button !== undefined && e.button !== 0) return;
      e.preventDefault();
      var startX = e.clientX;
      var startW = sidebarW;
      setResizing(true);
      function onMove(ev) {
        setSidebarW(clampSidebarWidth(startW + (ev.clientX - startX), window.innerWidth));
      }
      function onUp() {
        document.removeEventListener("mousemove", onMove);
        document.removeEventListener("mouseup", onUp);
        setResizing(false);
      }
      document.addEventListener("mousemove", onMove);
      document.addEventListener("mouseup", onUp);
    }

    function resizeByKey(e) {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      e.preventDefault();
      setSidebarW(clampSidebarWidth(sidebarW + (e.key === "ArrowLeft" ? -16 : 16), window.innerWidth));
    }

    // 查找 / 替换：直接调 Monaco 原生 Find Widget（与 VS Code 同一套 UI、同一套快捷键），
    // 作用域天然只有当前 editor 的 model，也就是"只查找当前打开的文件"。
    function runFind(replace) {
      var ed = editorRef.current;
      if (!ed || !openFileRef.current) {
        showNotice("info", "请先打开一个文件再查找");
        return;
      }
      ed.focus();
      ed.trigger("toolbar", replace ? "editor.action.startFindReplaceAction" : "actions.find", null);
      // Find 输入框把 placeholder 当 tooltip，Monaco 0.56 在带偏移/滚动的容器里会把
      // 这个悬停层定位到负坐标（跑到窗口外）。清掉 tooltip，保留可见的 placeholder。
      setTimeout(silenceFindTooltips, 0);
    }

    function silenceFindTooltips() {
      try {
        var ed = editorRef.current;
        if (!ed || !ed.getContribution) return;
        var ctrl = ed.getContribution("editor.contrib.findController");
        var widget = ctrl && ctrl._widget;
        if (!widget) return;
        ["_findInput", "_replaceInput"].forEach(function (k) {
          var box = widget[k] && widget[k].inputBox;
          if (box && box.tooltip) box.tooltip = "";
        });
      } catch (e) { /* 内部字段改名时静默降级，不影响查找功能 */ }
    }

    // 浏览器全屏：优先整个 document；PawApp iframe 未授权 fullscreen 时给出提示
    React.useEffect(function () {
      function onFsChange() {
        setIsFullscreen(!!(document.fullscreenElement || document.webkitFullscreenElement));
      }
      document.addEventListener("fullscreenchange", onFsChange);
      document.addEventListener("webkitfullscreenchange", onFsChange);
      return function () {
        document.removeEventListener("fullscreenchange", onFsChange);
        document.removeEventListener("webkitfullscreenchange", onFsChange);
      };
    }, []);

    function toggleFullscreen() {
      try {
        var doc = document;
        if (doc.fullscreenElement || doc.webkitFullscreenElement) {
          var exit = doc.exitFullscreen || doc.webkitExitFullscreen;
          if (exit) {
            var p0 = exit.call(doc);
            if (p0 && p0.catch) p0.catch(function () { /* ignore */ });
          }
          return;
        }
        var el = doc.documentElement;
        var req = el.requestFullscreen || el.webkitRequestFullscreen;
        if (!req) {
          showNotice("error", "当前浏览器不支持全屏 API，可用 F11");
          return;
        }
        var p = req.call(el);
        if (p && p.catch) {
          p.catch(function (e) {
            showNotice("error", "全屏被浏览器/容器拒绝：" + ((e && e.message) || e) + "（可用 F11 或宿主窗口最大化）");
          });
        }
      } catch (e) {
        showNotice("error", "全屏失败：" + ((e && e.message) || e));
      }
    }

    // 右键菜单关闭：点击其他区域 / 滚轮 / Esc / 右键其它位置。
    // 右键菜单本身或文件树行内右键不触发关闭（行内由 onContextMenu 自己管理）。
    React.useEffect(function () {
      function closeOnClick() { setCtxMenu(null); }
      function closeOnWheel() { setCtxMenu(null); }
      function closeOnKey(e) { if (e.key === "Escape") setCtxMenu(null); }
      function closeOnOtherContext(e) {
        if (e.target && e.target.closest &&
            (e.target.closest(".ce-tree-row") || e.target.closest(".ce-ctx-menu"))) return;
        setCtxMenu(null);
      }
      document.addEventListener("click", closeOnClick);
      document.addEventListener("wheel", closeOnWheel);
      document.addEventListener("contextmenu", closeOnOtherContext);
      document.addEventListener("keydown", closeOnKey);
      return function () {
        document.removeEventListener("click", closeOnClick);
        document.removeEventListener("wheel", closeOnWheel);
        document.removeEventListener("contextmenu", closeOnOtherContext);
        document.removeEventListener("keydown", closeOnKey);
      };
    }, []);

    // 加载目录 children
    function loadDir(path, nodeKey, silent) {
      setBusy("加载目录…");
      return fetchJson(API_BASE + "/ls?path=" + encodeURIComponent(path))
        .then(function (j) {
          var next = Object.assign({}, nodesRef.current);
          next[nodeKey] = {
            item: { name: basename(path), path: path, type: "dir" },
            children: j.items,
            loaded: true,
            expanded: true,
          };
          nodesRef.current = next;
          setTreeNodes(next);
          return true;
        })
        .catch(function (e) {
          if (!silent) showNotice("error", "目录加载失败: " + e.message);
          return false;
        })
        .finally(function () { setBusy(""); });
    }

    // 保存展开的目录链（刷新恢复）
    function saveExpanded() {
      var arr = [];
      Object.keys(nodesRef.current).forEach(function (k) {
        var n = nodesRef.current[k];
        if (n && n.expanded) arr.push(k);
      });
      try { localStorage.setItem(LS_EXPANDED, JSON.stringify(arr)); } catch (e) { /* ignore */ }
    }

    // 按目录链依次加载并展开（父先子后；静默失败，用于缓存恢复）
    function loadChain(paths, done) {
      var seen = {};
      var arr = [];
      paths.forEach(function (p) {
        if (p && !seen[p]) { seen[p] = 1; arr.push(p); }
      });
      arr.sort(function (a, b) {
        return a.split("/").length - b.split("/").length;
      });
      var i = 0;
      function next() {
        if (i >= arr.length) { done && done(); return; }
        loadDir(arr[i], arr[i], true).then(function () { i++; next(); });
      }
      next();
    }

    // 快捷访问跳转：切换文件树根到指定目录
    function jumpTo(path) {
      setSelectedDir(path);
      try { localStorage.setItem(LS_LAST_DIR, path); } catch (e) { /* ignore */ }
      treeRootRef.current = path;
      setTreeNodes({});
      loadDir(path, path);
    }

    // 初始化：status + 根目录 + 恢复缓存（展开链 / 打开文件 / 滚动位置）
    React.useEffect(function () {
      // 从文件浏览器跳转打开指定文件：file-browser 会把目标路径写入
      // localStorage（键 qwenpaw-code-editor:externalFile），读完即删。
      // 说明：宿主 SPA 路由渲染时会重写 URL 丢弃 query，故不用 ?file= 参数。
      var externalFile = null;
      try {
        externalFile = localStorage.getItem("qwenpaw-code-editor:externalFile");
        if (externalFile) localStorage.removeItem("qwenpaw-code-editor:externalFile");
        if (externalFile) externalTargetRef.current = externalFile;
      } catch (e) { /* ignore */ }
      fetchJson(API_BASE + "/status")
        .then(function (j) {
          setStatus(j);
          setRootPath(j.access_root);
          // 恢复上次访问目录（快捷访问可能不在 access_root 内；加载失败才回退）
          var last = localStorage.getItem(LS_LAST_DIR);
          var start = last || j.access_root;
          setSelectedDir(start);
          treeRootRef.current = start;
          setTreeNodes({});
          var expanded = [];
          try { expanded = JSON.parse(localStorage.getItem(LS_EXPANDED) || "[]") || []; } catch (e) { expanded = []; }
          var chain = expanded.filter(function (p) { return p && p !== start && p.indexOf("/") === 0; });
          chain.push(start);
          return loadDir(start, start).then(function (ok) {
            if (!ok && start !== j.access_root) {
              // 上次目录已不可访问 → 回退默认根
              start = j.access_root;
              setSelectedDir(start);
              treeRootRef.current = start;
              setTreeNodes({});
              return loadDir(start, start).then(function () {
                return loadChain(chain.filter(function (p) { return p.indexOf(start) === 0; }), function () { });
              });
            }
            return loadChain(chain, function () {
              // 优先打开外部跳转指定文件（文件浏览器「编辑」）；否则恢复上次文件
              var target = externalTargetRef.current;
              var f = target || localStorage.getItem(LS_FILE);
              if (target) {
                // 文件树定位到目标文件所在目录并展开：
                //  - 父目录在当前树根链上 → 逐级展开整条链（树根 → 父目录）
                //  - 父目录不在当前树根下 → 树根切换到父目录（立即展开该目录）
                var parentDir = dirname(target);
                var treeRoot = treeRootRef.current;
                if (parentDir && parentDir !== treeRoot) {
                  if (parentDir.indexOf(treeRoot + "/") === 0) {
                    var subChain = [];
                    var cur = parentDir;
                    while (cur && cur !== treeRoot) { subChain.unshift(cur); cur = dirname(cur); }
                    loadChain(subChain, function () { });
                  } else {
                    treeRootRef.current = parentDir;
                    nodesRef.current = {};
                    setTreeNodes({});
                    setSelectedDir(parentDir);
                    try { localStorage.setItem(LS_LAST_DIR, parentDir); } catch (e) { /* ignore */ }
                    loadDir(parentDir, parentDir, true);
                  }
                }
              }
              if (f && editorRef.current) { openPath(f); }
              else if (f) { pendingOpen = f; }
            });
          });
        })
        .catch(function (e) { showNotice("error", "初始化失败: " + e.message); });
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // 加载 Monaco（页面挂载即开始，后台预加载）
    React.useEffect(function () {
      loadMonaco()
        .then(function (m) { window.monaco = m; setMonacoReady(true); })
        .catch(function (e) { setMonacoErr(e.message); });
    }, []);

    // 全局 Ctrl/Cmd+F 查找、Ctrl/Cmd+H 替换：焦点不在编辑器内时也能唤起
    // （焦点在编辑器内时 Monaco 自己处理，不重复触发）
    React.useEffect(function () {
      function onFindKey(e) {
        if (!(e.ctrlKey || e.metaKey) || e.altKey) return;
        var k = String(e.key || "").toLowerCase();
        if (k !== "f" && k !== "h") return;
        var host = editorElRef.current;
        if (host && host.contains(e.target)) return;
        if (!editorRef.current || !openFileRef.current) return;
        e.preventDefault();
        runFind(k === "h");
      }
      document.addEventListener("keydown", onFindKey);
      return function () { document.removeEventListener("keydown", onFindKey); };
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // 编辑器容器挂载后创建 editor
    React.useEffect(function () {
      if (!monacoReady || !editorElRef.current) return;
      if (editorRef.current) return; // 已创建
      var monaco = window.monaco;
      var editor = monaco.editor.create(editorElRef.current, {
        value: "",
        language: "plaintext",
        theme: "vs-dark",
        automaticLayout: true,
        fontSize: 13,
        lineHeight: 20,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        tabSize: 4,
        insertSpaces: true,
        wordWrap: "off",
        renderWhitespace: "selection",
        fontFamily: "'JetBrains Mono','Fira Code',Consolas,'Courier New',monospace",
        padding: { top: 8 },
        smoothScrolling: true,
        cursorBlinking: "smooth",
        scrollbar: { verticalScrollbarSize: 10, horizontalScrollbarSize: 10 },
      });
      editorRef.current = editor;
      // Find 输入框的 tooltip 在容器带偏移时会被定位到窗口外，创建后立刻清掉
      setTimeout(silenceFindTooltips, 0);
      // 右键菜单汉化：优先走官方 nls 语言包（loadMonaco 已预加载 zh-cn 语言包并修复 #5402 挂起，
      // 覆盖 Cut/Copy/Paste 等 ContextMenuController 内部固定项）；仅当语言包未生效（CDN 异常、
      // 预加载失败）时才用 localizeMonacoMenu 改 action label 兜底，避免覆盖官方翻译。
      if (!(globalThis._VSCODE_NLS_LANGUAGE === "zh-cn" && globalThis._VSCODE_NLS_MESSAGES)) {
        localizeMonacoMenu(editor);
      }
      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, function () {
        saveFile();
      });
      editor.onDidChangeModelContent(function () {
        if (suppressChange.current) return;
        setDirty(true);
      });
      // 滚动位置变化 → 节流保存（刷新恢复）
      var scrollTimer = null;
      editor.onDidScrollChange(function () {
        if (scrollTimer) clearTimeout(scrollTimer);
        scrollTimer = setTimeout(function () {
          try { localStorage.setItem(LS_SCROLL, String(editor.getScrollTop())); } catch (e) { /* ignore */ }
        }, 300);
      });
      // 打开文件（刷新恢复 / 外部跳转）+ 恢复滚动位置。
      // 优先外部跳转目标（文件浏览器「编辑」），其次 pendingOpen（初始化时 editor 未就绪缓存的
      // 待打开文件），最后才恢复 LS_FILE——避免 Monaco 就绪并发 openPath 时旧文件覆盖目标。
      var f = externalTargetRef.current || pendingOpen || localStorage.getItem(LS_FILE);
      if (f) {
        openPath(f).then(function () {
          var st = parseInt(localStorage.getItem(LS_SCROLL) || "0", 10);
          if (st > 0) { try { editor.setScrollTop(st); } catch (e) { /* ignore */ } }
        });
      }
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [monacoReady]);

    // 打开文件（读内容）
    function openPath(path) {
      setBusy("打开文件…");
      return fetchJson(API_BASE + "/read?path=" + encodeURIComponent(path))
        .then(function (j) {
          suppressChange.current = true;
          var ed = editorRef.current;
          if (ed) {
            ed.setValue(j.content || "");
            var lang = langForPath(path);
            if (lang !== "plaintext") {
              var m = window.monaco;
              var model = ed.getModel();
              if (model && m.editor) {
                try { m.editor.setModelLanguage(model, lang); } catch (e) { /* ignore */ }
              }
            }
            suppressChange.current = false;
            ed.focus();
          }
          setOpenFile({ path: j.path, name: basename(path), content: j.content || "", isNew: false });
          setDirty(false);
          try { localStorage.setItem(LS_FILE, path); } catch (e) { /* ignore */ }
        })
        .catch(function (e) {
          showNotice("error", "打开失败: " + e.message);
        })
        .finally(function () { setBusy(""); });
    }

    // 保存后把新文件插入文件树（父目录已加载则直接插入；未加载则尝试加载）
    function insertFileIntoTree(path) {
      var idx = path.lastIndexOf("/");
      if (idx <= 0) return;
      var parent = path.substring(0, idx);
      var name = path.substring(idx + 1);
      var node = nodesRef.current[parent];
      if (!node || !node.loaded) {
        // 父目录节点未加载（可能是新建的带子路径目录）：尝试加载并展开
        if (parent.indexOf("/") === 0) loadDir(parent, parent, true);
        return;
      }
      if (node.children.some(function (c) { return c.path === path; })) return;
      var next = Object.assign({}, nodesRef.current);
      var children = node.children.concat([{
        name: name, path: path, type: "file", size: 0, mtime: Math.floor(Date.now() / 1000),
      }]);
      // 与后端 _sorted_items 一致：目录在前、名称自然排序
      children.sort(function (a, b) {
        if (a.type !== b.type) return a.type === "dir" ? -1 : 1;
        var an = a.name.toLowerCase(), bn = b.name.toLowerCase();
        return an < bn ? -1 : an > bn ? 1 : 0;
      });
      next[parent] = Object.assign({}, node, { children: children });
      nodesRef.current = next;
      setTreeNodes(next);
    }

    // 保存
    function saveFile() {
      var of = openFile;
      if (!of || saving) return;
      if (!dirty && !of.isNew) {
        showNotice("info", "没有需要保存的更改");
        return;
      }
      var ed = editorRef.current;
      if (!ed) return;
      setSaving(true);
      var content = ed.getValue();
      fetchJson(API_BASE + "/write", { method: "POST", body: { path: of.path, content: content } })
        .then(function (j) {
          setDirty(false);
          setOpenFile(Object.assign({}, of, { content: content, isNew: false }));
          insertFileIntoTree(of.path);
          showNotice("ok", "已保存 " + basename(of.path));
        })
        .catch(function (e) { showNotice("error", "保存失败: " + e.message); })
        .finally(function () { setSaving(false); });
    }

    // 新建文件（在选中目录下）
    function newFile() {
      var dir = selectedDir || rootPath;
      var name = window.prompt("新建文件名（如 hello.py，可带子路径）：", "");
      if (!name || !name.trim()) return;
      var full = dir.replace(/\/+$/, "") + "/" + name.trim();
      if (editorRef.current) {
        suppressChange.current = true;
        editorRef.current.setValue("");
        try { window.monaco.editor.setModelLanguage(editorRef.current.getModel(), langForPath(full)); } catch (e) { /* ignore */ }
        suppressChange.current = false;
      }
      setOpenFile({ path: full, name: name.trim(), content: "", isNew: true });
      setDirty(true);
      try { localStorage.setItem(LS_FILE, full); } catch (e) { /* ignore */ }
      editorRef.current && editorRef.current.focus();
    }

    // 展开/折叠目录
    function toggleDir(nodeKey, item) {
      var node = nodesRef.current[nodeKey];
      if (!node) {
        loadDir(item.path, nodeKey).then(function () { saveExpanded(); });
        return;
      }
      var next = Object.assign({}, nodesRef.current);
      next[nodeKey] = Object.assign({}, node, { expanded: !node.expanded });
      nodesRef.current = next;
      setTreeNodes(next);
      setSelectedDir(item.path);
      saveExpanded();
    }

    // 点击文件
    function clickFile(item) {
      setSelectedDir(dirname(item.path));
      openPath(item.path);
    }

    // ---------- 文件右键菜单动作 ----------

    // 复制路径（clipboard API 失败时回退 execCommand）
    function copyPath(item) {
      var text = item.path;
      function fallback() {
        try {
          var ta = document.createElement("textarea");
          ta.value = text;
          ta.style.position = "fixed";
          ta.style.opacity = "0";
          document.body.appendChild(ta);
          ta.focus();
          ta.select();
          var ok = document.execCommand("copy");
          document.body.removeChild(ta);
          showNotice(ok ? "ok" : "error", ok ? "已复制路径" : "复制失败");
        } catch (e) { showNotice("error", "复制失败"); }
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () {
          showNotice("ok", "已复制路径");
        }, fallback);
      } else {
        fallback();
      }
    }

    // 下载文件（走后端 /download attachment 接口）
    // <a href> 无法携带 Authorization：非 loopback 访问会 401。改为 fetch +
    // 流式读取（带进度 / 可取消）后再触发本地下载，token 只走请求头。
    function transferText(t) {
      if (!t) return "";
      var pct = t.total > 0 ? Math.min(100, Math.floor((t.loaded / t.total) * 100)) : -1;
      var secs = Math.max(0.2, (Date.now() - t.startedAt) / 1000);
      return (pct >= 0 ? pct + "% " : "") + fmtSize(t.loaded) +
        (t.total > 0 ? " / " + fmtSize(t.total) : "") +
        " · " + fmtSize(Math.round(t.loaded / secs)) + "/s";
    }

    function cancelDownload() {
      if (downloadAbort.current) downloadAbort.current.abort();
    }

    function downloadFile(item) {
      if (downloadAbort.current) { showNotice("info", "已有下载任务进行中"); return; }
      var controller = (typeof AbortController !== "undefined") ? new AbortController() : null;
      downloadAbort.current = controller;
      var label = basename(item.path);
      var startedAt = Date.now();
      setTransfer({ label: label, loaded: 0, total: 0, startedAt: startedAt });
      fetchBlobWithProgress(
        API_BASE + "/download?path=" + encodeURIComponent(item.path),
        function (loaded, total) {
          setTransfer({ label: label, loaded: loaded, total: total, startedAt: startedAt });
        },
        controller ? controller.signal : undefined
      )
        .then(function (blob) {
          var url = URL.createObjectURL(blob);
          var a = document.createElement("a");
          a.href = url;
          a.download = label;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
          showNotice("ok", "已下载: " + label);
        })
        .catch(function (e) {
          if (e && e.name === "AbortError") showNotice("info", "已取消下载");
          else showNotice("error", "下载失败: " + ((e && e.message) || e));
        })
        .finally(function () {
          downloadAbort.current = null;
          setTransfer(null);
        });
    }

    // 重命名 / 删除后刷新父目录（保持原展开状态）
    function reloadParent(path) {
      var parent = dirname(path);
      if (!parent || !nodesRef.current[parent]) return;
      var wasExpanded = nodesRef.current[parent].expanded;
      loadDir(parent, parent, true).then(function () {
        if (!wasExpanded) {
          var next = Object.assign({}, nodesRef.current);
          if (next[parent]) next[parent] = Object.assign({}, next[parent], { expanded: false });
          nodesRef.current = next;
          setTreeNodes(next);
        }
      });
    }

    // 重命名（后端仅允许同级改名）
    function renameItem(item) {
      var oldName = basename(item.path);
      var name = window.prompt("重命名为（当前目录下）：", oldName);
      if (!name) return;
      var newName = name.trim();
      if (!newName || newName === oldName) return;
      setBusy("重命名…");
      fetchJson(API_BASE + "/rename", { method: "POST", body: { path: item.path, new_name: newName } })
        .then(function (j) {
          // 若重命名的是当前打开文件，同步更新打开状态与缓存
          if (openFile && openFile.path === item.path) {
            var np = j.path;
            setOpenFile(Object.assign({}, openFile, { path: np, name: newName }));
            try { localStorage.setItem(LS_FILE, np); } catch (e) { /* ignore */ }
          }
          reloadParent(item.path);
          showNotice("ok", "已重命名 → " + newName);
        })
        .catch(function (e) { showNotice("error", "重命名失败: " + e.message); })
        .finally(function () { setBusy(""); });
    }

    // 删除（文件或目录；前端二次确认）
    function deleteItem(item) {
      var kind = item.type === "dir" ? "目录" : "文件";
      if (!window.confirm("确定删除" + kind + " " + item.path + " ？\n删除后不可恢复！")) return;
      setBusy("删除…");
      fetchJson(API_BASE + "/delete", { method: "POST", body: { path: item.path } })
        .then(function () {
          // 若删除的是当前打开文件，清空编辑器
          if (openFile && openFile.path === item.path) {
            if (editorRef.current) {
              suppressChange.current = true;
              editorRef.current.setValue("");
              suppressChange.current = false;
            }
            setOpenFile(null);
            try { localStorage.removeItem(LS_FILE); } catch (e) { /* ignore */ }
          }
          // 若删除的是已展开的目录，清理其子树缓存，避免残留
          var next = Object.assign({}, nodesRef.current);
          Object.keys(next).forEach(function (k) {
            if (k === item.path || k.indexOf(item.path + "/") === 0) delete next[k];
          });
          nodesRef.current = next;
          setTreeNodes(next);
          reloadParent(item.path);
          showNotice("ok", "已删除 " + item.path);
        })
        .catch(function (e) { showNotice("error", "删除失败: " + e.message); })
        .finally(function () { setBusy(""); });
    }

    // ---------- 自定义快捷访问（localStorage 持久化） ----------

    function normQuickPath(p) { return String(p).replace(/\/+$/, ""); }
    function saveQuickCustom(list) {
      try { localStorage.setItem(LS_QUICK_CUSTOM, JSON.stringify(list)); } catch (e) { /* ignore */ }
    }
    function isInQuick(path) {
      var p = normQuickPath(path);
      return customQuick.some(function (c) { return normQuickPath(c.path) === p; });
    }
    function addToQuick(item) {
      if (isInQuick(item.path)) { showNotice("info", "已在快捷访问中"); return; }
      var entry = { path: normQuickPath(item.path), label: basename(item.path) };
      var next = customQuick.concat([entry]);
      setCustomQuick(next);
      saveQuickCustom(next);
      showNotice("ok", "已添加到快捷访问");
    }
    function removeFromQuick(path) {
      var p = normQuickPath(path);
      var next = customQuick.filter(function (c) { return normQuickPath(c.path) !== p; });
      setCustomQuick(next);
      saveQuickCustom(next);
      showNotice("ok", "已从快捷访问移除");
    }

    // 渲染树节点
    function renderNode(nodeKey, node, depth) {
      if (!node) return null;
      var item = node.item;
      var isDir = item.type === "dir";
      var pad = { paddingLeft: (6 + depth * 14) + "px" };
      var rowStyle = Object.assign({
        display: "flex", alignItems: "center", gap: 4,
        paddingTop: 3, paddingBottom: 3, cursor: "pointer",
        whiteSpace: "nowrap", overflow: "hidden", fontSize: 13,
        color: isDir ? C.text : (openFile && openFile.path === item.path ? C.accent : "#c9d1d9"),
        background: (openFile && openFile.path === item.path) ? C.hover : "transparent",
      }, pad);
      var arrow = isDir
        ? h("span", { style: { width: 18, textAlign: "center", color: C.muted, fontSize: 14, lineHeight: "16px" } },
            node.expanded ? "▾" : "▸")
        : h("span", { style: { width: 18 } });
      return h("div", { key: nodeKey },
        h("div", {
          className: "ce-tree-row",
          style: rowStyle,
          onClick: function () {
            if (isDir) { toggleDir(nodeKey, item); }
            else { clickFile(item); }
          },
          onContextMenu: function (e) {
            e.preventDefault();
            e.stopPropagation();
            setCtxMenu({ x: e.clientX, y: e.clientY, item: item });
          },
          title: item.path,
        },
          arrow,
          h("span", { style: { marginRight: 4 } }, iconFor(item)),
          h("span", { style: { overflow: "hidden", textOverflow: "ellipsis", color: item.broken ? C.muted : undefined } }, item.name),
          item.link
            ? h("span", {
                style: { flex: "0 0 auto", fontSize: 10.5, color: item.broken ? C.red : C.muted },
                title: item.broken ? "符号链接已失效" : "符号链接",
              }, item.broken ? "🔗失效" : "🔗")
            : null,
        ),
        isDir && node.expanded
          ? h("div", null,
              node.loaded
                ? node.children.map(function (c) {
                    var key = c.path;
                    return renderNode(key, nodesRef.current[key] || { item: c, loaded: false, expanded: false, children: [] }, depth + 1);
                  })
                : h("div", { style: Object.assign({ paddingTop: 2, paddingBottom: 2, color: C.muted, fontSize: 12 }, pad) }, "加载中…")
            )
          : null
      );
    }

    // 快捷访问区（与 file-browser 一致的 roots 列表，可折叠）
    function renderQuick() {
      if (!status || !status.roots || !status.roots.length) return null;
      var qStyle = {
        display: "flex", alignItems: "center", gap: 6,
        padding: "4px 12px", cursor: "pointer", fontSize: 12.5,
        color: "#c9d1d9", whiteSpace: "nowrap", overflow: "hidden",
      };
      var isAgent = function (label) { return label.indexOf("🤖") === 0; };
      return h("div", { style: { borderBottom: "1px solid " + C.border } },
        h("div", {
          style: { padding: "8px 12px 6px", color: C.muted, fontSize: 11.5, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: 4, userSelect: "none" },
          onClick: function () {
            setQuickCollapsed(!quickCollapsed);
            try { localStorage.setItem(LS_QUICK, quickCollapsed ? "0" : "1"); } catch (e) { /* ignore */ }
          },
          title: quickCollapsed ? "展开快捷访问" : "折叠快捷访问",
        },
          h("span", { style: { fontSize: 9, color: C.muted, transform: quickCollapsed ? "rotate(-90deg)" : "none", display: "inline-block" } }, "▼"),
          "⚡ 快捷访问",
          h("span", { style: { marginLeft: "auto", fontSize: 10, color: C.muted } }, quickCollapsed ? "展开" : "折叠"),
        ),
        quickCollapsed ? null : h("div", null,
          status.roots.map(function (r) {
            var agent = isAgent(r.label);
            var icon = agent ? "🤖"
              : r.label === "WORKING_DIR" ? "🏠"
              : r.path === "/" ? "🌐"
              : r.path === "/run/csi/mount-root/nas" ? "🗄️"
              : "📂";
            // label 已含 🤖 前缀（后端与 file-browser 一致），渲染时去掉，避免与 icon 重复
            var label = agent ? r.label.replace(/^🤖\s*/, "") : r.label;
            return h("div", {
              key: r.path,
              style: qStyle,
              onClick: function () { jumpTo(r.path); },
              title: r.path,
            },
              h("span", { style: { flex: "0 0 auto" } }, icon),
              h("span", { style: { overflow: "hidden", textOverflow: "ellipsis" } }, label),
              selectedDir === r.path ? h("span", { style: { marginLeft: "auto", color: C.accent } }, "✓") : null
            );
          }),
          // 用户自定义快捷访问（右键「添加到快捷访问」加入；右侧 ✕ 可移除）
          customQuick.length ? h("div", {
            style: { marginTop: 4, paddingTop: 4, borderTop: "1px solid " + C.border },
          },
            customQuick.map(function (c) {
              var label = c.label || basename(c.path);
              return h("div", {
                key: c.path,
                style: qStyle,
                onClick: function () { jumpTo(c.path); },
                title: c.path,
              },
                h("span", { style: { flex: "0 0 auto" } }, "📌"),
                h("span", { style: { overflow: "hidden", textOverflow: "ellipsis", flex: "1 1 auto", minWidth: 0 } }, label),
                selectedDir === c.path ? h("span", { style: { marginLeft: "auto", color: C.accent } }, "✓") : null,
                h("span", {
                  style: { flex: "0 0 auto", marginLeft: 6, cursor: "pointer", color: C.muted, fontSize: 12, padding: "0 3px", borderRadius: 4, lineHeight: "16px" },
                  onClick: function (e) { e.stopPropagation(); removeFromQuick(c.path); },
                  onMouseEnter: function (e) { e.currentTarget.style.color = C.red; },
                  onMouseLeave: function (e) { e.currentTarget.style.color = C.muted; },
                  title: "从快捷访问移除",
                }, "✕")
              );
            })
          ) : null
        ),
      );
    }

    // 树内容
    function renderTree() {
      if (!rootPath) return h("div", { style: { color: C.muted, padding: 12, fontSize: 13 } }, "加载中…");
      var treeRoot = treeRootRef.current || rootPath;
      var rootNode = nodesRef.current[treeRoot] || { item: { name: basename(treeRoot), path: treeRoot, type: "dir" }, loaded: false, expanded: false, children: [] };
      return h("div", { className: "ce-tree-scroll", style: { overflow: "auto", flex: 1, paddingBottom: 8 } },
        renderNode(treeRoot, rootNode, 0)
      );
    }

    // 文件树右键菜单（打开 / 复制路径 / 下载（文件）/ 重命名 / 删除；目录可添加到快捷访问）
    function renderCtxMenu() {
      if (!ctxMenu) return null;
      var item = ctxMenu.item;
      var isDir = item.type === "dir";
      var menuW = 190, menuH = 6 + 5 * 30; // 行高估算，用于贴边
      var x = Math.max(0, Math.min(ctxMenu.x, window.innerWidth - menuW));
      var y = Math.max(0, Math.min(ctxMenu.y, window.innerHeight - menuH));
      var menuStyle = {
        position: "fixed", left: x, top: y, zIndex: 99999,
        minWidth: 182, background: C.panel, border: "1px solid " + C.border,
        borderRadius: 8, boxShadow: "0 8px 24px rgba(0,0,0,.5)",
        padding: 4, fontSize: 13, color: C.text, userSelect: "none",
      };
      var rowBase = {
        padding: "6px 10px", borderRadius: 6, cursor: "pointer",
        display: "flex", alignItems: "center", gap: 8, whiteSpace: "nowrap",
      };
      function menuRow(label, icon, fn, danger, disabled) {
        return h("div", {
          key: label,
          style: Object.assign({}, rowBase,
            danger ? { color: C.red } : {},
            disabled ? { color: C.muted, cursor: "not-allowed", opacity: .65 } : {}),
          onMouseEnter: function (e) { if (!disabled) e.currentTarget.style.background = C.hover; },
          onMouseLeave: function (e) { e.currentTarget.style.background = "transparent"; },
          onClick: function (e) {
            e.stopPropagation();
            if (disabled) return;
            setCtxMenu(null);
            fn(item);
          },
        },
          h("span", { style: { width: 16, textAlign: "center", flex: "0 0 auto" } }, icon),
          h("span", null, label)
        );
      }
      var rows = [];
      if (isDir) {
        rows.push(menuRow("打开 / 展开", "📂", function () { toggleDir(item.path, item); }));
        rows.push(menuRow(isInQuick(item.path) ? "已在快捷访问" : "添加到快捷访问", "📌", addToQuick, false, isInQuick(item.path)));
      } else {
        rows.push(menuRow("打开", "📄", function () { clickFile(item); }));
      }
      rows.push(menuRow("复制路径", "📋", copyPath));
      if (!isDir) rows.push(menuRow("下载", "⬇️", downloadFile));
      rows.push(menuRow("重命名", "✏️", renameItem));
      rows.push(menuRow("删除", "🗑️", deleteItem, true));
      return h("div", {
        className: "ce-ctx-menu",
        style: menuStyle,
        onContextMenu: function (e) { e.preventDefault(); e.stopPropagation(); },
      }, rows);
    }

    // 顶部工具栏
    function renderToolbar() {
      var btnBase = {
        padding: "4px 12px", borderRadius: 6, fontSize: 12.5, cursor: "pointer",
        border: "1px solid " + C.border, background: C.panel, color: C.text,
      };
      return h("div", {
        style: {
          display: "flex", alignItems: "center", gap: 8,
          // 右侧预留 76px：宿主窗口/PawApp 的关闭按钮浮在右上角；窄屏换行时
          // 按钮也不会落到按钮下面（与 file-browser 顶栏同样留 76px）
          padding: "8px 76px 8px 12px",
          borderBottom: "1px solid " + C.border, background: C.panel, flexWrap: "wrap",
        }
      },
        h("span", { style: { fontWeight: 600, color: C.text, fontSize: 13.5, marginRight: 4 } }, "📝" + PLUGIN_NAME),
        h("span", { style: { color: C.muted, fontSize: 11, marginRight: 8 } }, "v" + VERSION),
        h("button", { style: btnBase, onClick: function () { setTreeNodes({}); loadDir(selectedDir || rootPath, selectedDir || rootPath); } }, "⟳ 刷新"),
        h("button", { style: btnBase, onClick: newFile }, "➕ 新建文件"),
        h("button", {
          style: Object.assign({}, btnBase, {
            background: dirty ? C.active : C.panel,
            color: dirty ? "#fff" : C.muted,
            cursor: dirty ? "pointer" : "not-allowed",
            borderColor: dirty ? C.active : C.border,
          }),
          onClick: saveFile,
          title: "Ctrl+S",
        }, saving ? "保存中…" : (dirty ? "💾 保存 ●" : "💾 保存")),
        // 右上角：全屏 / 查找 / 替换
        h("div", { style: { marginLeft: "auto", display: "flex", gap: 8, flex: "0 0 auto" } },
          h("button", {
            style: Object.assign({}, btnBase, isFullscreen ? { borderColor: C.accent, color: C.accent } : {}),
            onClick: toggleFullscreen,
            title: isFullscreen ? "退出全屏" : "浏览器全屏显示（Esc 退出）",
          }, isFullscreen ? "⛶ 退出全屏" : "⛶ 全屏"),
          h("button", {
            style: btnBase,
            onClick: function () { runFind(false); },
            title: "查找（Ctrl+F），仅当前打开的文件",
          }, "🔍 查找"),
          h("button", {
            style: btnBase,
            onClick: function () { runFind(true); },
            title: "替换（Ctrl+H），仅当前打开的文件",
          }, "⇄ 替换")
        ),
        // 工作区路径、动态提示统一放到底部状态栏；顶栏只保留操作按钮
      );
    }

    // 状态栏（底部）：保存状态 / 动态提示（复制路径、下载、重命名等）/ 当前文件 / 工作区 / 语言 / Monaco
    function renderStatusBar() {
      var lang = openFile ? langForPath(openFile.path) : "";
      var noticeColor = notice ? (notice.type === "error" ? C.red : notice.type === "ok" ? C.green : C.yellow) : C.muted;
      var noticeIcon = notice ? (notice.type === "error" ? "❌ " : notice.type === "ok" ? "✅ " : "ℹ️ ") : "";
      return h("div", {
        style: {
          display: "flex", alignItems: "center", gap: 10, overflow: "hidden",
          padding: "3px 12px", borderTop: "1px solid " + C.border,
          background: C.panel, color: C.muted, fontSize: 11.5, minHeight: 24,
        }
      },
        h("span", { style: { flex: "0 0 auto", color: dirty ? C.yellow : C.green } },
          dirty ? "● 未保存" : "已保存"),
        // 动态提示（已复制路径 / 已下载 / 重命名失败…）紧挨保存状态显示
        notice ? h("span", {
          style: {
            flex: "0 1 auto", minWidth: 0, maxWidth: "42%", color: noticeColor,
            overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
          },
          title: notice.text,
        }, noticeIcon + notice.text) : null,
        h("span", {
          style: {
            flex: "1 1 auto", minWidth: 0, overflow: "hidden",
            textOverflow: "ellipsis", whiteSpace: "nowrap",
          },
          title: openFile ? openFile.path : "",
        }, openFile ? openFile.path : ""),
        status ? h("span", {
          style: {
            flex: "0 1 auto", minWidth: 0, maxWidth: "34%", marginLeft: "auto",
            overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
          },
          title: status.working_dir,
        }, "工作区: " + status.working_dir + (status.mode === "platform" ? "（平台模式）" : "")) : null,
        lang ? h("span", { style: { flex: "0 0 auto" } }, lang) : null,
        h("span", { style: { flex: "0 0 auto" } },
          monacoErr
            ? h("span", { style: { color: C.red } }, "Monaco 加载失败")
            : (monacoReady ? "Monaco " + (window.monaco && window.monaco.editor ? "✓" : "") : "加载 Monaco…")),
      );
    }

    // 编辑器占位 / 加载中
    function renderEditorArea() {
      if (monacoErr) {
        return h("div", {
          style: { flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: C.red, fontSize: 14, flexDirection: "column", gap: 8 },
        },
          h("div", null, "❌ " + monacoErr),
          h("div", { style: { color: C.muted, fontSize: 12 } }, "编辑器需要从 定制版Qwenpaw 加载 Monaco!"),
        );
      }
      if (!monacoReady) {
        return h("div", {
          style: { flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: C.muted, fontSize: 13, flexDirection: "column", gap: 8 },
        },
          h("div", { style: { fontSize: 28 } }, "⏳"),
          h("div", null, "正在加载 Monaco Editor（首次约 3~8 秒，CDN 资源较大）…"),
        );
      }
      return h("div", { ref: editorElRef, style: { flex: 1, minHeight: 0 } });
    }

    return h("div", { style: { display: "flex", flexDirection: "column", height: "100%", background: C.bg, color: C.text, fontFamily: "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif" } },
      renderToolbar(),
      h("div", { style: { display: "flex", flex: 1, minHeight: 0 } },
        // 左侧文件树（宽度可拖拽调整，刷新恢复）
        h("div", {
          style: {
            width: sidebarW, flex: "0 0 auto", minWidth: 0,
            background: C.treeBg, display: "flex", flexDirection: "column", minHeight: 0,
          }
        },
          renderQuick(),
          h("div", {
            style: { padding: "8px 12px", borderBottom: "1px solid " + C.border, color: C.muted, fontSize: 11.5, display: "flex", justifyContent: "space-between" },
          },
            h("span", null, "文件"),
            transfer
              ? h("span", { style: { color: C.yellow, display: "flex", alignItems: "center", gap: 5, minWidth: 0 } },
                  h("span", {
                    style: { overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" },
                    title: "下载 " + transfer.label + "：" + transferText(transfer),
                  }, transferText(transfer)),
                  h("span", {
                    style: { cursor: "pointer", color: C.muted, flex: "0 0 auto" },
                    onClick: cancelDownload,
                    title: "取消下载",
                  }, "✕")
                )
              : (busy ? h("span", { style: { color: C.yellow } }, busy) : null),
          ),
          renderTree(),
        ),
        // 拖拽手柄：调整左侧栏宽度（双击恢复默认，左右方向键微调）
        h("div", {
          className: "ce-resize",
          role: "separator",
          "aria-orientation": "vertical",
          "aria-label": "调整文件树宽度",
          "aria-valuemin": 180,
          "aria-valuemax": 640,
          "aria-valuenow": sidebarW,
          tabIndex: 0,
          title: "拖拽调整宽度，双击恢复默认（" + SIDEBAR_DEFAULT + "px），←/→ 微调",
          onMouseDown: startResize,
          onDoubleClick: function () { setSidebarW(SIDEBAR_DEFAULT); },
          onKeyDown: resizeByKey,
          style: {
            flex: "0 0 auto", width: 6, marginLeft: -3, marginRight: -3,
            cursor: "col-resize", background: resizing ? C.accent : "transparent",
            zIndex: 5,
          },
        }),
        // 右侧编辑器
        h("div", { style: { flex: 1, display: "flex", flexDirection: "column", minWidth: 0, minHeight: 0 } },
          renderEditorArea(),
          renderStatusBar(),
        ),
      ),
      // 拖拽期间盖一层透明遮罩，避免 Monaco / 文件树吞掉 mousemove 或误选中
      resizing ? h("div", {
        style: { position: "fixed", top: 0, left: 0, right: 0, bottom: 0, zIndex: 99990, cursor: "col-resize" },
      }) : null,
      renderCtxMenu(),
    );
  }

  // ---------- 文件树滚动条样式 ----------
  // 平台/其它面板为暗色细滚动条（或隐藏），文件树此前是浏览器默认样式，这里统一为暗色细条，
  // 与 Monaco 编辑器滚动条风格一致（class 限定作用域，不影响平台其它区域）
  (function () {
    try {
      if (document.getElementById("ce-scrollbar-style")) return;
      var s = document.createElement("style");
      s.id = "ce-scrollbar-style";
      s.textContent =
        ".ce-tree-scroll::-webkit-scrollbar{width:10px;height:10px}" +
        ".ce-tree-scroll::-webkit-scrollbar-track{background:transparent}" +
        ".ce-tree-scroll::-webkit-scrollbar-thumb{background:rgba(110,118,129,.4);border-radius:5px;border:2px solid transparent;background-clip:content-box}" +
        ".ce-tree-scroll::-webkit-scrollbar-thumb:hover{background:rgba(110,118,129,.65);border:2px solid transparent;background-clip:content-box}" +
        ".ce-tree-scroll::-webkit-scrollbar-corner{background:transparent}" +
        ".ce-resize{border-left:1px solid #30363d}" +
        ".ce-resize:hover,.ce-resize:focus-visible{background:rgba(88,166,255,.45);outline:none}" +
        ".ce-resize:active{background:rgba(88,166,255,.7)}";
      document.head.appendChild(s);
    } catch (e) { console.error(e); }
  })();

  // ---------- 注册 ----------
  var routes = [{ path: "/apps/" + PLUGIN_ID, component: App, label: PLUGIN_NAME, icon: "📝" }];
  if (QP.registerRoutes) {
    try { QP.registerRoutes(PLUGIN_ID, routes); } catch (e) { console.error(e); }
  }
  if (QP.route && QP.route.add) {
    try { QP.route.add(PLUGIN_ID, [{ id: PLUGIN_ID, path: "/plugin/" + PLUGIN_ID, component: App }]); } catch (e) { console.error(e); }
  }
  // 侧边栏入口：与文件/终端插件一致，位于侧边栏最底部（primary.settings 顶层，无 parentId，order 90 排在文件/终端之后）
  if (QP.menu && QP.menu.add) {
    try {
      QP.menu.add(PLUGIN_ID, [{
        id: PLUGIN_ID + ".menu",
        location: "primary.settings",
        label: PLUGIN_NAME,
        icon: "📝",
        route: PLUGIN_ID,
        order: 90,
      }]);
    } catch (e) { console.error(e); }
  }
})();
