/**
 * Learning View - 学习空间
 */

const { React, antd } = (window as any).QwenPaw.host;
const { useState, useEffect, useCallback } = React;
const { Layout, Menu, Card, Statistic, Row, Col, Button, Input, Spin, Tag, message } = antd;
const { Sider, Content, Header } = Layout;


// ==================== 学习空间页面 ====================
export const LearningView = ({ api }) => {
  // 占位实现，将在后续更新中完善
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100%',
        padding: '24px'
      }}
    >
      <div style={{ fontSize: '64px', marginBottom: '24px' }}>🎓</div>
      <h2 style={{ marginBottom: '12px' }}>学习空间</h2>
      <p style={{ color: '#666', maxWidth: '500px', textAlign: 'center' }}>
        系统化的课程学习，跟踪学习进度。
      </p>
    </div>
  );
}