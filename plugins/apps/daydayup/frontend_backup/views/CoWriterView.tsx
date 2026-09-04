/**
 * Co-Writer View - 协同写作
 */

const { React, ReactDOM, antd } = window.QwenPaw.host;
const { useState, useEffect, useCallback } = React;

interface CoWriterViewProps {
  api?: any;
}

export const CoWriterView: React.FC<CoWriterViewProps> = ({ api }) => {
  const [documents, setDocuments] = useState<any[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<any>(null);
  const [editorContent, setEditorContent] = useState('');
  const [aiSuggestions, setAiSuggestions] = useState<string[]>([]);
  const [isAiThinking, setIsAiThinking] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 加载文档列表
    fetch('/plugins/daydayup/cowriter/documents?user_id=default')
      .then(res => res.json())
      .then(data => {
        setDocuments(data.documents || []);
        if (data.documents?.length > 0) {
          setSelectedDocument(data.documents[0]);
          setEditorContent(data.documents[0].content || '');
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load documents:', err);
        setLoading(false);
      });
  }, []);

  const handleDocumentSelect = (doc: any) => {
    setSelectedDocument(doc);
    setEditorContent(doc.content || '');
    setAiSuggestions([]);
  };

  const createNewDocument = async () => {
    try {
      const response = await fetch('/plugins/daydayup/cowriter/document', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'default',
          title: '新建文档',
          content: ''
        })
      });

      const data = await response.json();
      const newDoc = {
        id: data.id,
        title: '新建文档',
        content: '',
        created_at: data.created_at,
        updated_at: data.updated_at
      };

      setDocuments([newDoc, ...documents]);
      setSelectedDocument(newDoc);
      setEditorContent('');
      setAiSuggestions([]);
    } catch (err) {
      console.error('Failed to create document:', err);
    }
  };

  const saveDocument = async () => {
    if (!selectedDocument) return;

    try {
      const response = await fetch(`/plugins/daydayup/cowriter/document/${selectedDocument.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: editorContent
        })
      });

      const data = await response.json();
      // 更新文档列表中的内容
      setDocuments(prev =>
        documents.map(doc =>
          doc.id === selectedDocument.id
            ? { ...doc, content: editorContent, updated_at: data.updated_at }
            : doc
        )
      );
      setSelectedDocument(prev =>
        prev ? { ...prev, content: editorContent, updated_at: data.updated_at } : prev
      );
      alert('文档保存成功');
    } catch (err) {
      console.error('Failed to save document:', err);
      alert('文档保存失败');
    }
  };

  const getAiSuggestion = async () => {
    if (!editorContent.trim() || !selectedDocument) return;

    setIsAiThinking(true);
    try {
      const response = await fetch('/plugins/daydayup/cowriter/ai-suggest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_id: selectedDocument.id,
          user_id: 'default',
          content: editorContent,
          context: 'continue' // 或者可以是 'improve', 'summarize' 等
        })
      });

      const data = await response.json();
      setAiSuggestions(data.suggestions || []);
    } catch (err) {
      console.error('Failed to get AI suggestion:', err);
    } finally {
      setIsAiThinking(false);
    }
  };

  const applySuggestion = (suggestion: string) => {
    setEditorContent(prev => prev + ' ' + suggestion);
    setAiSuggestions([]);
  };

  if (loading) {
    return (
      <div className="view-loading">
        <div className="loading-spinner">✍️</div>
        <p>加载中...</p>
      </div>
    );
  }

  return (
    <div className="cowriter-view">
      <div className="cowriter-sidebar">
        <h2>我的文档</h2>
        <button className="new-doc-btn" onClick={createNewDocument}>
          <span>+</span>
          <span>新建文档</span>
        </button>
        <div className="documents-list">
          {documents.map(doc => (
            <div
              key={doc.id}
              className={`doc-item ${selectedDocument?.id === doc.id ? 'active' : ''}`}
              onClick={() => handleDocumentSelect(doc)}
            >
              <span className="doc-icon">📄</span>
              <div className="doc-info">
                <h4>{doc.title}</h4>
                <span className="doc-updated">
                  {new Date(doc.updated_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="cowriter-main">
        {selectedDocument ? (
          <>
            <div className="document-header">
              <h3>{selectedDocument.title}</h3>
              <div className="doc-actions">
                <button className="save-btn" onClick={saveDocument}>
                  保存
                </button>
                <button className="ai-suggest-btn" onClick={getAiSuggestion}
                  disabled={isAiThinking || !editorContent.trim()}
                >
                  {isAiThinking ? 'AI思考中...' : 'AI建议'}
                </button>
              </div>
            </div>

            <div className="editor-container">
              <textarea
                value={editorContent}
                onChange={(e) => setEditorContent(e.target.value)}
                placeholder="开始写作..."
                className="editor-textarea"
                rows={20}
              />
            </div>

            {aiSuggestions.length > 0 && !isAiThinking && (
              <div className="ai-suggestions">
                <h4>AI 建议</h4>
                <div className="suggestions-list">
                  {aiSuggestions.map((suggestion, index) => (
                    <div
                      key={index}
                      className="suggestion-item"
                      onClick={() => applySuggestion(suggestion)}
                    >
                      {suggestion}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="no-document-selected">
            <p>请选择或创建一个文档开始写作</p>
            <button className="new-doc-btn" onClick={createNewDocument}>
              <span>+</span>
              <span>新建文档</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};