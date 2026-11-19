(function () {
  const pluginId = "agent-flow-designer";
  const QwenPaw = window.QwenPaw;
  const host = QwenPaw && QwenPaw.host;
  const React = host && host.React;
  if (!QwenPaw || !React || !host.getApiUrl || !QwenPaw.registerRoutes) {
    console.warn("[agent-flow-designer] QwenPaw PawApp host API is unavailable.");
    return;
  }

  function AgentFlowDesignerFrame() {
    const frameRef = React.useRef(null);
    const [iframeSrc, setIframeSrc] = React.useState(null);
    const [sessionError, setSessionError] = React.useState(null);
    const [loading, setLoading] = React.useState(true);
    const renewTimerRef = React.useRef(null);

    // 清理定时器
    React.useEffect(() => {
      return () => {
        if (renewTimerRef.current) {
          clearTimeout(renewTimerRef.current);
        }
      };
    }, []);

    // 获取或续签会话
    const acquireSession = React.useCallback(async () => {
      try {
        setSessionError(null);
        setLoading(true);

        // 尝试获取浏览器会话(Hub 模式)
        const session = await host.prepareBrowserSession(pluginId);

        if (!session) {
          // 非 Hub 模式,直接使用原始 URL
          const directUrl = host.getApiUrl(
            "/frontend_plugin/" + pluginId + "/files/ui/dist/index.html"
          );
          setIframeSrc(directUrl);
          setLoading(false);
          return;
        }

        // Hub 模式:构建带会话 Cookie 的 URL
        const baseUrl = host.getApiUrl(
          "/frontend_plugin/" + pluginId + "/files/ui/dist/index.html"
        );
        setIframeSrc(baseUrl);
        setLoading(false);

        // 设置自动续签(提前 60 秒)
        if (session.expires_in) {
          const renewDelay = Math.max((session.expires_in - 60) * 1000, 5000);
          if (renewTimerRef.current) {
            clearTimeout(renewTimerRef.current);
          }
          renewTimerRef.current = setTimeout(() => {
            acquireSession();
          }, renewDelay);
        }
      } catch (err) {
        console.error("[agent-flow-designer] Session acquisition failed:", err);
        setSessionError(err.message || "鉴权失败");
        setLoading(false);
      }
    }, []);

    // 首次挂载时获取会话
    React.useEffect(() => {
      acquireSession();
    }, [acquireSession]);

    // 加载状态
    if (loading) {
      return React.createElement("div", {
        style: {
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#f5f5f5",
          color: "#666",
          fontSize: 14,
        },
      }, "正在初始化 AFD...");
    }

    // 错误状态
    if (sessionError) {
      return React.createElement("div", {
        style: {
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: "#fff2f0",
          color: "#cf1322",
          padding: 20,
        },
      },
        React.createElement("div", { style: { marginBottom: 16, fontSize: 16 } },
          "AFD 鉴权失败: " + sessionError
        ),
        React.createElement("button", {
          onClick: acquireSession,
          style: {
            padding: "8px 16px",
            background: "#1890ff",
            color: "#fff",
            border: "none",
            borderRadius: 4,
            cursor: "pointer",
          },
        }, "重试")
      );
    }

    // 正常渲染
    return React.createElement("div", {
      style: {
        width: "100%",
        height: "100%",
        overflow: "hidden",
      },
    }, React.createElement("iframe", {
      ref: frameRef,
      title: "AFD",
      src: iframeSrc,
      allowFullScreen: true,
      style: {
        width: "100%",
        height: "100%",
        border: 0,
        display: "block",
      },
    }));
  }

  QwenPaw.registerRoutes(pluginId, [
    {
      path: "/apps/agent-flow-designer",
      component: AgentFlowDesignerFrame,
      label: "AFD",
      icon: "🧩",
    },
  ]);

  // 侧边栏快捷入口：宿主不会为 /apps/ 路由自动生成菜单项，
  // 需另注册一条非 /apps/ 路由并用 menu.add 挂到侧边栏。
  try {
    if (QwenPaw.menu && QwenPaw.route) {
      QwenPaw.menu.add(pluginId, {
        id: "agent-flow-designer.entry",
        label: "AFD",
        icon: React.createElement(
          "span",
          { style: { fontSize: 16 } },
          "🧩"
        ),
        route: "agent-flow-designer.page",
        location: "primary.agentScoped",
        order: 20,
      });
      QwenPaw.route.add(pluginId, {
        id: "agent-flow-designer.page",
        path: "/agent-flow-designer",
        component: AgentFlowDesignerFrame,
      });
    }
  } catch (e) {
    console.error("[agent-flow-designer] 注册侧边栏菜单失败：", e);
  }

  console.info("[agent-flow-designer] registered route /apps/agent-flow-designer");
})();
