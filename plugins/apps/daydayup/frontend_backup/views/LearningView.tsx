/**
 * Learning View - 学习空间
 */
const { React, ReactDOM, antd } = window.QwenPaw.host;
const { useState, useEffect, useCallback } = React;

interface LearningViewProps {
  api?: any;
}

export const LearningView: React.FC<LearningViewProps> = ({ api }) => {
  const [courses, setCourses] = useState<any[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<any>(null);
  const [courseLessons, setCourseLessons] = useState<any[]>([]);
  const [currentLesson, setCurrentLesson] = useState<any>(null);
  const [lessonProgress, setLessonProgress] = useState(0);
  const [learningStats, setLearningStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 加载课程列表
    fetch('/plugins/daydayup/learning/courses?user_id=default')
      .then(res => res.json())
      .then(data => {
        setCourses(data.courses || []);
        if (data.courses?.length > 0) {
          setSelectedCourse(data.courses[0]);
          loadCourseLessons(data.courses[0].id);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load courses:', err);
        setLoading(false);
      });

    // 加载学习统计
    fetch('/plugins/daydayup/learning/stats?user_id=default')
      .then(res => res.json())
      .then(data => {
        setLearningStats(data);
      })
      .catch(err => {
        console.error('Failed to load learning stats:', err);
      });
  }, []);

  const loadCourseLessons = (courseId: string) => {
    fetch(`/plugins/daydayup/learning/course/${courseId}/lessons?user_id=default`)
      .then(res => res.json())
      .then(data => {
        setCourseLessons(data.lessons || []);
        if (data.lessons?.length > 0) {
          setCurrentLesson(data.lessons[0]);
          loadLessonProgress(data.lessons[0].id);
        }
      })
      .catch(err => {
        console.error('Failed to load course lessons:', err);
      });
  };

  const loadLessonProgress = (lessonId: string) => {
    fetch(`/plugins/daydayup/learning/lesson/${lessonId}/progress?user_id=default`)
      .then(res => res.json())
      .then(data => {
        setLessonProgress(data.progress || 0);
      })
      .catch(err => {
        console.error('Failed to load lesson progress:', err);
      });
  };

  const handleCourseSelect = (course: any) => {
    setSelectedCourse(course);
    loadCourseLessons(course.id);
  };

  const handleLessonSelect = (lesson: any) => {
    setCurrentLesson(lesson);
    loadLessonProgress(lesson.id);
  };

  const updateLessonProgress = async (progress: number) => {
    if (!currentLesson) return;

    try {
      await fetch(`/plugins/daydayup/learning/lesson/${currentLesson.id}/progress`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'default',
          progress: progress
        })
      });
      setLessonProgress(progress);
    } catch (err) {
      console.error('Failed to update lesson progress:', err);
    }
  };

  const completeLesson = async () => {
    if (!currentLesson) return;

    try {
      await fetch(`/plugins/daydayup/learning/lesson/${currentLesson.id}/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'default'
        })
      });

      // 加载下一课
      const currentIndex = courseLessons.findIndex(
        (lesson: any) => lesson.id === currentLesson.id
      );
      if (currentIndex < courseLessons.length - 1) {
        setCurrentLesson(courseLessons[currentIndex + 1]);
        loadLessonProgress(courseLessons[currentIndex + 1].id);
      }
    } catch (err) {
      console.error('Failed to complete lesson:', err);
    }
  };

  if (loading) {
    return (
      <div className="view-loading">
        <div className="loading-spinner">🎓</div>
        <p>加载中...</p>
      </div>
    );
  }

  return (
    <div className="learning-view">
      <div className="learning-sidebar">
        <h2>我的课程</h2>
        <div className="courses-list">
          {courses.map(course => (
            <div
              key={course.id}
              className={`course-item ${selectedCourse?.id === course.id ? 'active' : ''}`}
              onClick={() => handleCourseSelect(course)}
            >
              <span className="course-icon">📘</span>
              <div className="course-info">
                <h4>{course.title}</h4>
                <span className="course-instructor">{course.instructor}</span>
                <div className="course-progress">
                  <div
                    className="progress-bar"
                    style={{ width: `${course.progress || 0}%` }}
                  />
                  <span className="progress-text">{course.progress || 0}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 添加新课程按钮 */}
        <button className="add-course-btn" onClick={() => alert('添加新课程功能开发中...')}>
          <span>+</span>
          <span>添加课程</span>
        </button>
      </div>

      <div className="learning-main">
        {selectedCourse ? (
          <>
            <div className="course-header">
              <h3>{selectedCourse.title}</h3>
              <p className="course-subtitle">{selectedCourse.description}</p>
              <div className="course-meta">
                <span>讲师：{selectedCourse.instructor}</span>
                <span>难度：{selectedCourse.difficulty}</span>
                <span>时长：{selectedCourse.duration}</span>
              </div>
            </div>

            <div className="course-tabs">
              <button className="tab-btn active" onClick={() => {}}
                >课程 ({selectedCourse.lesson_count || 0} 节)</button>
              <button className="tab-btn" onClick={() => {}}
                >作业</button>
              <button className="tab-btn" onClick={() => {}}
                >讨论</button>
              <button className="tab-btn" onClick={() => {}}
                >笔记</button>
            </div>

            {courseLessons.length > 0 ? (
              <>
                <div className="lessons-list">
                  {courseLessons.map(lesson => (
                    <div
                      key={lesson.id}
                      className={`lesson-item ${currentLesson?.id === lesson.id ? 'active' : ''}`}
                      onClick={() => handleLessonSelect(lesson)}
                    >
                      <span className="lesson-icon">📝</span>
                      <div className="lesson-info">
                        <h4>{lesson.title}</h4>
                        <span className="lesson-type">{lesson.type}</span>
                        <div className="lesson-progress">
                          <div className="progress-bar"
                            style={{
                              width: `${
                                lesson.id === currentLesson.id
                                  ? lessonProgress
                                  : lesson.progress || 0
                              }%`}}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {currentLesson && (
                  <>
                    <div className="lesson-header">
                      <h4>{currentLesson.title}</h4>
                      <p className="lesson-desc">{currentLesson.description}</p>
                    </div>

                    <div className="lesson-content">
                      {currentLesson.content_type === 'video' && (
                        <div className="video-container">
                          {/* 视频播放器占位 */}
                          <div className="video-placeholder">
                            <span>▶️</span>
                            <span>视频课程内容</span>
                          </div>
                        </div>
                      )}
                      {currentLesson.content_type === 'text' && (
                        <div className="text-content">
                          <p>{currentLesson.content}</p>
                        </div>
                      )}
                      {currentLesson.content_type === 'quiz' && (
                        <div className="quiz-container">
                          <h5>小测验</h5>
                          {/* 测验内容占位 */}
                          <div className="quiz-placeholder">
                            <p>测验题目将在这里显示</p>
                            <button className="start-quiz-btn">开始测验</button>
                          </div>
                        </div>
                      )}
                    </div>

                    <div className="lesson-actions">
                      <div className="progress-container">
                        <div className="progress-bar">
                          <div
                            className="progress-fill"
                            style={{ width: `${lessonProgress}%` }}
                          />
                        </div>
                        <div className="progress-info">
                          <span>{lessonProgress}%</span>
                          <span>/ 100%</span>
                        </div>
                      </div>
                      <div className="progress-slider">
                        <input
                          type="range"
                          min="0"
                          max="100"
                          value={lessonProgress}
                          onChange={(e) => updateLessonProgress(parseInt(e.target.value))}
                        />
                      </div>
                      <button
                        className="complete-lesson-btn"
                        onClick={completeLesson}
                        disabled={lessonProgress >= 100}
                      >
                        {lessonProgress >= 100 ? '已完成' : '标记完成'}
                      </button>
                    </div>
                  </>
                )}
              </>
            ) : (
              <div className="no-lessons">
                <p>该课程暂无课程内容</p>
              </div>
            )}
          </>
        ) : (
          <div className="no-course-selected">
            <p>请选择一门课程开始学习</p>
          </div>
        )}
      </div>
    </div>
  );
};