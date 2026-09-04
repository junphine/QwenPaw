/**
 * Knowledge View - 知识中心
 */
const { React, ReactDOM, antd } = window.QwenPaw.host;
const { useState, useEffect, useCallback } = React;

interface KnowledgeViewProps {
  api?: any;
}

export const KnowledgeView: React.FC<KnowledgeViewProps> = ({ api }) => {
  const [knowledgeBase, setKnowledgeBase] = useState<any[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [filteredKnowledge, setFilteredKnowledge] = useState<any[]>([]);
  const [knowledgeStats, setKnowledgeStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 加载知识统计
    fetch('/plugins/daydayup/knowledge/stats?user_id=default')
      .then(res => res.json())
      .then(data => {
        setKnowledgeStats(data);
      })
      .catch(err => {
        console.error('Failed to load knowledge stats:', err);
      });

    // 加载知识库
    fetch('/plugins/daydayup/knowledge/list?user_id=default')
      .then(res => res.json())
      .then(data => {
        setKnowledgeBase(data.knowledge || []);
        // 提取所有分类
        const cats = Array.from(
          new Set(data.knowledge.map((k: any) => k.category))
        );
        setCategories(['all', ...cats]);
        setFilteredKnowledge(data.knowledge || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load knowledge base:', err);
        setLoading(false);
      });
  }, [selectedCategory, searchQuery]);

  useEffect(() => {
    // 根据分类和搜索过滤知识
    if (!knowledgeBase.length) {
      setFilteredKnowledge([]);
      return;
    }

    let filtered = knowledgeBase;

    // 按分类过滤
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(
        (k: any) => k.category === selectedCategory
      );
    }

    // 按搜索词过滤
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim();
      filtered = filtered.filter(
        (k: any) =>
          k.title.toLowerCase().includes(query) ||
          k.content.toLowerCase().includes(query) ||
          k.tags?.some((tag: string) => tag.toLowerCase().includes(query)) ||
          k.category.toLowerCase().includes(query)
      );
    }

    setFilteredKnowledge(filtered);
  }, [knowledgeBase, selectedCategory, searchQuery]);

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const clearSearch = () => {
    setSearchQuery('');
  };

  const createKnowledgeItem = async () => {
    // TODO: 创建新知识条目
    alert('创建知识条目功能开发中...');
  };

  const exportKnowledge = async () => {
    // TODO: 导出知识库
    alert('导出知识库功能开发中...');
  };

  if (loading) {
    return (
      <div className="view-loading">
        <div className="loading-spinner">📖</div>
        <p>加载中...</p>
      </div>
    );
  }

  return (
    <div className="knowledge-view">
      <div className="knowledge-header">
        <h2>知识中心</h2>
        <div className="knowledge-search">
          <input
            type="text"
            value={searchQuery}
            onChange={handleSearchChange}
            placeholder="搜索知识..."
            className="search-input"
          />
          <button
            className="search-btn"
            onClick={handleSearchChange}
          >
            搜索
          </button>
          {searchQuery.trim() && (
            <button className="clear-btn" onClick={clearSearch}>
              清除
            </button>
          )}
        </div>
        <div className="knowledge-actions">
          <button className="add-knowledge-btn" onClick={createKnowledgeItem}>
            <span>+</span>
            <span>新建知识</span>
          </button>
          <button className="export-btn" onClick={exportKnowledge}>
            导出知识库
          </button>
        </div>
      </div>

      <div className="knowledge-stats">
        {knowledgeStats && (
          <div className="stats-grid">
            <div className="stat-card">
              <span className="stat-icon">📚</span>
              <span className="stat-value">{knowledgeStats.total_knowledge}</span>
              <span className="stat-label">知识条目</span>
            </div>
            <div className="stat-card">
              <span className="stat-icon">🏷️</span>
              <span className="stat-value">{knowledgeStats.total_categories}</span>
              <span className="stat-label">知识分类</span>
            </div>
            <div className="stat-card">
              <span className="stat-icon">🔗</span>
              <span className="stat-value">{knowledgeStats.total_connections}</span>
              <span className="stat-label">知识关联</span>
            </div>
            <div className="stat-card">
              <span className="stat-icon">📊</span>
              <span className="stat-value">{knowledgeStats.avg_rating}</span>
              <span className="stat-label">平均评分</span>
            </div>
          </div>
        )}
      </div>

      <div className="knowledge-categories">
        <h3>知识分类</h3>
        <div className="categories-list">
          {categories.map(category => (
            <button
              key={category}
              className={`category-btn ${selectedCategory === category ? 'active' : ''}`}
              onClick={() => handleCategoryChange(category)}
            >
              {category === 'all' ? '全部' : category}
              {category !== 'all' && (
                <span className="category-count">
                  ({knowledgeBase.filter((k: any) => k.category === category).length})
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="knowledge-items">
        <h3>
          {selectedCategory === 'all'
            ? '所有知识'
            : `${selectedCategory} (${filteredKnowledge.length} 项)`}
        </h3>
        {filteredKnowledge.length > 0 ? (
          <div className="items-grid">
            {filteredKnowledge.map((item, index) => (
              <div key={item.id} className="knowledge-item">
                <div className="item-header">
                  <h4>{item.title}</h4>
                  <span className="item-category-tag">
                    {item.category}
                  </span>
                </div>
                <div className="item-content">
                  <p>{item.summary || item.content.substring(0, 200)}...</p>
                  {item.tags?.length > 0 && (
                    <div className="item-tags">
                      {item.tags.map((tag: string, idx: number) => (
                        <span key={idx} className="tag">{tag}</span>
                      ))}
                    </div>
                  )}
                  <div className="item-meta">
                    <span>创建：{new Date(item.created_at).toLocaleDateString()}</span>
                    <span>评分：{item.rating || '未评分'}/5</span>
                  </div>
                </div>
                <div className="item-actions">
                  <button className="view-detail-btn">查看详情</button>
                  <button className="edit-btn">编辑</button>
                  <button className="share-btn">分享</button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>暂无匹配的知识条目</p>
            {searchQuery.trim() && (
              <p>尝试使用不同的关键词搜索</p>
            )}
            {!searchQuery.trim() && selectedCategory !== 'all' && (
              <p>该分类下暂无知识条目</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};