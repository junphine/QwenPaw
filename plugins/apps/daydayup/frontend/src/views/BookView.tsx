/**
 * Book View - 交互式书本
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

// ==================== 交互式书本页面 ====================
export const BookView = ({ api }) => {
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
      <div style={{ fontSize: '64px', marginBottom: '24px' }}>📚</div>
      <h2 style={{ marginBottom: '12px' }}>交互式书本</h2>
      <p style={{ color: '#666', maxWidth: '500px', textAlign: 'center' }}>
        阅读交互式学习材料，边学边练。基于 Deep Tutor BookEngine。
      </p>
    </div>
  );
}