/**
 * Co-Writer View - 协同写作
 */
const { React, antd } = (window as any).QwenPaw.host;
const { useState, useEffect, useCallback } = React;
const { Layout, Menu, Card, Statistic, Row, Col, Button, Input, Spin, Tag, message } = antd;
const { Sider, Content, Header } = Layout;


// ==================== 协同写作页面 ====================
export const CoWriterView = ({ api }) => {
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
      <div style={{ fontSize: '64px', marginBottom: '24px' }}>✍️</div>
      <h2 style={{ marginBottom: '12px' }}>协同写作</h2>
      <p style={{ color: '#666', maxWidth: '500px', textAlign: 'center' }}>
        与 AI 一起写作，获得实时反馈和改进建议。基于 Deep Tutor Co-Writer。
      </p>
    </div>
  );
}