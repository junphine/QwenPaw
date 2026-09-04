/**
 * Memory View - 三层记忆系统
 */
const { React, ReactDOM, antd } = window.QwenPaw.host;
const { useState, useEffect, useCallback } = React;

interface MemoryViewProps {
  api?: any;
}

export const MemoryView: React.FC<MemoryViewProps> = ({ api }) => {
  const [traces, setTraces] = useState<any[]>([]);
  const [documents, setDocuments] = useState<any[]>([]);
  const [consolidated, setConsolidated] = useState<any[]>([]);
  const [memoryStats, setMemoryStats] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('traces');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 加载记忆统计
    fetch('/plugins/daydayup/memory/stats?user_id=default')
      .then(res => res.json())
      .then(data => {
        setMemoryStats(data);
      })
      .catch(err => {
        console.error('Failed to load memory stats:', err);
      });

    // 加载三层记忆数据
    fetch('/plugins/daydayup/memory/overview?user_id=default')
      .then(res => res.json())
      .then(data => {
        setTraces(data.traces || []);
        setDocuments(data.documents || []);
        setConsolidated(data.consolidated || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load memory overview:', err);
        setLoading(false);
      });
  }, []);

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
  };

  const createTrace = async () => {
    // TODO: 创建新的trace记录
    alert('创建记忆痕迹功能开发中...');
  };

  const consolidateMemories = async () => {
    // TODO: 触发记忆巩固过程
    alert('记忆巩固功能开发中...');
  };

  if (loading) {
    return (
      <div className="view-loading">
        <div className="loading-spinner">🧠</div>
        <p>加载中...</p>
      </div>
    );
  }

  return (
    <div className="memory-view">
      <div className="memory-header">
        <h2>三层记忆系统</h2>
        <div className="memory-tabs">
          <button
            className={`tab-btn ${activeTab === 'traces' ? 'active' : ''}`}
            onClick={() => handleTabChange('traces')}
          >
            L1 Trace ({traces.length})
          </button>
          <button
            className={`tab-btn ${activeTab === 'documents' ? 'active' : ''}`}
            onClick={() => handleTabChange('documents')}
          >
            L2 Document ({documents.length})
          </button>
          <button
            className={`tab-btn ${activeTab === 'consolidated' ? 'active' : ''}`}
            onClick={() => handleTabChange('consolidated')}
          >
            L3 Consolidated ({consolidated.length})
          </button>
        </div>
        <div className="memory-actions">
          <button className="create-trace-btn" onClick={createTrace}>
            <span>+</span>
            <span>新建痕迹</span>
          </button>
          <button className="consolidate-btn" onClick={consolidateMemories}>
            巩固记忆
          </button>
        </div>
      </div>

      <div className="memory-stats">
        {memoryStats && (
          <div className="stats-grid">
            <div className="stat-card">
              <span className="stat-icon">📝</span>
              <span className="stat-value">{memoryStats.total_traces}</span>
              <span className="stat-label">痕迹条目</span>
            </div>
            <div className="stat-card">
              <span className="stat-icon">📄</span>
              <span className="stat-value">{memoryStats.total_documents}</span>
              <span className="stat-label">文档数量</span>
            </div>
            <div className="stat-card">
              <span className="stat-icon">🧠</span>
              <span className="stat-value">{memoryStats.total_consolidated}</span>
              <span className="stat-label">巩固知识</span>
            </div>
            <div className="stat-card">
              <span className="stat-icon">⚡</span>
              <span className="stat-value">{memoryStats.consolidation_rate}%</span>
              <span className="stat-label">巩固效率</span>
            </div>
          </div>
        )}
      </div>

      <div className="memory-content">
        {activeTab === 'traces' && (
          <div className="traces-list">
            <h3>L1 Trace - 原始痕迹</h3>
            <p className="traces-desc">
              记录学习过程中的原始事件、想法和观察
            </p>
            <div className="traces-items">
              {traces.length > 0 ? (
                traces.map((trace, index) => (
                  <div key={trace.id} className="trace-item">
                    <div className="trace-header">
                      <span className="trace-type">{trace.type}</span>
                      <span className="trace-time">
                        {new Date(trace.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <div className="trace-content">
                      <p>{trace.content}</p>
                      {trace.metadata && (
                        <div className="trace-meta">
                          <small>来源：{trace.metadata.source}</small>
                        </div>
                      )}
                    </div>
                    <div className="trace-tags">
                      {trace.tags?.map((tag: string) => (
                        <span key={tag} className="tag">{tag}</span>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state">
                  <p>暂无记忆痕迹</p>
                  <button className="create-trace-btn" onClick={createTrace}>
                    创建第一条痕迹
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="documents-list">
            <h3>L2 Document - 主题文档</h3>
            <p className="documents-desc">
              将相关的痕迹整合成主题文档，带有引用和上下文
            </p>
            <div className="documents-items">
              {documents.length > 0 ? (
                documents.map((doc, index) => (
                  <div key={doc.id} className="document-item">
                    <div className="document-header">
                      <h4>{doc.title}</h4>
                      <span className="doc-count">
                        来源 {doc.source_traces?.length || 0} 条痕迹
                      </span>
                    </div>
                    <div className="document-content">
                      <p>{doc.summary}</p>
                      {doc.key_points?.length > 0 && (
                        <div className="key-points">
                          <strong>关键点：</strong>
                          <ul>
                            {doc.key_points.map((point: string, idx: number) => (
                              <li key={idx}>{point}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                    <div className="document-footer">
                      <span className="doc-created">
                        创建于：{new Doc(doc.created_at).toLocaleDateString()}
                      </span>
                      <span className="doc-updated">
                        更新于：{new Date(doc.updated_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state">
                  <p>暂无主题文档</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'consolidated' && (
          <div className="consolidated-list">
            <h3>L3 Consolidated - 巩固知识</h3>
            <p className="consolidated-desc">
              经过提炼和升维的核心知识，可用于迁移学习和创新思维
            </p>
            <div className="consolidated-items">
              {consolidated.length > 0 ? (
                consolidated.map((knowledge, index) => (
                  <div key={knowledge.id} className="knowledge-item">
                    <div className="knowledge-header">
                      <h4>{knowledge.title}</h4>
                      <span className="knowledge-level">
                        Lv.{knowledge.level}
                      </span>
                    </div>
                    <div className="knowledge-content">
                      <p>{knowledge.content}</p>
                      {knowledge.connections?.length > 0 && (
                        <div className="connections">
                          <strong>关联知识：</strong>
                          {knowledge.connections.map((conn: string, idx: number) => (
                            <span key={idx} className="conn-tag">{conn}</span>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="knowledge-footer">
                      <span className="knowledge-source">
                        源自 {knowledge.source_count} 条文档
                      </span>
                      <span className="knowledge-updated">
                        更新于：{new Date(knowledge.updated_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="knowledge-actions">
                      <button className="apply-knowledge-btn">
                        应用知识
                      </button>
                      <button className="share-knowledge-btn">
                        分享知识
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state">
                  <p>暂无巩固知识</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};