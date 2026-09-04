/**
 * Partners View - 学习伙伴
 */

const { React, antd } = (window as any).QwenPaw.host;
const { useState, useEffect } = React;
const { Card, Row, Col, Button, Input, Spin, message } = antd;


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

// ==================== 学习伙伴页面 ====================
export const PartnersView = ({ api }) => {
  const [partners, setPartners] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedPartner, setSelectedPartner] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [inputMessage, setInputMessage] = useState<string>('');

  useEffect(() => {
    // 加载伙伴列表
    apiRequest(api+'/partners/list')
      .then((data: any) => {
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

  if (loading) return (
      <Spin size="large" />
    );

  return (
    <div style={{ padding: '24px' }}>
      <h2>学习伙伴</h2>
      <p style={{ color: '#666' }}>
        基于 Deep Tutor Partner 系统的 AI 学习伙伴
      </p>

      <div style={{ display: 'flex', marginTop: '24px' }}>
        {/* 伙伴列表 */}
        <div style={{ flex: '0 0 150px', marginRight: '24px' }}>
          <Card title="选择伙伴">
            {partners.map((partner: any) => (
              <div
                key={partner.id}
                onClick={() => setSelectedPartner(partner)}
                style={{
                  padding: '12px',
                  marginBottom: '8px',
                  cursor: 'pointer',
                  borderRadius: '4px',
                  backgroundColor: selectedPartner?.id === partner.id ? '#e6f7ff' : 'white',
                  border: '1px solid #f0f0f0'
                }}
              >
                <div style={{ fontSize: '20px' }}>{partner.avatar}</div>
                <div>{partner.name}</div>
                <div style={{ fontSize: '12px', color: '#666' }}>{partner.personality}</div>
              </div>
            ))}
          </Card>
        </div>

        {/* 聊天区域 */}
        <div style={{ flex: 1 }}>
          {selectedPartner ? (
            <div>
              <Card title={`${selectedPartner.name} - ${selectedPartner.description}`} style={{ marginBottom: '16px' }}>
                {/* 消息列表 */}
                <div style={{ height: '300px', overflowY: 'auto', marginBottom: '16px', border: '1px solid #f0f0f0', borderRadius: '4px', padding: '12px' }}>
                  {messages.length === 0 ? (
                    <div style={{ textAlign: 'center', color: '#999', padding: '20px' }}>
                      开始和伙伴聊天吧！
                    </div>
                  ) : (
                    messages.map((msg: any, idx: number) => (
                      <div
                        key={idx}
                        style={{
                          marginBottom: '8px',
                          textAlign: msg.role === 'user' ? 'right' : 'left'
                        }}
                      >
                        <div
                          style={{
                            display: 'inline-block',
                            padding: '8px 12px',
                            borderRadius: '12px',
                            background: msg.role === 'user' ? '#1890ff' : '#f0f0f0',
                            color: msg.role === 'user' ? '#fff' : '#333',
                            maxWidth: '70%'
                          }}
                        >
                          {msg.content}
                        </div>
                      </div>
                    ))
                  )}
                </div>
                {/* 输入区域 */}
                <div style={{ display: 'flex', gap: '8px' }}>
                  <Input
                    value={inputMessage}
                    onChange={(e: any) => setInputMessage(e.target.value)}
                    placeholder="输入消息..."
                    onPressEnter={(e: any) => {
                      if (!e.shiftKey) {
                        e.preventDefault();
                        sendMessage();
                      }
                    }}
                  />
                  <Button type="primary" onClick={sendMessage}>
                    发送
                  </Button>
                </div>
              </Card>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
              <div style={{ fontSize: '48px' }}>👥</div>
              <div style={{ marginTop: '16px' }}>选择一个学习伙伴开始聊天</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}