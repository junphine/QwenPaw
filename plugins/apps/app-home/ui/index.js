/**
 * QwenPaw 应用首页（app-home）v0.2.0 — 前端 UI
 *
 * 功能：
 *  1. 展示本机已安装应用卡片（从 /api/plugins/app-home/apps 拉取）
 *  2. 每个卡片提供"设为启动默认"按钮
 *  3. 顶部正中间 ON/OFF 开关：控制"启动时自动打开默认应用"
 *  4. 【核心】插件 JS 一加载（即 Console 启动时）就检查配置：
 *     enabled=true 且已选应用 → 直接跳转到该应用，无需进入本页面
 *
 * 防循环/防打扰：
 *  - 默认应用是本插件自身 → 不跳
 *  - 当前已在目标路径 → 不跳
 *  - 同一次后端启动只自动跳一次（localStorage 记录后端启动时间戳比对）
 *  - fetch 失败自动重试 2 次；跳转失败静默，不影响 Console 正常使用
 *  - 每一步上报后端 /log（写进 qwenpaw.log，可诊断）
 */
(function () {
  'use strict';

  if (!window.QwenPaw || !window.QwenPaw.host) {
    console.error("[app-home] QwenPaw not ready");
    return;
  }

  var QP = window.QwenPaw;
  var React = QP.host.React;
  var h = React.createElement;

  var PLUGIN_ID = "app-home";
  var PLUGIN_NAME = "应用首页";
  var HOME_PATH = "/apps/" + PLUGIN_ID; // 应用首页自身路由（默认落地点）
  var API = "/api/plugins/" + PLUGIN_ID;
  var LAST_OPEN_KEY = "app-home:last-open-server-ts";

  // 前端遥测：上报到后端日志（qwenpaw.log 可查），静默失败
  function logStep(step, detail) {
    try {
      fetch(API + "/log", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ step: step, detail: String(detail || "") }),
      }).catch(function () {});
    } catch (e) {}
  }

  // ════════════════════════════════════════════════════════════
  // 启动即执行：QwenPaw 进入就打开"应用首页"；
  // 若用户已选默认启动应用且开关 ON → 直达该应用。
  //
  // 触发范围：仅当当前不在任何应用/插件页内（/apps/*、/plugin/* 除外），
  //   避免用户在使用某应用时刷新页面被拽走。
  // 防重判据：后端启动时间戳 server_started_at。
  //   localStorage 记录"上次为其自动打开过的后端启动时间"，
  //   每次 QwenPaw（后端）重启 → 时间戳变新 → 执行一次自动打开。
  //   WebView 常驻/页面刷新不会重复触发。
  // ════════════════════════════════════════════════════════════
  (function autoOpenDefaultApp() {
    var cur = window.location.pathname || "/";
    logStep("boot", "url=" + window.location.href);

    // 已在应用/插件页内 → 不打扰（含跳转后的二次加载，天然防循环）
    if (/^\/(apps|plugin)\//.test(cur)) {
      logStep("guard", "inside_app_page:" + cur);
      return;
    }

    function attempt(retriesLeft) {
      fetch(API + "/default")
          .then(function (r) { return r.ok ? r.json() : null; })
          .then(function (d) {
            if (!d) {
              logStep("fetch_null", "");
              return;
            }
            logStep("fetched", JSON.stringify({
              id: d.id, enabled: d.enabled, path: d.path,
              srv: d.server_started_at,
            }));

            // 开关关闭 → 完全不做跳转（尊重用户）
            if (!d.enabled) {
              logStep("skip", "disabled");
              return;
            }

            // 决定落地目标：已指定其它应用 → 直达该应用；否则 → 应用首页
            var target, reason;
            if (d.id && d.id !== PLUGIN_ID) {
              target = d.path || ("/apps/" + d.id);
              reason = "default_app";
            } else {
              target = HOME_PATH;
              reason = "home";
            }

            // 防重：这次后端启动已经自动打开过 → 不跳
            var lastTs = "";
            try { lastTs = localStorage.getItem(LAST_OPEN_KEY) || ""; } catch (e) {}
            if (lastTs && String(d.server_started_at) === lastTs) {
              logStep("guard", "already_opened_this_boot ts=" + lastTs);
              return;
            }
            try { localStorage.setItem(LAST_OPEN_KEY, String(d.server_started_at)); } catch (e) {}

            logStep("redirecting", target + " reason=" + reason);
            // 延迟等 Console 初步就绪再整页跳转（history 路由，服务端 catch-all）
            setTimeout(function () {
              try {
                window.location.replace(target);
              } catch (e) {
                try { window.location.href = target; } catch (e2) {
                  logStep("redirect_failed", String(e2));
                }
              }
            }, 250);
          })
          .catch(function (e) {
            logStep("fetch_error", String(e) + " retriesLeft=" + retriesLeft);
            if (retriesLeft > 0) {
              setTimeout(function () { attempt(retriesLeft - 1); }, 1500);
            }
          });
    }
    attempt(2); // 失败最多重试 2 次（覆盖启动初期后端时序问题）
  })();

  // ---------- 样式（GitHub Dark） ----------
  var C = {
    bg: "transparent",
    panel: "transparent",
    border: "#f5f5f5",
    text: "#041625",
    muted: "#8b949e",
    green: "#3fb950",
    blue: "#58a6ff",
    orange: "#d29922",
    purple: "#bc8cff",
    red: "#f85149",
    on: "#3fb950",
    off: "#8b949e",
  };

  var S = {
    wrap: {
      display: "flex", flexDirection: "column",
      height: "100%", minHeight: 0,
      background: C.bg, color: C.text,
      fontFamily: "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif",
      fontSize: 13,
    },
    // 顶部栏：三段布局，中间段用绝对定位精确居中
    topBar: {
      position: "relative",
      display: "flex", alignItems: "center",
      padding: "10px 16px",
      background: C.panel,
      borderBottom: "1px solid " + C.border,
      flexShrink: 0,
      minHeight: 44,
    },
    topLeft: { display: "flex", alignItems: "center", gap: 10, flexShrink: 0 },
    // 正中间：absolute + left 50% + translateX(-50%)，与左右内容宽度无关
    topCenter: {
      position: "absolute", left: "50%", top: "50%",
      transform: "translate(-50%, -50%)",
      display: "flex", alignItems: "center", gap: 10,
      whiteSpace: "nowrap",
    },
    topRight: {
      marginLeft: "auto", display: "flex", alignItems: "center", gap: 8, flexShrink: 0,
    },
    title: { fontSize: 16, fontWeight: 700, color: C.text },
    sub: { color: C.muted, fontSize: 12 },
    toggle: {
      display: "inline-flex", alignItems: "center", gap: 8,
      cursor: "pointer", userSelect: "none",
    },
    toggleTrack: {
      width: 44, height: 22, borderRadius: 11,
      background: C.off, position: "relative",
      transition: "background .2s",
      boxSizing: "border-box",
    },
    toggleOn: { background: C.on },
    toggleKnob: {
      position: "absolute", top: 2, left: 2,
      width: 18, height: 18, borderRadius: "50%",
      background: "#fff", transition: "left .2s",
    },
    toggleKnobOn: { left: 24 },
    toggleLabel: { fontSize: 12, fontWeight: 700 },
    body: { flex: 1, minHeight: 0, overflow: "auto", padding: 16, boxSizing: "border-box" },
    errBar: {
      margin: "0 0 12px", padding: "8px 12px",
      background: "rgba(248,81,73,0.12)", color: C.red,
      border: "1px solid rgba(248,81,73,0.4)", borderRadius: 6, fontSize: 12,
    },
    grid: {
      display: "grid",
      gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
      gap: 12,
    },
    card: {
      background: C.panel,
      border: "1px solid " + C.border,
      borderRadius: 10,
      padding: "14px 14px 10px",
      display: "flex", flexDirection: "column", gap: 8,
      transition: "border-color .15s, transform .15s",
    },
    cardDefault: {
      borderColor: C.blue,
      boxShadow: "0 0 0 1px " + C.blue,
    },
    cardHead: { display: "flex", alignItems: "center", gap: 8 },
    cardIcon: { fontSize: 22, lineHeight: 1 },
    cardName: { fontWeight: 600, fontSize: 13, color: C.text, flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" },
    cardVer: { fontSize: 11, color: C.muted },
    cardDesc: { fontSize: 12, color: C.muted, lineHeight: 1.4, minHeight: 34, maxHeight: 48, overflow: "hidden" },
    cardActions: { display: "flex", gap: 8, marginTop: "auto", paddingTop: 6 },
    btn: {
      flex: 1,
      background: "transparent", color: C.blue,
      border: "1px solid " + C.blue, borderRadius: 6,
      padding: "4px 8px", cursor: "pointer", fontSize: 12,
      textAlign: "center", textDecoration: "none",
    },
    btnPrimary: {
      flex: 1,
      background: C.blue, color: "#fff",
      border: "1px solid " + C.blue, borderRadius: 6,
      padding: "4px 8px", cursor: "pointer", fontSize: 12,
      textAlign: "center",
    },
    btnDisabled: {
      flex: 1,
      background: "transparent", color: C.muted,
      border: "1px solid " + C.border, borderRadius: 6,
      padding: "4px 8px", cursor: "not-allowed", fontSize: 12,
      textAlign: "center",
    },
    badge: {
      display: "inline-block", fontSize: 10, padding: "1px 6px",
      borderRadius: 4, background: C.blue, color: "#fff",
      marginLeft: 4, verticalAlign: "middle",
    },
    empty: {
      display: "flex", alignItems: "center", justifyContent: "center",
      height: "100%", color: C.muted, fontSize: 13,
    },
  };

  // ---------- 工具 ----------
  function fetchJson(url, opts) {
    var o = opts || {};
    return fetch(url, o).then(function (r) {
      if (!r.ok) return r.text().then(function (t) { throw new Error(t || r.status); });
      return r.json();
    });
  }

  // ---------- 主组件 ----------
  function App() {
    var appsPair = React.useState(null);
    var apps = appsPair[0];
    var setApps = appsPair[1];

    var defaultIdPair = React.useState("");
    var defaultId = defaultIdPair[0];
    var setDefaultId = defaultIdPair[1];

    var enabledPair = React.useState(false);
    var enabled = enabledPair[0];
    var setEnabled = enabledPair[1];

    var errPair = React.useState(null);
    var err = errPair[0];
    var setErr = errPair[1];

    var savingPair = React.useState(false);
    var saving = savingPair[0];
    var setSaving = savingPair[1];

    // 首次加载：拉应用列表 + 当前默认配置（不在此处做启动跳转，
    // 跳转逻辑已在插件加载时于顶层 autoOpenDefaultApp() 执行）
    React.useEffect(function () {
      var alive = true;
      fetchJson(API + "/apps").then(function (d) {
        if (!alive) return;
        if (d.error) { setErr(d.error); return; }
        setErr(null);
        setApps(d.apps || []);
        setDefaultId(d.default_app_id || "");
        setEnabled(!!d.default_enabled);
      }).catch(function (e) {
        if (alive) setErr(String((e && e.message) || e));
      });
      return function () { alive = false; };
    }, []);

    function handleSetDefault(appId) {
      setSaving(true);
      fetchJson(API + "/default", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: appId, enabled: true }),
      }).then(function (r) {
        setSaving(false);
        if (r.ok) {
          setDefaultId(r.id || "");
          setEnabled(!!r.enabled);
          // 清除"本次启动已自动打开"标记，让下次刷新即可验证新默认
          try { localStorage.removeItem(LAST_OPEN_KEY); } catch (e) {}
        } else {
          setErr(r.detail || "保存失败");
        }
      }).catch(function (e) {
        setSaving(false);
        setErr(String((e && e.message) || e));
      });
    }

    function handleToggle() {
      var next = !enabled;
      setEnabled(next);
      setSaving(true);
      fetchJson(API + "/default", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: defaultId, enabled: next }),
      }).then(function (r) {
        setSaving(false);
        if (r.ok) {
          setDefaultId(r.id || "");
          setEnabled(!!r.enabled);
          try { localStorage.removeItem(LAST_OPEN_KEY); } catch (e) {}
        } else {
          setErr(r.detail || "保存失败");
          setEnabled(!next); // 回滚
        }
      }).catch(function (e) {
        setSaving(false);
        setErr(String((e && e.message) || e));
        setEnabled(!next); // 回滚
      });
    }

    if (!apps) {
      return h("div", { style: S.wrap },
          h("div", { style: S.empty }, "加载中…" + (err ? "（" + err + "）" : "")));
    }

    // 空 = 未指定其它应用 → 落地页就是应用首页自身
    var effectiveDefaultId = defaultId || PLUGIN_ID;
    var defaultApp = apps.filter(function (a) { return a.id === effectiveDefaultId; })[0];

    return h("div", { style: S.wrap },
        // 顶部栏：左标题 / 正中开关 / 右侧状态
        h("div", { style: S.topBar },
            // 左：标题
            h("div", { style: S.topLeft },
                h("span", { style: S.title }, "🏠 " + PLUGIN_NAME),
                h("span", { style: S.sub }, "共 " + apps.length + " 个应用")
            ),
            // 正中：启动默认应用 ON/OFF
            h("div", { style: S.topCenter },
                h("span", { style: S.sub },
                    "启动时打开：" + (!enabled
                        ? "已关闭"
                        : (defaultApp && defaultApp.id !== PLUGIN_ID
                            ? (defaultApp.name || defaultApp.id)
                            : "应用首页"))),
                h("div", { style: S.toggle, onClick: handleToggle, title: enabled ? "点击关闭" : "点击开启" },
                    h("div", {
                          style: Object.assign({}, S.toggleTrack, enabled ? S.toggleOn : {}),
                        },
                        h("div", {
                          style: Object.assign({}, S.toggleKnob, enabled ? S.toggleKnobOn : {}),
                        })),
                    h("span", {
                      style: Object.assign({}, S.toggleLabel, { color: enabled ? C.on : C.off }),
                    }, enabled ? "ON" : "OFF")
                )
            ),
            // 右：保存状态
            h("div", { style: S.topRight },
                saving ? h("span", { style: { color: C.muted, fontSize: 11 } }, "保存中…") : null
            )
        ),
        // 错误提示
        err ? h("div", { style: S.errBar }, "⚠ " + err) : null,
        // 应用网格
        h("div", { style: S.body },
            apps.length === 0
                ? h("div", { style: S.empty }, "暂无应用")
                : h("div", { style: S.grid },
                    apps.map(function (app) {
                      var isDefault = app.id === effectiveDefaultId;
                      return h("div", {
                            key: app.id,
                            style: Object.assign({}, S.card, isDefault ? S.cardDefault : {}),
                          },
                          h("div", { style: S.cardHead },
                              h("span", { style: S.cardIcon }, app.icon || "🧩"),
                              h("span", { style: S.cardName }, app.name || app.id),
                              isDefault ? h("span", { style: S.badge }, "默认") : null
                          ),
                          h("div", { style: S.cardVer }, "v" + (app.version || "0.0.0")),
                          h("div", { style: S.cardActions },
                              h("a", {
                                style: S.btn,
                                href: app.path || ("/apps/" + app.id),
                              }, "打开"),
                              isDefault
                                  ? h("button", { style: S.btnDisabled, disabled: true }, "已默认")
                                  : h("button", {
                                    style: S.btnPrimary,
                                    onClick: function () { handleSetDefault(app.id); },
                                    disabled: saving,
                                  }, saving ? "保存中…" : "默认启动")
                          )
                      );
                    })
                )
        )
    );
  }

  // ---------- 注册（双显示模式：应用栏目 + 侧边栏） ----------
  // 1. 应用栏目
  if (QP.registerRoutes) {
    try {
      QP.registerRoutes(PLUGIN_ID, [{
        path: "/apps/" + PLUGIN_ID,
        component: App,
        label: PLUGIN_NAME,
        icon: "🏠",
      }]);
      console.info("[" + PLUGIN_ID + "] registered via registerRoutes");
    } catch (e) {
      console.warn("[" + PLUGIN_ID + "] registerRoutes failed:", e);
    }
  }

  // 2. 侧边栏菜单
  if (QP.menu && QP.menu.add) {
    try {
      QP.menu.add(PLUGIN_ID, [{
        id: PLUGIN_ID + ".menu",
        location: "primary.settings",
        label: PLUGIN_NAME,
        icon: function () { return h("span", { style: { fontSize: 18 } }, "🏠"); },
        route: PLUGIN_ID + ".home",
        order: 10,
      }]);
      console.info("[" + PLUGIN_ID + "] registered via menu.add");
    } catch (e) {
      console.warn("[" + PLUGIN_ID + "] menu.add failed:", e);
    }
  }

  // 3. 侧边栏路由
  if (QP.route && QP.route.add) {
    try {
      QP.route.add(PLUGIN_ID, [{
        id: PLUGIN_ID + ".home",
        path: "/plugin/" + PLUGIN_ID,
        component: App,
      }]);
      console.info("[" + PLUGIN_ID + "] registered via route.add");
    } catch (e) {
      console.warn("[" + PLUGIN_ID + "] route.add failed:", e);
    }
  }
})();
