/**
 * 趣学习 (Daydayup) - 前端入口
 * 基于 Deep Tutor 架构，适配 QwenPaw 环境
 *
 * 八大核心功能：
 * 1. Home - 主页学习空间
 * 2. Partners - AI 学习伙伴
 * 3. My Agents - 我的智能体
 * 4. Co-Writer - 协同写作
 * 5. Book - 交互式书本
 * 6. Learning Space - 学习空间
 * 7. Memory - 三层记忆系统
 * 8. Knowledge Center - 知识中心
 */


// 等待 QwenPaw 加载
if (typeof window.QwenPaw === 'undefined') {
  console.error('[Daydayup] QwenPaw is not defined. Plugin cannot load.');
}

console.log('[Daydayup] Initializing plugin with Deep Tutor integration...');

const { React, ReactDOM, antd } = window.QwenPaw.host;
const { useState, useEffect, useCallback } = React;
const { createRoot } = ReactDOM;
const { Layout, Menu, Card, Statistic, Row, Col, Button, Input, Spin, Tag, message } = antd;
const { Sider, Content, Header } = Layout;


// API 基础 URL

const pluginId = 'daydayup';


// 组件导入
import { HomeView } from './views/HomeView';
import { PartnersView } from './views/PartnersView';
import { AgentsView } from './views/AgentsView';
import { CoWriterView } from './views/CoWriterView';
import { BookView } from './views/BookView';
import { LearningView } from './views/LearningView';
import { MemoryView } from './views/MemoryView';
import { KnowledgeView } from './views/KnowledgeView';

// 样式
import './styles/index.css';

// 类型定义
interface PluginProps {
  config?: any;
}

// 加载外部样式表
function loadStylesheet(url:string) {
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = url;
  document.head.appendChild(link);
}

// 主应用组件
const DaydayupApp: React.FC<PluginProps> = ({ config }) => {
  const [activeTab, setActiveTab] = useState('home');
  const [pluginInfo, setPluginInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const api = '/plugins/daydayup';
  // 导航项配置
  const navItems = [
    { id: 'home', label: '首页', icon: '🏠' },
    { id: 'partners', label: '学习伙伴', icon: '👥' },
    { id: 'agents', label: '我的智能体', icon: '🤖' },
    { id: 'cowriter', label: '协同写作', icon: '✍️' },
    { id: 'book', label: '交互式书本', icon: '📚' },
    { id: 'learning', label: '学习空间', icon: '🎓' },
    { id: 'memory', label: '记忆系统', icon: '🧠' },
    { id: 'knowledge', label: '知识中心', icon: '📖' },
  ];


  useEffect(() => {
    // 使用
    loadStylesheet('/api/frontend_plugin/daydayup/files/dist/style.css');
    // 获取插件信息
    fetch('/plugins/daydayup/info')
      .then(res => res.json())
      .then(data => {
        setPluginInfo(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load plugin info:', err);
        setLoading(false);
      });
  }, []);

  // 渲染当前视视图
  const renderView = () => {
    switch (activeTab) {
      case 'home':
        return <HomeView api={api} />;
      case 'partners':
        return <PartnersView api={api} />;
      case 'agents':
        return <AgentsView api={api} />;
      case 'cowriter':
        return <CoWriterView api={api} />;
      case 'book':
        return <BookView api={api} />;
      case 'learning':
        return <LearningView api={api} />;
      case 'memory':
        return <MemoryView api={api} />;
      case 'knowledge':
        return <KnowledgeView api={api} />;
      default:
        return <HomeView api={api} />;
    }
  };

  if (loading) {
    return (
      <div className="daydayup-loading">
        <div className="loading-spinner">📚</div>
        <p>正在加载趣学习...</p>
      </div>
    );
  }

  return (
    <div className="daydayup-app">
      {/* 侧边栏导航 */}
      <aside className="daydayup-sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <span className="logo-icon">📚</span>
            <span className="logo-text">趣学习</span>
          </div>
          <div className="version">v{pluginInfo?.version || '2.0.0'}</div>
        </div>

        <nav className="sidebar-nav">
          {navItems.map(item => (
            <button
              key={item.id}
              className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="team-info">
            <span>0+1+2≠3</span>
            <span>Team 115886</span>
          </div>
        </div>
      </aside>

      {/* 主内容区 */}
      <main className="daydayup-main">
        {renderView()}
      </main>
    </div>
  );
};

// 挂载函数
function mount(container: HTMLElement, props?: PluginProps) {
  const root = createRoot(container);
  root.render(<DaydayupApp {...props} />);
  return () => root.unmount();
}

(() => {
  // 注册路由
  if (window.QwenPaw.registerRoutes) {
    window.QwenPaw.registerRoutes(pluginId, [{
        path: "/apps/" + pluginId,
        component: DaydayupApp,
        label: '趣学习',
        icon: "📚",
        priority: 100
    }]);
    console.log('[趣学习] 已注册路由');
  }
})();


