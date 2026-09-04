/**
 * Home View - 主页学习空间
 */

const { React, ReactDOM, antd } = window.QwenPaw.host;
const { useState, useEffect, useCallback } = React;

interface HomeViewProps {
  api?: any;
}

export const HomeView: React.FC<HomeViewProps> = ({ api }) => {
  const [dashboard, setDashboard] = useState<any>(null);
  const [quickActions, setQuickActions] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 加载仪表板数据
    fetch('/plugins/daydayup/home/dashboard?user_id=default')
      .then(res => res.json())
      .then(data => {
        setDashboard(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load dashboard:', err);
        setLoading(false);
      });

    // 加载快速操作
    fetch('/plugins/daydayup/home/quick-actions')
      .then(res => res.json())
      .then(data => {
        setQuickActions(data.actions || []);
      })
      .catch(err => {
        console.error('Failed to load quick actions:', err);
      });

    // 加载统计
    fetch('/plugins/daydayup/home/stats')
      .then(res => res.json())
      .then(data => {
        setStats(data);
      })
      .catch(err => {
        console.error('Failed to load stats:', err);
      });
  }, []);

  const handleQuickAction = (actionId: string) => {
    console.log('Quick action:', actionId);
    // 处理快速操作
  };

  if (loading) {
    return (
      <div className="view-loading">
        <div className="loading-spinner">🏠</div>
        <p>加载中...</p>
      </div>
    );
  }

  return (
    <div className="home-view">
      {/* 欢迎区域 */}
      <section className="welcome-section">
        <h1>欢迎回到趣学习！</h1>
        <p className="subtitle">继续你的学习之旅</p>
        {stats && (
          <div className="streak-badge">
            <span className="streak-icon">🔥</span>
            <span className="streak-count">连续学习 {stats.streak_days} 天</span>
          </div>
        )}
      </section>

      {/* 快速操作 */}
      <section className="quick-actions-section">
        <h2>快速操作</h2>
        <div className="quick-actions-grid">
          {quickActions.map(action => (
            <button
              key={action.id}
              className="quick-action-card"
              onClick={() => handleQuickAction(action.id)}
            >
              <span className="action-icon">{action.icon}</span>
              <span className="action-name">{action.name}</span>
              <span className="action-desc">{action.description}</span>
            </button>
          ))}
        </div>
      </section>

      {/* 最近课程 */}
      <section className="recent-courses-section">
        <h2>最近学习</h2>
        <div className="courses-list">
          {dashboard?.recent_courses?.map((course: any) => (
            <div key={course.id} className="course-card">
              <div className="course-info">
                <h3>{course.title}</h3>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${course.progress}%` }}
                  />
                </div>
                <span className="progress-text">{course.progress}% 完成</span>
              </div>
              <button className="continue-btn">继续</button>
            </div>
          ))}
        </div>
      </section>

      {/* 学习统计 */}
      {stats && (
        <section className="stats-section">
          <h2>学习统计</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <span className="stat-icon">📚</span>
              <span className="stat-value">{stats.total_courses}</span>
              <span className="stat-label">总课程</span>
            </div>
            <div className="stat-card">
              <span className="stat-icon">✅</span>
              <span className="stat-value">{stats.completed_courses}</span>
              <span className="stat-label">已完成</span>
            </div>
            <div className="stat-card">
              <span className="stat-icon">🧠</span>
              <span className="stat-value">{stats.total_memories}</span>
              <span className="stat-label">记忆条目</span>
            </div>
            <div className="stat-card">
              <span className="stat-icon">⏱️</span>
              <span className="stat-value">{stats.total_study_time}</span>
              <span className="stat-label">学习时长</span>
            </div>
          </div>
        </section>
      )}

      {/* 最近记忆 */}
      <section className="recent-memories-section">
        <h2>最近记忆</h2>
        <div className="memories-list">
          {dashboard?.recent_memories?.map((memory: any) => (
            <div key={memory.id} className="memory-card">
              <span className={`memory-layer layer-${memory.layer}`}>
                {memory.layer.toUpperCase()}
              </span>
              <p className="memory-content">{memory.content}</p>
              <span className="memory-time">
                {new Date(memory.timestamp).toLocaleDateString()}
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};
