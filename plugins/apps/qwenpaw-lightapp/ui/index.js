/**
 * QwenPaw 轻应用管理器 v0.1.0 — 前端 GUI
 * 支持通过iframe显示用户配置的URL，可指定启动时窗口大小，
 * 数据以JSON方式保存在后端接口的磁盘上
 * 与文件浏览器插件同一套开发范式：React.createElement + 样式对象 + GitHub Dark。
 */
(function () {
  "use strict";

  if (!window.QwenPaw || !window.QwenPaw.host) {
    console.error("[qwenpaw-lightapp] QwenPaw not ready");
    return;
  }

  var QP = window.QwenPaw;
  var React = QP.host.React;
  var h = React.createElement;

  var PLUGIN_ID = "qwenpaw-lightapp";
  var PLUGIN_NAME = "轻应用管理器";
  var VERSION = "0.1.0";
  var API_BASE = "/api/qwenpaw-lightapp";

  // localStorage 键
  var LS_CURRENT_APP = "qwenpaw-lightapp:currentApp";

  // fetch 封装
  function fetchJson(url, opts) {
    var o = opts || {};
    return fetch(url, {
      method: o.method || "GET",
      headers: o.body ? { "Content-Type": "application/json" } : undefined,
      body: o.body ? JSON.stringify(o.body) : undefined,
    }).then(function (r) {
      // 非 2xx 一律抛错：后端错误体是 {"detail": "..."}（无 ok 字段），
      // 不检查 HTTP 状态会把错误响应当成功数据，导致渲染崩溃
      if (!r.ok) {
        return r.json().catch(function () { return {}; }).then(function (body) {
          var msg = (body && (body.detail || body.error || body.message)) || ("HTTP " + r.status);
          var err = new Error(msg);
          err.status = r.status;
          throw err;
        });
      }
      return r.json();
    });
  }

  // 样式对象（灰白色方案）
  var styles = {
    app: {
      display: "flex",
      height: "100%",
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
      color: "#333333",
      backgroundColor: "#ffffff",
    },
    sidebar: {
      width: "220px",
      borderRight: "1px solid #dddddd",
      backgroundColor: "#f8f9fa",
      overflowY: "auto",
      padding: "16px",
    },
    main: {
      flex: 1,
      display: "flex",
      flexDirection: "column",
      overflow: "hidden",
    },
    header: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      padding: "0 16px 16px",
      borderBottom: "1px solid #dddddd",
    },
    title: {
      fontSize: "18px",
      fontWeight: "600",
      margin: 0,
      color: "#333333",
    },
    version: {
      fontSize: "12px",
      color: "#666666",
    },
    toolbar: {
      display: "flex",
      gap: "8px",
      padding: "8px 16px",
      borderBottom: "1px solid #dddddd",
      backgroundColor: "#f8f9fa",
    },
    btn: {
      padding: "6px 12px",
      fontSize: "13px",
      fontWeight: "500",
      color: "#333333",
      backgroundColor: "#ffffff",
      border: "1px solid #dddddd",
      borderRadius: "3px",
      cursor: "pointer",
    },
    btnPrimary: {
      backgroundColor: "#007bff",
      borderColor: "#007bff",
      color: "#ffffff",
    },
    btnDanger: {
      backgroundColor: "#dc3545",
      borderColor: "#dc3545",
      color: "#ffffff",
    },
    input: {
      padding: "8px 12px",
      fontSize: "13px",
      border: "1px solid #dddddd",
      borderRadius: "3px",
      backgroundColor: "#ffffff",
      color: "#333333",
      width: "100%",
      boxSizing: "border-box",
    },
    formGroup: {
      marginBottom: "12px",
    },
    label: {
      display: "block",
      marginBottom: "4px",
      fontSize: "13px",
      fontWeight: "500",
      color: "#333333",
    },
    listItem: {
      padding: "12px",
      borderBottom: "1px solid #eeeeee",
      cursor: "pointer",
      display: "flex",
      alignItems: "center",
    },
    listItemActive: {
      backgroundColor: "#e3f2fd",
    },
    listItemName: {
      fontSize: "14px",
      fontWeight: "500",
      marginBottom: "4px",
      color: "#333333",
    },
    listItemUrl: {
      fontSize: "12px",
      color: "#666666",
      wordBreak: "break-all",
    },
    listItemSize: {
      fontSize: "12px",
      color: "#666666",
    },
    modalOverlay: {
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: "rgba(0, 0, 0, 0.5)",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      zIndex: 1000,
    },
    modalContent: {
      backgroundColor: "#ffffff",
      border: "1px solid #dddddd",
      borderRadius: "6px",
      width: "400px",
      maxHeight: "80vh",
      overflowY: "auto",
    },
    modalHeader: {
      padding: "16px",
      borderBottom: "1px solid #dddddd",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
    },
    modalTitle: {
      fontSize: "16px",
      fontWeight: "600",
      margin: 0,
      color: "#333333",
    },
    modalBody: {
      padding: "16px",
    },
    modalFooter: {
      padding: "16px",
      borderTop: "1px solid #dddddd",
      display: "flex",
      justifyContent: "flex-end",
      gap: "8px",
    },
    iframeContainer: {
      flex: 1,
      position: "relative",
      overflow: "hidden",
    },
    iframe: {
      position: "absolute",
      top: 0,
      left: 0,
      width: "100%",
      height: "100%",
      border: "none",
    },
    statusBar: {
      padding: "8px 16px",
      fontSize: "12px",
      color: "#666666",
      borderTop: "1px solid #dddddd",
      backgroundColor: "#f8f9fa",
    },
  };

  // 加载外部样式表
  function loadStylesheet(url) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = url;
    document.head.appendChild(link);
  }

  // 使用
  loadStylesheet('/api/frontend_plugin/qwenpaw-lightapp/files/ui/styles.css');

  // 主组件
  function LightAppManager() {
    var [apps, setApps] = React.useState([]);
    var [currentAppId, setCurrentAppId] = React.useState(null);
    var [loading, setLoading] = React.useState(true);
    var [modalVisible, setModalVisible] = React.useState(false);
    var [editMode, setEditMode] = React.useState(false);
    var [formData, setFormData] = React.useState({
      name: "",
      url: "",
      width: "100%",
      height: "100%",
      x: 0,
      y: 0,
      desktop: false,
    });
    var [statusMessage, setStatusMessage] = React.useState("");

    // 加载应用列表
    React.useEffect(function () {
      loadApps();
    }, []);

    function loadApps() {
      setLoading(true);
      fetchJson(API_BASE + "/apps")
        .then(function (res) {
          if (res.ok) {
            setApps(res.apps || []);
            // 如果没有当前选中的应用且有应用存在，则选中第一个
            if (currentAppId === null && apps.length > 0) {
              setCurrentAppId(0);
              var lsCurrent = localStorage.getItem(LS_CURRENT_APP);
              if (lsCurrent !== null) {
                var parsed = parseInt(lsCurrent, 10);
                if (!isNaN(parsed) && parsed >= 0 && parsed < apps.length) {
                  setCurrentAppId(parsed);
                }
              }
            }
          } else {
            setStatusMessage("加载应用列表失败: " + (res.detail || "未知错误"));
          }
        })
        .catch(function (err) {
          setStatusMessage("加载应用列表失败: " + err.message);
        })
        .finally(function () {
          setLoading(false);
        });
    }

    // 保存当前选中的应用到localStorage
    React.useEffect(function () {
      if (currentAppId !== null) {
        localStorage.setItem(LS_CURRENT_APP, String(currentAppId));
      }
    }, [currentAppId]);

    // 创建新应用
    function handleCreateApp() {
      if (!formData.name.trim() || !formData.url.trim()) {
        setStatusMessage("名称和URL不能为空");
        return;
      }

      if (!formData.url.startsWith("http://") && !formData.url.startsWith("https://")) {
        setStatusMessage("URL必须以http://或https://开头");
        return;
      }

      setLoading(true);
      fetchJson(API_BASE + "/apps", {
        method: "POST",
        body: {
          name: formData.name.trim(),
          url: formData.url.trim(),
          width: formData.width || "100%",
          height: formData.height || "100%",
          x: parseInt(formData.x) || 0,
          y: parseInt(formData.y) || 0,
          desktop: formData.desktop || false,
        },
      })
        .then(function (res) {
          if (res.ok) {
            setStatusMessage("应用创建成功");
            loadApps();
            // 清空表单并切换到新创建的应用
            setFormData({
              name: "",
              url: "",
              width: "100%",
              height: "100%",
              x: 0,
              y: 0,
              desktop: false,
            });
            setCurrentAppId(res.id);
            setModalVisible(false);
          } else {
            setStatusMessage("创建应用失败: " + (res.detail || "未知错误"));
          }
        })
        .catch(function (err) {
          setStatusMessage("创建应用失败: " + err.message);
        })
        .finally(function () {
          setLoading(false);
        });
    }

    // 更新应用
    function handleUpdateApp() {
      if (currentAppId === null) return;

      if (!formData.name.trim() || !formData.url.trim()) {
        setStatusMessage("名称和URL不能为空");
        return;
      }

      if (!formData.url.startsWith("http://") && !formData.url.startsWith("https://")) {
        setStatusMessage("URL必须以http://或https://开头");
        return;
      }

      setLoading(true);
      fetchJson(API_BASE + "/apps/" + currentAppId, {
        method: "PUT",
        body: {
          name: formData.name.trim(),
          url: formData.url.trim(),
          width: formData.width,
          height: formData.height,
          x: parseInt(formData.x) || 0,
          y: parseInt(formData.y) || 0,
          desktop: formData.desktop || false,
        },
      })
        .then(function (res) {
          if (res.ok) {
            setStatusMessage("应用更新成功");
            loadApps();
            setEditMode(false);
            setModalVisible(false);
          } else {
            setStatusMessage("更新应用失败: " + (res.detail || "未知错误"));
          }
        })
        .catch(function (err) {
          setStatusMessage("更新应用失败: " + err.message);
        })
        .finally(function () {
          setLoading(false);
        });
    }

    // 删除应用
    function handleDeleteApp() {
      if (currentAppId === null || !window.confirm("确定要删除此应用吗？此操作不可恢复。")) {
        return;
      }

      setLoading(true);
      fetchJson(API_BASE + "/apps/" + currentAppId, {
        method: "DELETE",
      })
        .then(function (res) {
          if (res.ok) {
            setStatusMessage("应用删除成功");
            loadApps();
            // 如果删除的是当前选中的应用，则选择下一个或清空
            if (currentAppId === apps.length) {
              setCurrentAppId(Math.max(0, apps.length - 1));
            }
          } else {
            setStatusMessage("删除应用失败: " + (res.detail || "未知错误"));
          }
        })
        .catch(function (err) {
          setStatusMessage("删除应用失败: " + err.message);
        })
        .finally(function () {
          setLoading(false);
          setModalVisible(false);
        });
    }

    // 切换编辑模式
    function handleEditApp(index) {
      try {
        // 检查索引是否有效
        if (index === null || index === undefined || index < 0 || index >= apps.length) {
          return;
        }
        var app = apps[index];
        // 检查应用是否存在
        if (!app) {
          return;
        }

        setEditMode(true);
        setCurrentAppId(index);
        setFormData({
          name: app.name || "",
          url: app.url || "",
          width: app.width || "100%",
          height: app.height || "100%",
          x: app.x || 0,
          y: app.y || 0,
          desktop: app.desktop || false,
        });
        setModalVisible(true);
      } catch (error) {
        console.error("Error in handleEditApp:", error);
      }
    }

    // 取消编辑
    function handleCancelEdit() {
      setEditMode(false);
      // 恢复原始数据
      if (currentAppId !== null && apps[currentAppId]) {
        var app = apps[currentAppId];
        setFormData({
          name: app.name || "",
          url: app.url || "",
          width: app.width || "100%",
          height: app.height || "100%",
          x: app.x || 0,
          y: app.y || 0,
          desktop: app.desktop || false,
        });
      } else {
        setFormData({
          name: "",
          url: "",
          width: "100%",
          height: "100%",
          x: 0,
          y: 0,
          desktop: false,
        });
      }
      setModalVisible(false);
    }

    // 选择应用
    function handleSelectApp(index) {
      setCurrentAppId(index);
      setEditMode(false);
    }

    // 清除状态消息
    function clearStatusMessage() {
      setStatusMessage("");
    }

    // 渲染应用列表项
    function renderAppItem(app, index) {
      var isActive = index === currentAppId;
      return h("div", {
        key: index,
        className: "list-item",
        style: Object.assign({}, styles.listItem, isActive ? styles.listItemActive : {}, { display: "flex", alignItems: "center" }),
        onClick: function () {
          handleSelectApp(index);
        },
      }, [
        h("div", {
          style: Object.assign({}, styles.listItemName, { flexGrow: 1, minWidth: 0 }),
        }, app.name || "未命名应用"),
        h("button", {
          style: Object.assign({}, styles.btn, { padding: "4px 8px", fontSize: "11px", marginLeft: "8px" }),
          onClick: function (e) {
            e.stopPropagation(); // 防止触发列表项点击事件
            handleEditApp(index);
          },
          title: "编辑"
        }, "编辑"),
      ]);
    }

    // 渲染表单
    function renderForm() {
      return h("div", null, [
        h("div", {
          className: "form-group",
          style: styles.formGroup,
        }, [
          h("label", {
            style: styles.label,
          }, "应用名称"),
          h("input", {
            style: styles.input,
            type: "text",
            value: formData.name,
            onChange: function (e) {
              setFormData(function (prev) {
                return Object.assign({}, prev, { name: e.target.value });
              });
            },
            placeholder: "请输入应用名称",
          }),
        ]),
        h("div", {
          className: "form-group",
          style: styles.formGroup,
        }, [
          h("label", {
            style: styles.label,
          }, "应用URL"),
          h("input", {
            style: styles.input,
            type: "text",
            value: formData.url,
            onChange: function (e) {
              setFormData(function (prev) {
                return Object.assign({}, prev, { url: e.target.value });
              });
            },
            placeholder: "例如：https://example.com",
          }),
        ]),
        h("div", {
          className: "form-group",
          style: styles.formGroup,
        }, [
          h("label", {
            style: styles.label,
          }, "宽度"),
          h("input", {
            style: styles.input,
            type: "text",
            value: formData.width,
            onChange: function (e) {
              setFormData(function (prev) {
                return Object.assign({}, prev, { width: e.target.value });
              });
            },
            placeholder: "例如：100% 或 800px",
          }),
        ]),
        h("div", {
          className: "form-group",
          style: styles.formGroup,
        }, [
          h("label", {
            style: styles.label,
          }, "高度"),
          h("input", {
            style: styles.input,
            type: "text",
            value: formData.height,
            onChange: function (e) {
              setFormData(function (prev) {
                return Object.assign({}, prev, { height: e.target.value });
              });
            },
            placeholder: "例如：100% 或 600px",
          }),
        ]),
        h("div", {
          className: "form-group",
          style: styles.formGroup,
        }, [
          h("label", {
            style: styles.label,
          }, "X 坐标"),
          h("input", {
            style: styles.input,
            type: "number",
            value: formData.x,
            onChange: function (e) {
              setFormData(function (prev) {
                return Object.assign({}, prev, { x: parseInt(e.target.value) || 0 });
              });
            },
            placeholder: "水平偏移（像素）",
          }),
        ]),
        h("div", {
          className: "form-group",
          style: styles.formGroup,
        }, [
          h("label", {
            style: styles.label,
          }, "Y 坐标"),
          h("input", {
            style: styles.input,
            type: "number",
            value: formData.y,
            onChange: function (e) {
              setFormData(function (prev) {
                return Object.assign({}, prev, { y: parseInt(e.target.value) || 0 });
              });
            },
            placeholder: "垂直偏移（像素）",
          }),
        ]),
        h("div", {
          className: "form-group",
          style: styles.formGroup,
        }, [
          h("label", {
            style: styles.label,
          }, "在桌面显示"),
          h("input", {
            style: Object.assign({}, styles.input, { width: "auto", marginRight: "8px" }),
            type: "checkbox",
            checked: formData.desktop,
            onChange: function (e) {
              setFormData(function (prev) {
                return Object.assign({}, prev, { desktop: e.target.checked });
              });
            },
          }),
        ]),
      ]);
    }

    // 渲染模态框
    function renderModal() {
      if (!modalVisible) return null;

      return h("div", {
        style: styles.modalOverlay,
        onClick: function (e) {
          if (e.target === e.currentTarget) {
            setModalVisible(false);
          }
        },
      }, [
        h("div", {
          style: styles.modalContent,
        }, [
          h("div", {
            style: styles.modalHeader,
          }, [
            h("h3", {
              style: styles.modalTitle,
            }, editMode ? "编辑应用" : "添加应用"),
            h("button", {
              style: Object.assign({}, styles.btn, { padding: "4px 8px", fontSize: "11px" }),
              onClick: function () {
                setModalVisible(false);
              },
            }, "×"),
          ]),
          h("div", {
            style: styles.modalBody,
          }, [
            renderForm(),
          ]),
          h("div", {
            style: styles.modalFooter,
          }, [
            h("button", {
              style: Object.assign({}, styles.btn, { marginRight: "8px" }),
              onClick: editMode ? handleCancelEdit : function () {
                setModalVisible(false);
              },
            }, editMode ? "取消" : "关闭"),
            editMode ? h("button", {
              style: Object.assign({}, styles.btn, styles.btnDanger),
              onClick: function () {
                if (currentAppId === null || !window.confirm("确定要删除此应用吗？此操作不可恢复。")) {
                  return;
                }

                setLoading(true);
                fetchJson(API_BASE + "/apps/" + currentAppId, {
                  method: "DELETE",
                })
                .then(function (res) {
                  if (res.ok) {
                    setStatusMessage("应用删除成功");
                    loadApps();
                    // 如果删除的是当前选中的应用，则选择下一个或清空
                    if (currentAppId === apps.length) {
                      setCurrentAppId(Math.max(0, apps.length - 1));
                    } else if (currentAppId >= apps.length && apps.length > 0) {
                      setCurrentAppId(apps.length - 1);
                    } else if (apps.length === 0) {
                      setCurrentAppId(null);
                    }
                    setModalVisible(false);
                    setEditMode(false);
                  } else {
                    setStatusMessage("删除应用失败: " + (res.detail || "未知错误"));
                  }
                })
                .catch(function (err) {
                  setStatusMessage("删除应用失败: " + err.message);
                })
                .finally(function () {
                  setLoading(false);
                });
              },
            }, "删除") : null,
            h("button", {
              style: Object.assign({}, styles.btn, editMode ? styles.btnPrimary : styles.btn),
              onClick: editMode ? handleUpdateApp : handleCreateApp,
            }, editMode ? "更新" : "添加"),
          ]),
        ]),
      ]);
    }

    return h("div", {
      style: styles.app,
    }, [
      // 侧边栏
      h("div", {
        style: styles.sidebar,
      }, [
        h("div", {
          style: styles.header,
        }, [
          h("h3", {
            style: styles.title,
          }, PLUGIN_NAME),
          h("div", {
            style: styles.version,
          }, "v" + VERSION),
        ]),
        h("div", {
          style: styles.toolbar,
        }, [
          h("button", {
            style: Object.assign({}, styles.btn, styles.btnPrimary),
            onClick: function () {
              setModalVisible(true);
              setEditMode(false);
              setFormData({
                name: "",
                url: "",
                width: "100%",
                height: "100%",
                x: 0,
                y: 0,
              });
            },
          }, "+ 添加应用"),
        ]),
        h("div", {
          style: {
            marginTop: "16px",
            paddingTop: "16px",
            borderTop: "1px solid #dddddd",
          },
        }, [
          h("p", {
            style: {
              margin: 0,
              fontSize: "12px",
              color: "#666666",
            },
          }, "共 " + apps.length + " 个应用"),
          h("div", {
            style: {
              marginTop: "8px",
            },
          }, [
            loading ? h("div", {
              style: {
                textAlign: "center",
                padding: "8px",
                color: "#666666",
              },
            }, "加载中...") : apps.length === 0 ? h("div", {
              style: {
                textAlign: "center",
                padding: "8px",
                color: "#666666",
              },
            }, "暂无应用") : h("div", null, apps.map(renderAppItem)),
          ]),
        ]),
      ]),

      // 主内容区
      h("div", {
        style: styles.main,
      }, [
        h("div", {
          style: styles.header,
        }, [
          h("h3", {
            style: styles.title,
          }, currentAppId !== null && apps[currentAppId] ? apps[currentAppId].name : "未选择应用"),
          h("div", {
            style: styles.version,
          }, currentAppId !== null ? "ID: " + currentAppId : ""),
        ]),
        h("div", {
          style: styles.iframeContainer,
        }, [
          currentAppId !== null && apps[currentAppId] ? h("iframe", {
            style: styles.iframe,
            src: apps[currentAppId].url,
          }) : h("div", {
            style: {
              flex: 1,
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              color: "#666666",
              fontSize: "14px",
            },
          }, "请从左侧选择一个应用或添加新应用"),
        ]),
        h("div", {
          style: styles.statusBar,
        }, statusMessage ? h("span", null, statusMessage) : h("span", null, "就绪")),
      ]),

      // 模态框
      renderModal(),
    ]);
  }

  // 注册插件
  function registerPlugin() {
    if (!QP.registerRoutes) {
      console.error("[qwenpaw-lightapp] 插件系统未就绪");
      return;
    }
    QP.registerRoutes(PLUGIN_ID, [{
      path: "/apps/" + PLUGIN_ID,
      component: LightAppManager,
      label: PLUGIN_NAME,
      icon: "📱",
      priority: 100
    }]);
    console.log('[轻应用管理] 已注册路由');
  }

  // 等待QwenPaw就绪
  if (window.QwenPaw && window.QwenPaw.host && window.QwenPaw.host.React) {
    registerPlugin();
  } else {
    window.addEventListener("QwenPawReady", registerPlugin);
  }
})();