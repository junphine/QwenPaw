/**
 * Book View - 交互式书本
 */

const { React, ReactDOM, antd } = window.QwenPaw.host;
const { useState, useEffect, useCallback } = React;


interface BookViewProps {
  api?: any;
}

export const BookView: React.FC<BookViewProps> = ({ api }) => {
  const [books, setBooks] = useState<any[]>([]);
  const [selectedBook, setSelectedBook] = useState<any>(null);
  const [currentChapter, setCurrentChapter] = useState<any>(null);
  const [chapterContent, setChapterContent] = useState('');
  const [readingProgress, setReadingProgress] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 加载书籍列表
    fetch('/plugins/daydayup/books/list?user_id=default')
      .then(res => res.json())
      .then(data => {
        setBooks(data.books || []);
        if (data.books?.length > 0) {
          setSelectedBook(data.books[0]);
          loadBookChapters(data.books[0].id);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load books:', err);
        setLoading(false);
      });
  }, []);

  const loadBookChapters = (bookId: string) => {
    fetch(`/plugins/daydayup/books/${bookId}/chapters?user_id=default`)
      .then(res => res.json())
      .then(data => {
        const chapters = data.chapters || [];
        if (chapters.length > 0) {
          setCurrentChapter(chapters[0]);
          loadChapterContent(chapters[0].id);
        }
      })
      .catch(err => {
        console.error('Failed to load book chapters:', err);
      });
  };

  const loadChapterContent = (chapterId: string) => {
    fetch(`/plugins/daydayup/books/chapter/${chapterId}/content?user_id=default`)
      .then(res => res.json())
      .then(data => {
        setChapterContent(data.content || '');
        setReadingProgress(data.progress || 0);
      })
      .catch(err => {
        console.error('Failed to load chapter content:', err);
      });
  };

  const handleBookSelect = (book: any) => {
    setSelectedBook(book);
    loadBookChapters(book.id);
  };

  const handleChapterSelect = (chapter: any) => {
    setCurrentChapter(chapter);
    loadChapterContent(chapter.id);
  };

  const updateReadingProgress = async (progress: number) => {
    if (!currentChapter) return;

    try {
      await fetch(`/plugins/daydayup/books/chapter/${currentChapter.id}/progress`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'default',
          progress: progress
        })
      });
      setReadingProgress(progress);
    } catch (err) {
      console.error('Failed to update reading progress:', err);
    }
  };

  if (loading) {
    return (
      <div className="view-loading">
        <div className="loading-spinner">📚</div>
        <p>加载中...</p>
      </div>
    );
  }

  return (
    <div className="book-view">
      <div className="book-sidebar">
        <h2>我的书库</h2>
        <div className="books-list">
          {books.map(book => (
            <div
              key={book.id}
              className={`book-item ${selectedBook?.id === book.id ? 'active' : ''}`}
              onClick={() => handleBookSelect(book)}
            >
              <span className="book-icon">📖</span>
              <div className="book-info">
                <h4>{book.title}</h4>
                <span className="book-author">{book.author}</span>
                <div className="book-progress">
                  <div
                    className="progress-bar"
                    style={{ width: `${book.progress || 0}%` }}
                  />
                  <span className="progress-text">{book.progress || 0}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 添加新书籍按钮 */}
        <button className="add-book-btn" onClick={() => alert('添加新书籍功能开发中...')}>
          <span>+</span>
          <span>添加书籍</span>
        </button>
      </div>

      <div className="book-main">
        {selectedBook ? (
          <>
            <div className="book-header">
              <h3>{selectedBook.title}</h3>
              <p className="book-subtitle">{selectedBook.subtitle || ''}</p>
              <div className="book-meta">
                <span>作者：{selectedBook.author}</span>
                <span>分类：{selectedBook.category}</span>
                <span>更新：{new Date(selectedBook.updated_at).toLocaleDateString()}</span>
              </div>
            </div>

            <div className="book-tabs">
              <button className="tab-btn active" onClick={() => {}}
                >章节 ({selectedBook.chapter_count || 0})</button>
              <button className="tab-btn" onClick={() => {}}
                >书签</button>
              <button className="tab-btn" onClick={() => {}}
                >笔记</button>
            </div>

            {currentChapter ? (
              <>
                <div className="chapter-header">
                  <h4>{currentChapter.title}</h4>
                  <div className="chapter-meta">
                    <span>第 {currentChapter.index} 章</span>
                    <span>• {readingProgress}% 已读</span>
                  </div>
                </div>

                <div className="chapter-content">
                  <div className="content-text">
                    {chapterContent}
                  </div>
                </div>

                <div className="reading-controls">
                  <div className="progress-container">
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{ width: `${readingProgress}%` }}
                      />
                    </div>
                    <div className="progress-info">
                      <span>{readingProgress}%</span>
                      <span>/ 100%</span>
                    </div>
                  </div>
                  <div className="progress-slider">
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={readingProgress}
                      onChange={(e) => updateReadingProgress(parseInt(e.target.value))}
                    />
                  </div>
                </div>

                <div className="chapter-navigation">
                  <button
                    className="nav-btn"
                    onClick={() => {
                      // TODO: 上一章
                    }}
                    disabled={!currentChapter || currentChapter.index <= 1}
                  >
                    上一章
                  </button>
                  <span className="chapter-info">
                    {currentChapter.index}/{selectedBook.chapter_count || 0}
                  </span>
                  <button
                    className="nav-btn"
                    onClick={() => {
                      // TODO: 下一章
                    }}
                    disabled={
                      !currentChapter ||
                      currentChapter.index >= (selectedBook.chapter_count || 0)
                    }
                  >
                    下一章
                  </button>
                </div>
              </>
            ) : (
              <div className="no-chapter-selected">
                <p>请选择章节开始阅读</p>
              </div>
            )}
          </>
        ) : (
          <div className="no-book-selected">
            <p>请选择一本书开始阅读</p>
          </div>
        )}
      </div>
    </div>
  );
};