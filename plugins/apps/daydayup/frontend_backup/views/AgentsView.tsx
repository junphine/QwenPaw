/**
 * Agents View - 我的智能体
 */

const { React, ReactDOM, antd } = window.QwenPaw.host;
const { useState, useEffect, useCallback } = React;


interface AgentsViewProps {
  api?: any;
}

export const AgentsView: React.FC<AgentsViewProps> = ({ api }) => {
  const [agents, setAgents] = useState<any[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<any>(null);
  const [agentCapabilities, setAgentCapabilities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 加载智能体列表
    fetch('/plugins/daydayup/agents/list?user_id=default')
      .then(res => res.json())
      .then(data => {
        setAgents(data.agents || []);
        if (data.agents?.length > 0) {
          setSelectedAgent(data.agents[0]);
          loadAgentCapabilities(data.agents[0].id);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load agents:', err);
        setLoading(false);
      });
  }, []);

  const loadAgentCapabilities = (agentId: string) => {
    fetch(`/plugins/daydayup/agents/${agentId}/capabilities?user_id=default`)
      .then(res => res.json())
      .then(data => {
        setAgentCapabilities(data.capabilities || []);
      })
      .catch(err => {
        console.error('Failed to load agent capabilities:', err);
      });
  };

  const handleAgentSelect = (agent: any) => {
    setSelectedAgent(agent);
    loadAgentCapabilities(agent.id);
  };

  const runAgent = async (capabilityId: string) => {
    if (!selectedAgent) return;

    try {
      const response = await fetch('/plugins/daydayup/agents/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: selectedAgent.id,
          user_id: 'default',
          capability_id: capabilityId
        })
      });

      const data = await response.json();
      console.log('Agent execution result:', data);
      // TODO: 显示执行结果
    } catch (err) {
      console.error('Failed to run agent:', err);
    }
  };

  if (loading) {
    return (
      <div className="view-loading">
        <div className="loading-spinner">🤖</div>
        <p>加载中...</p>
      </div>
    );
  }

  return (
    <div className="agents-view">
      <div className="agents-sidebar">
        <h2>我的智能体</h2>
        <div className="agents-list">
          {agents.map(agent => (
            <button
              key={agent.id}
              className={`agent-item ${selectedAgent?.id === agent.id ? 'active' : ''}`}
              onClick={() => handleAgentSelect(agent)}
            >
              <span className="agent-icon">{agent.icon}</span>
              <div className="agent-info">
                <span className="agent-name">{agent.name}</span>
                <span className="agent-type">{agent.type}</span>
              </div>
            </button>
          ))}
        </div>

        {/* 创建新智能体按钮 */}
        <button className="create-agent-btn" onClick={() => alert('创建新智能体功能开发中...')}>
          <span>+</span>
          <span>创建智能体</span>
        </button>
      </div>

      <div className="agents-main">
        {selectedAgent ? (
          <>
            <div className="agent-header">
              <div className="agent-avatar">{selectedAgent.icon}</div>
              <div className="agent-header-info">
                <h3>{selectedAgent.name}</h3>
                <p className="agent-desc">{selectedAgent.description}</p>
              </div>
            </div>

            <div className="agent-tabs">
              <button className="tab-btn active" onClick={() => {}}
                >能力 ({agentCapabilities.length})</button>
              <button className="tab-btn" onClick={() => {}}
                >配置</button>
              <button className="tab-btn" onClick={() => {}}
                >使用历史</button>
            </div>

            <div className="agent-capabilities">
              {agentCapabilities.length > 0 ? (
                <div className="capabilities-grid">
                  {agentCapabilities.map(capability => (
                    <div key={capability.id} className="capability-card">
                      <div className="capability-icon">{capability.icon}</div>
                      <h4>{capability.name}</h4>
                      <p className="capability-desc">{capability.description}</p>
                      <div className="capability-tags">
                        {capability.tags?.map((tag: string) => (
                          <span key={tag} className="tag">{tag}</span>
                        ))}
                      </div>
                      <button
                        className="run-capability-btn"
                        onClick={() => runAgent(capability.id)}
                      >
                        运行
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="no-capabilities">
                  <p>该智能体暂无可用能力</p>
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="no-agent-selected">
            <p>请选择一个智能体查看详情</p>
          </div>
        )}
      </div>
    </div>
  );
};