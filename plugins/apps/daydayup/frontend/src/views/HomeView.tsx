/**
 * Home View - 主页学习空间
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

// ==================== 首页组件 ====================
export const HomeView = ({ api }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    apiRequest(api+'/home/dashboard?user_id=default')
      .then((data: any) => {
        setData(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Spin size="large" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }} />
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ marginBottom: '8px' }}>欢迎回到趣学习！</h1>
      <p style={{ color: '#666', marginBottom: '24px' }}>
        基于 Deep Tutor 架构的 AI 学习伴侣
      </p>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic title="最近课程" value={data?.recent_courses?.length || 0} prefix="📖" />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="记忆条目" value={data?.recent_memories?.length || 0} prefix="🧠" />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="学习伙伴" value={data?.active_partners?.length || 0} prefix="👥" />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="知识条目" value={data?.total_memories || 0} prefix="📚" />
          </Card>
        </Col>
      </Row>

      {/* Deep Tutor Capabilities 介绍 */}
      <Card title="Deep Tutor Capabilities" style={{ marginBottom: '24px' }}>
        <Row gutter={16}>
          <Col span={8}>
            <div style={{ textAlign: 'center', padding: '16px' }}>
              <div style={{ fontSize: '32px' }}>🎯</div>
              <div style={{ fontWeight: 'bold', marginTop: '8px' }}>深度解题</div>
              <div style={{ color: '#666', fontSize: '12px' }}>Deep Solve</div>
            </div>
          </Col>
          <Col span={8}>
            <div style={{ textAlign: 'center', padding: '16px' }}>
              <div style={{ fontSize: '32px' }}>❓</div>
              <div style={{ fontWeight: 'bold', marginTop: '8px' }}>深度提问</div>
              <div style={{ color: '#666', fontSize: '12px' }}>Deep Question</div>
            </div>
          </Col>
          <Col span={8}>
            <div style={{ textAlign: 'center', padding: '16px' }}>
              <div style={{ fontSize: '32px' }}>🔬</div>
              <div style={{ fontWeight: 'bold', marginTop: '8px' }}>深度研究</div>
              <div style={{ color: '#666', fontSize: '12px' }}>Deep Research</div>
            </div>
          </Col>
        </Row>
      </Card>

      {/* 快速开始 */}
      <Card title="快速开始">
        <Row gutter={16}>
          <Col span={6}>
            <Button type="primary" block size="large" onClick={() => window.location.hash = '#/daydayup/partners'}>
              👥 和学习伙伴聊天
            </Button>
          </Col>
          <Col span={6}>
            <Button block size="large" onClick={() => window.location.hash = '#/daydayup/agents'}>
              🤖 创建智能体
            </Button>
          </Col>
          <Col span={6}>
            <Button block size="large" onClick={() => window.location.hash = '#/daydayup/memory'}>
              🧠 查看记忆
            </Button>
          </Col>
          <Col span={6}>
            <Button block size="large" onClick={() => window.location.hash = '#/daydayup/learning'}>
              🎓 继续学习
            </Button>
          </Col>
        </Row>
      </Card>
    </div>
  );
}