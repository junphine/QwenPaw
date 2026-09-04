/**
 * Agents View - 我的智能体
 */

const { React, antd } = (window as any).QwenPaw.host;
const { useState, useEffect, useCallback } = React;
const { Layout, Menu, Card, Statistic, Row, Col, Button, Input, Spin, Tag, message } = antd;
const { Sider, Content, Header } = Layout;



// 通用 API 请求函数
async function apiRequest(endpoint: string, options: any = {}) {
  const url = `${endpoint}`;
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

// ==================== 智能体页面 ====================
export const AgentsView = ({api}) => {
  const [agents, setAgents] = useState<any[]>([]);
  const [capabilities, setCapabilities] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    Promise.all([
      apiRequest(api+'/agents/list'),
      apiRequest(api+'/agents/capabilities')
    ]).then(([agentsData, capsData]: any[]) => {
      setAgents(agentsData.agents || []);
      setCapabilities(capsData.capabilities || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return (
      <Spin size="large" />
    );

  return (
    <div style={{ padding: '24px' }}>
      <h2>我的智能体</h2>
      <p style={{ color: '#666' }}>
        基于 Deep Tutor Agent 系统的自定义智能体
      </p>

      {/* Capabilities 展示 */}
      <Card title="Deep Tutor Capabilities" style={{ marginTop: '24px', marginBottom: '24px' }}>
        <Row gutter={16}>
          {capabilities.map((cap: any) => (
            <Col span={8} key={cap.id} style={{ marginBottom: '16px' }}>
              <Card size="small">
                <div style={{ fontWeight: 'bold' }}>{cap.name}</div>
                <div style={{ color: '#666', fontSize: '12px' }}>{cap.description}</div>
                <div style={{ marginTop: '8px' }}>
                  {cap.tools.map((tool: string) => (
                    <Tag key={tool} size="small">{tool}</Tag>
                  ))}
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>

      {/* 智能体列表 */}
      <Row gutter={16}>
        {agents.map((agent: any) => (
          <Col span={8} key={agent.id} style={{ marginBottom: '16px' }}>
            <Card
              title={
                <div>
                  <span style={{ fontSize: '24px', marginRight: '8px' }}>{agent.avatar}</span>
                  {agent.name}
                </div>
              }
              extra={<Button type="primary" size="small">聊天</Button>}
            >
              <div style={{ color: '#666' }}>{agent.description}</div>
              <div style={{ marginTop: '8px' }}>
                <Tag color="blue">{agent.capability}</Tag>
              </div>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
}