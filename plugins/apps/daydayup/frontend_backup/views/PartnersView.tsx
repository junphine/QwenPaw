/**
 * Partners View - AI 学习伙伴
 */

const { React, ReactDOM, antd } = window.QwenPaw.host;
const { useState, useEffect,useRef,useCallback } = React;

interface PartnersViewProps {
  api?: any;
}

export const PartnersView: React.FC<PartnersViewProps> = ({ api }) => {
  const [partners, setPartners] = useState<any[]>([]);
  const [selectedPartner, setSelectedPartner] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch('/plugins/daydayup/partners/list')
      .then(res => res.json())
      .then(data => {
        setPartners(data.partners || []);
        if (data.partners?.length > 0) {
          setSelectedPartner(data.partners[0]);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load partners:', err);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (selectedPartner) {
      fetch(`/plugins/daydayup/partners/${selectedPartner.id}/history?user_id=default`)
        .then(res => res.json())
        .then(data => {
          setMessages(data.history || []);
        })
        .catch(err => {
          console.error('Failed to load chat history:', err);
        });
    }
  }, [selectedPartner]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || !selectedPartner) return;

    const userMessage = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');

    try {
      const response = await fetch('/plugins/daydayup/partners/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          partner_id: selectedPartner.id,
          user_id: 'default',
          message: inputMessage
        })
      });

      const data = await response.json();
      
      const assistantMessage = {
        id: `msg_${Date.now() + 1}`,
        role: 'assistant',
        content: data.message,
        timestamp: data.timestamp,
        suggestions: data.suggestions
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };

  if (loading) {
    return (
      <div className="view-loading">
        <div className="loading-spinner">👥</div>
        <p>加载中...</p>
      </div>
    );
  }

  return (
    <div className="partners-view">
      <div className="partners-sidebar">
        <h2>学习伙伴</h2>
        <div className="partners-list">
          {partners.map(partner => (
            <button
              key={partner.id}
              className={`partner-item ${selectedPartner?.id === partner.id ? 'active' : ''}`}
              onClick={() => setSelectedPartner(partner)}
            >
              <span className="partner-avatar">{partner.avatar}</span>
              <div className="partner-info">
                <span className="partner-name">{partner.name}</span>
                <span className="partner-desc">{partner.description}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="chat-area">
        {selectedPartner ? (
          <>
            <div className="chat-header">
              <span className="partner-avatar">{selectedPartner.avatar}</span>
              <div className="chat-header-info">
                <span className="chat-partner-name">{selectedPartner.name}</span>
                <span className="chat-partner-personality">{selectedPartner.personality}</span>
              </div>
            </div>

            <div className="messages-container">
              {messages.map(msg => (
                <div key={msg.id} className={`message ${msg.role}`}>
                  <div className="message-content">{msg.content}</div>
                  {msg.suggestions && msg.suggestions.length > 0 && (
                    <div className="message-suggestions">
                      {msg.suggestions.map((suggestion: string, idx: number) => (
                        <button key={idx} className="suggestion-btn">
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-area">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="输入消息..."
                className="chat-input"
              />
              <button onClick={sendMessage} className="send-btn">
                发送
              </button>
            </div>
          </>
        ) : (
          <div className="no-partner-selected">
            <p>请选择一个学习伙伴开始聊天</p>
          </div>
        )}
      </div>
    </div>
  );
};
