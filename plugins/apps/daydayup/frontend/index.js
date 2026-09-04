/**
 * 趣学习 (Daydayup) v2.1.0 - 前端入口
 * 基于 Deep Tutor 架构，融合 QwenPaw 本地智能体
 * Build: 20240810-0900
 * 
 * 八大核心功能：
 * 1. Home - 主页学习空间
 * 2. Partners - AI 学习伙伴 (Deep Tutor Partner)
 * 3. My Agents - 我的智能体 (Deep Tutor Agent)
 * 4. Co-Writer - 协同写作
 * 5. Book - 交互式书本
 * 6. Learning Space - 学习空间
 * 7. Memory - 三层记忆系统 (Deep Tutor Memory)
 * 8. Knowledge Center - 知识中心
 * 
 * 作者：0+1+2≠3 Team 115886
 */

(function() {
  'use strict';

  const pluginId = 'daydayup';

  // 等待 QwenPaw 加载
  if (typeof window.QwenPaw === 'undefined') {
    console.error('[Daydayup] QwenPaw is not defined. Plugin cannot load.');
    return;
  }

  console.log('[Daydayup] Initializing plugin with Deep Tutor integration...');

  const { React, antd } = window.QwenPaw.host;
  
  if (!React || !antd) {
    console.error('[Daydayup] React or antd not available from host');
    return;
  }

  const { useState, useEffect, useCallback } = React;
  const { Layout, Menu, Card, Statistic, Row, Col, Button, Input, Spin, Tag, message } = antd;
  const { Sider, Content, Header } = Layout;

  // API 基础 URL
  const API_BASE = '/plugins/daydayup';

  // 导航配置
  const NAV_ITEMS = [
    { id: 'home', label: '首页', icon: '🏠' },
    { id: 'partners', label: '学习伙伴', icon: '👥' },
    { id: 'agents', label: '我的智能体', icon: '🤖' },
    { id: 'cowriter', label: '协同写作', icon: '✍️' },
    { id: 'book', label: '交互式书本', icon: '📚' },
    { id: 'learning', label: '学习空间', icon: '🎓' },
    { id: 'memory', label: '记忆系统', icon: '🧠' },
    { id: 'knowledge', label: '知识中心', icon: '📖' },
  ];

  // 通用 API 请求函数
  async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    try {
      const response = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        ...options
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`[Daydayup] API Error: ${url}`, error);
      throw error;
    }
  }

  // ==================== 首页组件 ====================
  function HomePage() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
      apiRequest('/home/dashboard?user_id=default')
        .then(data => {
          setData(data);
          setLoading(false);
        })
        .catch(() => setLoading(false));
    }, []);

    if (loading) {
      return React.createElement(Spin, { 
        size: 'large',
        style: { display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }
      });
    }

    return React.createElement('div', { style: { padding: '24px' } },
      React.createElement('h1', { style: { marginBottom: '8px' } }, '欢迎回到趣学习！'),
      React.createElement('p', { style: { color: '#666', marginBottom: '24px' } }, 
        '基于 Deep Tutor 架构的 AI 学习伴侣'),
      
      // 统计卡片
      React.createElement(Row, { gutter: 16, style: { marginBottom: '24px' } },
        React.createElement(Col, { span: 6 },
          React.createElement(Card, null,
            React.createElement(Statistic, {
              title: '最近课程',
              value: data?.recent_courses?.length || 0,
              prefix: '📖'
            })
          )
        ),
        React.createElement(Col, { span: 6 },
          React.createElement(Card, null,
            React.createElement(Statistic, {
              title: '记忆条目',
              value: data?.recent_memories?.length || 0,
              prefix: '🧠'
            })
          )
        ),
        React.createElement(Col, { span: 6 },
          React.createElement(Card, null,
            React.createElement(Statistic, {
              title: '学习伙伴',
              value: data?.active_partners?.length || 0,
              prefix: '👥'
            })
          )
        ),
        React.createElement(Col, { span: 6 },
          React.createElement(Card, null,
            React.createElement(Statistic, {
              title: '智能体',
              value: data?.active_agents?.length || 0,
              prefix: '🤖'
            })
          )
        )
      ),

      // Deep Tutor Capabilities 介绍
      React.createElement(Card, { title: 'Deep Tutor Capabilities', style: { marginBottom: '24px' } },
        React.createElement(Row, { gutter: 16 },
          React.createElement(Col, { span: 8 },
            React.createElement('div', { style: { textAlign: 'center', padding: '16px' } },
              React.createElement('div', { style: { fontSize: '32px' } }, '🎯'),
              React.createElement('div', { style: { fontWeight: 'bold', marginTop: '8px' } }, '深度解题'),
              React.createElement('div', { style: { color: '#666', fontSize: '12px' } }, 'Deep Solve')
            )
          ),
          React.createElement(Col, { span: 8 },
            React.createElement('div', { style: { textAlign: 'center', padding: '16px' } },
              React.createElement('div', { style: { fontSize: '32px' } }, '❓'),
              React.createElement('div', { style: { fontWeight: 'bold', marginTop: '8px' } }, '深度提问'),
              React.createElement('div', { style: { color: '#666', fontSize: '12px' } }, 'Deep Question')
            )
          ),
          React.createElement(Col, { span: 8 },
            React.createElement('div', { style: { textAlign: 'center', padding: '16px' } },
              React.createElement('div', { style: { fontSize: '32px' } }, '🔬'),
              React.createElement('div', { style: { fontWeight: 'bold', marginTop: '8px' } }, '深度研究'),
              React.createElement('div', { style: { color: '#666', fontSize: '12px' } }, 'Deep Research')
            )
          )
        )
      ),

      // 快速开始
      React.createElement(Card, { title: '快速开始' },
        React.createElement(Row, { gutter: 16 },
          React.createElement(Col, { span: 6 },
            React.createElement(Button, { 
              type: 'primary',
              block: true,
              size: 'large',
              onClick: () => window.location.hash = '#/daydayup/partners'
            }, '👥 和学习伙伴聊天')
          ),
          React.createElement(Col, { span: 6 },
            React.createElement(Button, { 
              block: true,
              size: 'large',
              onClick: () => window.location.hash = '#/daydayup/agents'
            }, '🤖 创建智能体')
          ),
          React.createElement(Col, { span: 6 },
            React.createElement(Button, { 
              block: true,
              size: 'large',
              onClick: () => window.location.hash = '#/daydayup/memory'
            }, '🧠 查看记忆')
          ),
          React.createElement(Col, { span: 6 },
            React.createElement(Button, { 
              block: true,
              size: 'large',
              onClick: () => window.location.hash = '#/daydayup/learning'
            }, '🎓 继续学习')
          )
        )
      )
    );
  }

  // ==================== 学习伙伴页面 ====================
  function PartnersPage() {
    const [partners, setPartners] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedPartner, setSelectedPartner] = useState(null);
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');

    useEffect(() => {
      // 加载伙伴列表
      apiRequest('/partners/list')
        .then(data => {
          setPartners(data.partners || []);
          setLoading(false);
        })
        .catch(() => setLoading(false));
    }, []);

    const sendMessage = async () => {
      if (!inputMessage.trim() || !selectedPartner) return;
      
      const userMsg = { role: 'user', content: inputMessage };
      setMessages(prev => [...prev, userMsg]);
      setInputMessage('');

      try {
        const response = await apiRequest('/partners/chat', {
          method: 'POST',
          body: JSON.stringify({
            partner_id: selectedPartner.id,
            user_id: 'default',
            message: inputMessage
          })
        });
        
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: response.message,
          partner: response.partner_name
        }]);
      } catch (e) {
        message.error('发送失败');
      }
    };

    if (loading) return React.createElement(Spin, { size: 'large' });

    return React.createElement('div', { style: { padding: '24px' } },
      React.createElement('h2', null, '学习伙伴'),
      React.createElement('p', { style: { color: '#666' } }, 
        '基于 Deep Tutor Partner 系统的 AI 学习伙伴'),
      
      React.createElement(Row, { gutter: 24, style: { marginTop: '24px' } },
        // 伙伴列表
        React.createElement(Col, { span: 6 },
          React.createElement(Card, { title: '选择伙伴' },
            partners.map(partner => 
              React.createElement('div', {
                key: partner.id,
                style: {
                  padding: '12px',
                  cursor: 'pointer',
                  background: selectedPartner?.id === partner.id ? '#e6f7ff' : 'transparent',
                  borderRadius: '8px',
                  marginBottom: '8px'
                },
                onClick: () => setSelectedPartner(partner)
              },
                React.createElement('div', { style: { fontSize: '24px' } }, partner.avatar),
                React.createElement('div', { style: { fontWeight: 'bold' } }, partner.name),
                React.createElement('div', { style: { fontSize: '12px', color: '#666' } }, partner.personality)
              )
            )
          )
        ),
        
        // 聊天区域
        React.createElement(Col, { span: 18 },
          selectedPartner ? 
            React.createElement(Card, { 
              title: `${selectedPartner.name} - ${selectedPartner.description}`,
              style: { height: '600px' }
            },
              // 消息列表
              React.createElement('div', { 
                style: { 
                  height: '450px', 
                  overflowY: 'auto',
                  border: '1px solid #f0f0f0',
                  borderRadius: '8px',
                  padding: '16px',
                  marginBottom: '16px'
                }
              },
                messages.length === 0 ? 
                  React.createElement('div', { 
                    style: { textAlign: 'center', color: '#999', padding: '40px' }
                  }, '开始和伙伴聊天吧！') :
                  messages.map((msg, idx) => 
                    React.createElement('div', {
                      key: idx,
                      style: {
                        marginBottom: '12px',
                        textAlign: msg.role === 'user' ? 'right' : 'left'
                      }
                    },
                      React.createElement('div', {
                        style: {
                          display: 'inline-block',
                          padding: '12px 16px',
                          borderRadius: '12px',
                          background: msg.role === 'user' ? '#1890ff' : '#f0f0f0',
                          color: msg.role === 'user' ? '#fff' : '#333',
                          maxWidth: '80%'
                        }
                      }, msg.content)
                    )
                  )
              ),
              // 输入区域
              React.createElement(Input.TextArea, {
                value: inputMessage,
                onChange: e => setInputMessage(e.target.value),
                placeholder: '输入消息...',
                rows: 2,
                onPressEnter: e => {
                  if (!e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }
              }),
              React.createElement(Button, {
                type: 'primary',
                style: { marginTop: '8px', float: 'right' },
                onClick: sendMessage
              }, '发送')
            ) :
            React.createElement(Card, { style: { height: '600px', display: 'flex', alignItems: 'center', justifyContent: 'center' } },
              React.createElement('div', { style: { textAlign: 'center', color: '#999' } },
                React.createElement('div', { style: { fontSize: '48px' } }, '👥'),
                React.createElement('div', { style: { marginTop: '16px' } }, '选择一个学习伙伴开始聊天')
              )
            )
        )
      )
    );
  }

  // ==================== 智能体页面 ====================
  function AgentsPage() {
    const [agents, setAgents] = useState([]);
    const [capabilities, setCapabilities] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
      Promise.all([
        apiRequest('/agents/list'),
        apiRequest('/agents/capabilities')
      ]).then(([agentsData, capsData]) => {
        setAgents(agentsData.agents || []);
        setCapabilities(capsData.capabilities || []);
        setLoading(false);
      }).catch(() => setLoading(false));
    }, []);

    if (loading) return React.createElement(Spin, { size: 'large' });

    return React.createElement('div', { style: { padding: '24px' } },
      React.createElement('h2', null, '我的智能体'),
      React.createElement('p', { style: { color: '#666' } }, 
        '基于 Deep Tutor Agent 系统的自定义智能体'),
      
      // Capabilities 展示
      React.createElement(Card, { title: 'Deep Tutor Capabilities', style: { marginTop: '24px', marginBottom: '24px' } },
        React.createElement(Row, { gutter: 16 },
          capabilities.map(cap => 
            React.createElement(Col, { span: 8, key: cap.id, style: { marginBottom: '16px' } },
              React.createElement(Card, { size: 'small' },
                React.createElement('div', { style: { fontWeight: 'bold' } }, cap.name),
                React.createElement('div', { style: { color: '#666', fontSize: '12px' } }, cap.description),
                React.createElement('div', { style: { marginTop: '8px' } },
                  cap.tools.map(tool => 
                    React.createElement(Tag, { size: 'small', key: tool }, tool)
                  )
                )
              )
            )
          )
        )
      ),

      // 智能体列表
      React.createElement(Row, { gutter: 16 },
        agents.map(agent => 
          React.createElement(Col, { span: 8, key: agent.id, style: { marginBottom: '16px' } },
            React.createElement(Card, {
              title: React.createElement('div', null, 
                React.createElement('span', { style: { fontSize: '24px', marginRight: '8px' } }, agent.avatar),
                agent.name
              ),
              extra: React.createElement(Button, { type: 'primary', size: 'small' }, '聊天')
            },
              React.createElement('div', { style: { color: '#666' } }, agent.description),
              React.createElement('div', { style: { marginTop: '8px' } },
                React.createElement(Tag, { color: 'blue' }, agent.capability)
              )
            )
          )
        )
      )
    );
  }

  // ==================== 记忆系统页面 ====================
  function MemoryPage() {
    const [stats, setStats] = useState(null);
    const [activeLayer, setActiveLayer] = useState('L1');

    useEffect(() => {
      apiRequest('/memory/stats?user_id=default')
        .then(data => setStats(data))
        .catch(() => {});
    }, []);

    return React.createElement('div', { style: { padding: '24px' } },
      React.createElement('h2', null, '记忆系统'),
      React.createElement('p', { style: { color: '#666' } }, 
        '基于 Deep Tutor 三层记忆系统：L1 Trace → L2 Document → L3 Consolidated'),
      
      // 三层记忆说明
      React.createElement(Row, { gutter: 16, style: { marginTop: '24px', marginBottom: '24px' } },
        React.createElement(Col, { span: 8 },
          React.createElement(Card, { 
            title: 'L1 - Trace',
            style: { borderTop: '3px solid #1890ff' }
          },
            React.createElement('div', null, '原始事件捕获'),
            React.createElement('div', { style: { color: '#666', fontSize: '12px', marginTop: '8px' } }, 
              'Append-only JSONL，按日期存储'),
            stats && React.createElement(Statistic, { 
              title: '事件数', 
              value: stats.l1_traces,
              style: { marginTop: '16px' }
            })
          )
        ),
        React.createElement(Col, { span: 8 },
          React.createElement(Card, { 
            title: 'L2 - Document',
            style: { borderTop: '3px solid #52c41a' }
          },
            React.createElement('div', null, 'Markdown 文档'),
            React.createElement('div', { style: { color: '#666', fontSize: '12px', marginTop: '8px' } }, 
              '带 footnote-citation 的文档'),
            stats && React.createElement(Statistic, { 
              title: '文档数', 
              value: stats.l2_documents,
              style: { marginTop: '16px' }
            })
          )
        ),
        React.createElement(Col, { span: 8 },
          React.createElement(Card, { 
            title: 'L3 - Consolidated',
            style: { borderTop: '3px solid #faad14' }
          },
            React.createElement('div', null, '整合记忆'),
            React.createElement('div', { style: { color: '#666', fontSize: '12px', marginTop: '8px' } }, 
              'LLM 驱动的 L1/L2 → L3 整合'),
            stats && React.createElement(Statistic, { 
              title: 'Slot 数', 
              value: stats.l3_slots,
              style: { marginTop: '16px' }
            })
          )
        )
      ),

      // Surfaces
      stats && React.createElement(Card, { title: 'Surfaces (记忆来源)' },
        React.createElement(Row, { gutter: 16 },
          stats.surfaces.map(surface => 
            React.createElement(Col, { span: 4, key: surface },
              React.createElement(Tag, { style: { width: '100%', textAlign: 'center' } }, surface)
            )
          )
        )
      )
    );
  }

  // ==================== 占位页面 ====================
  function PlaceholderPage({ icon, title, description }) {
    return React.createElement('div', { 
      style: { 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100%',
        padding: '24px'
      } 
    },
      React.createElement('div', { style: { fontSize: '64px', marginBottom: '24px' } }, icon),
      React.createElement('h2', { style: { marginBottom: '12px' } }, title),
      React.createElement('p', { style: { color: '#666', maxWidth: '500px', textAlign: 'center' } }, description)
    );
  }

  // ==================== 主应用组件 ====================
  function DaydayupApp() {
    const [activeTab, setActiveTab] = useState('home');

    // 根据 hash 路由切换
    useEffect(() => {
      const handleHashChange = () => {
        const hash = window.location.hash.replace('#/daydayup/', '');
        if (hash && NAV_ITEMS.find(item => item.id === hash)) {
          setActiveTab(hash);
        }
      };
      
      handleHashChange();
      window.addEventListener('hashchange', handleHashChange);
      return () => window.removeEventListener('hashchange', handleHashChange);
    }, []);

    const renderContent = () => {
      switch (activeTab) {
        case 'home':
          return React.createElement(HomePage);
        case 'partners':
          return React.createElement(PartnersPage);
        case 'agents':
          return React.createElement(AgentsPage);
        case 'cowriter':
          return React.createElement(PlaceholderPage, {
            icon: '✍️',
            title: '协同写作',
            description: '与 AI 一起写作，获得实时反馈和改进建议。基于 Deep Tutor Co-Writer。'
          });
        case 'book':
          return React.createElement(PlaceholderPage, {
            icon: '📚',
            title: '交互式书本',
            description: '阅读交互式学习材料，边学边练。基于 Deep Tutor BookEngine。'
          });
        case 'learning':
          return React.createElement(PlaceholderPage, {
            icon: '🎓',
            title: '学习空间',
            description: '系统化的课程学习，跟踪学习进度。'
          });
        case 'memory':
          return React.createElement(MemoryPage);
        case 'knowledge':
          return React.createElement(PlaceholderPage, {
            icon: '📖',
            title: '知识中心',
            description: '构建个人知识库，智能检索和问答。基于 Deep Tutor KB。'
          });
        default:
          return React.createElement(HomePage);
      }
    };

    return React.createElement(Layout, { style: { minHeight: '100vh', background: '#f5f5f5' } },
      // 侧边栏
      React.createElement(Sider, { 
        width: 220, 
        theme: 'light',
        style: { 
          borderRight: '1px solid #f0f0f0',
          boxShadow: '2px 0 8px rgba(0,0,0,0.05)'
        }
      },
        // Logo
        React.createElement('div', { 
          style: { 
            padding: '20px',
            borderBottom: '1px solid #f0f0f0',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: '#fff'
          } 
        },
          React.createElement('span', { style: { fontSize: '28px' } }, '📚'),
          React.createElement('div', null,
            React.createElement('div', { style: { fontSize: '16px', fontWeight: 'bold' } }, '趣学习'),
            React.createElement('div', { style: { fontSize: '10px', opacity: 0.8 } }, 'Deep Tutor Powered')
          )
        ),
        // 导航菜单
        React.createElement(Menu, {
          mode: 'inline',
          selectedKeys: [activeTab],
          style: { borderRight: 0, padding: '8px 0' },
          onClick: ({ key }) => {
            setActiveTab(key);
            window.location.hash = `#/daydayup/${key}`;
          },
          items: NAV_ITEMS.map(item => ({
            key: item.id,
            icon: React.createElement('span', { style: { fontSize: '18px' } }, item.icon),
            label: item.label
          }))
        }),
        // 底部信息
        React.createElement('div', { 
          style: { 
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            padding: '12px',
            borderTop: '1px solid #f0f0f0',
            textAlign: 'center',
            fontSize: '11px',
            color: '#999'
          }
        },
          React.createElement('div', null, '0+1+2≠3'),
          React.createElement('div', null, 'Team 115886')
        )
      ),
      
      // 主内容区
      React.createElement(Layout, null,
        React.createElement(Content, { style: { margin: '24px', minHeight: 280 } },
          renderContent()
        )
      )
    );
  }

  // ==================== 注册插件 ====================
  console.log('[Daydayup] Registering plugin...');
  
  try {
      // 注册路由
      if (window.QwenPaw.registerRoutes) {
          window.QwenPaw.registerRoutes(pluginId, [{
              path: "/apps/" + pluginId,
              component: DaydayupApp,
              label: '趣学习',
              icon: "📚",
              priority: 100
          }]);
          console.log('[双虾汇] 已注册路由');
      }
    console.log('[Daydayup] Plugin loaded successfully v2.0.0 with Deep Tutor integration');
  } catch (e) {
    console.error('[Daydayup] Failed to register plugin:', e);
  }
})();
