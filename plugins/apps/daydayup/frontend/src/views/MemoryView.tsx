/**
 * Memory View - 三层记忆系统
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

// ==================== 记忆系统页面 ====================
export const MemoryView = ({ api }) => {
  const [stats, setStats] = useState<any>(null);
  const [activeLayer, setActiveLayer] = useState<string>('L1');

  useEffect(() => {
    apiRequest(api+'/memory/stats?user_id=default')
      .then((data: any) => setStats(data))
      .catch(() => {});
  }, []);

  return (
    <div style={{ padding: '24px' }}>
      <h2>记忆系统</h2>
      <p style={{ color: '#666' }}>
        基于 Deep Tutor 三层记忆系统：L1 Trace → L2 Document → L3 Consolidated
      </p>

      {/* 三层记忆说明 */}
      <Row gutter={16} style={{ marginTop: '24px', marginBottom: '24px' }}>
        <Col span={8}>
          <Card
            title="L1 - Trace"
            style={{ borderTop: '3px solid #1890ff' }}
          >
            <div>原始事件捕获</div>
            <div style={{ color: '#666', fontSize: '12px', marginTop: '8px' }}>
              Append-only JSONL，按日期存储
            </div>
            {stats && (
              <Statistic title="事件数" value={stats.l1_traces} style={{ marginTop: '16px' }} />
            )}
          </Card>
        </Col>
        <Col span={8}>
          <Card
            title="L2 - Document"
            style={{ borderTop: '3px solid #52c41a' }}
          >
            <div>Markdown 文档</div>
            <div style={{ color: '#666', fontSize: '12px', marginTop: '8px' }}>
              带 footnote-citation 的文档
            </div>
            {stats && (
              <Statistic title="文档数" value={stats.l2_documents} style={{ marginTop: '16px' }} />
            )}
          </Card>
        </Col>
        <Col span={8}>
          <Card
            title="L3 - Consolidated"
            style={{ borderTop: '3px solid #faad14' }}
          >
            <div>整合记忆</div>
            <div style={{ color: '#666', fontSize: '12px', marginTop: '8px' }}>
              LLM 驱动的 L1/L2 → L3 整合
            </div>
            {stats && (
              <Statistic title="Slot 数" value={stats.l3_slots} style={{ marginTop: '16px' }} />
            )}
          </Card>
        </Col>
      </Row>

      {/* Surfaces */}
      {stats && (
        <Card title="Surfaces (记忆来源)">
          <Row gutter={16}>
            {(stats.surfaces || []).map((surface: string) => (
              <Col span={4} key={surface}>
                <Tag style={{ width: '100%', textAlign: 'center' }}>{surface}</Tag>
              </Col>
            ))}
          </Row>
        </Card>
      )}
    </div>
  );
}