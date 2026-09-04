/**
 * 双虾汇 v2.4.3 - AI辩论平台前端
 * 新增：全量智能体列表、3-50轮支持、历史记录修复、界面精简
 */
(function () {
  'use strict';

  if (!window.QwenPaw) {
    console.error("[双虾汇] QwenPaw not ready");
    return;
  }

  var QP = window.QwenPaw;
  var React = QP.host.React;
  var h = React.createElement;
  var useState = React.useState;
  var useEffect = React.useEffect;

  var PLUGIN_ID = "qwenpaw-doubao";
  var PLUGIN_NAME = "双虾汇";
  var API_BASE = "/api/plugins/qwenpaw-doubao";
  var STORAGE_KEY = "shuangxia_history_";
  var ACTIVE_SESSION_KEY = "shuangxia_active_session";

  // XSS防护
  function escapeHtml(text) {
    if (!text) return "";
    var map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
  }

  // 格式化时间
  function formatTime(isoString) {
    if (!isoString) return "";
    try {
      var d = new Date(isoString);
      return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    } catch (e) {
      return isoString;
    }
  }

  // 格式化完整时间
  function formatFullTime(isoString) {
    if (!isoString) return "";
    try {
      var d = new Date(isoString);
      return d.toLocaleString('zh-CN');
    } catch (e) {
      return isoString;
    }
  }

  // 主应用组件
  function ShuangXiaHuiApp() {
    // 状态管理
    var _agents = useState([]);
    var agents = _agents[0], setAgents = _agents[1];
    var _proAgent = useState(null);
    var proAgent = _proAgent[0], setProAgent = _proAgent[1];
    var _conAgent = useState(null);
    var conAgent = _conAgent[0], setConAgent = _conAgent[1];
    var _topics = useState([]);
    var topics = _topics[0], setTopics = _topics[1];
    var _selectedTopic = useState("");
    var selectedTopic = _selectedTopic[0], setSelectedTopic = _selectedTopic[1];
    var _customTopic = useState("");
    var customTopic = _customTopic[0], setCustomTopic = _customTopic[1];
    var _isCustomTopic = useState(false);
    var isCustomTopic = _isCustomTopic[0], setIsCustomTopic = _isCustomTopic[1];
    var _isDebateActive = useState(false);
    var isDebateActive = _isDebateActive[0], setIsDebateActive = _isDebateActive[1];
    var _messages = useState([]);
    var messages = _messages[0], setMessages = _messages[1];
    var _sessionId = useState("");
    var sessionId = _sessionId[0], setSessionId = _sessionId[1];
    var _isLoading = useState(false);
    var isLoading = _isLoading[0], setIsLoading = _isLoading[1];
    var _maxRounds = useState(3);
    var maxRounds = _maxRounds[0], setMaxRounds = _maxRounds[1];
    var _currentRound = useState(1);
    var currentRound = _currentRound[0], setCurrentRound = _currentRound[1];
    var _phase = useState('setup');
    var phase = _phase[0], setPhase = _phase[1];
    var _showHistory = useState(false);
    var showHistory = _showHistory[0], setShowHistory = _showHistory[1];
    var _debateHistory = useState([]);
    var debateHistory = _debateHistory[0], setDebateHistory = _debateHistory[1];
    var _isPaused = useState(false);
    var isPaused = _isPaused[0], setIsPaused = _isPaused[1];
    // 使用 ref 保存可变状态，避免闭包问题
    var pausedRef = { current: false };
    var agentsRef = { current: agents };
    var proAgentRef = { current: proAgent };
    var conAgentRef = { current: conAgent };
    var maxRoundsRef = { current: maxRounds };
    var selectedTopicRef = { current: selectedTopic };
    var customTopicRef = { current: customTopic };
    var isCustomTopicRef = { current: isCustomTopic };
    var historyRef = { current: [] };

    // 加载数据
    useEffect(function() {
      fetch(API_BASE + "/agents")
        .then(function(r) { return r.json(); })
        .then(function(data) { 
          var agents = data.agents || [];
          setAgents(agents);
          if (agents.length >= 2) {
            setProAgent(agents[0]);
            setConAgent(agents[1]);
          }
        });

      fetch(API_BASE + "/topics")
        .then(function(r) { return r.json(); })
        .then(function(data) { setTopics(data.topics || []); });

      // 加载历史记录
      loadDebateHistory();

      // 恢复上次活跃的辩论会话
      restoreActiveSession();
    }, []);

    // 自动保存活跃会话状态
    useEffect(function() {
      if (isDebateActive && sessionId) {
        saveActiveSession();
      }
    }, [isDebateActive, sessionId, messages, maxRounds, currentRound, phase]);

    // 同步状态到 ref
    useEffect(function() {
      pausedRef.current = isPaused;
    }, [isPaused]);
    useEffect(function() {
      agentsRef.current = agents;
    }, [agents]);
    useEffect(function() {
      proAgentRef.current = proAgent;
    }, [proAgent]);
    useEffect(function() {
      conAgentRef.current = conAgent;
    }, [conAgent]);
    useEffect(function() {
      maxRoundsRef.current = maxRounds;
    }, [maxRounds]);
    useEffect(function() {
      selectedTopicRef.current = selectedTopic;
    }, [selectedTopic]);
    useEffect(function() {
      customTopicRef.current = customTopic;
    }, [customTopic]);
    useEffect(function() {
      isCustomTopicRef.current = isCustomTopic;
    }, [isCustomTopic]);

    function getItemsByPrefix(prefix) {
      const result = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith(prefix)) {
          const history = JSON.parse(localStorage.getItem(key));
          // 过滤掉空记录和无效记录
          var validHistory = history.filter(function(item) {
            return item && item.topic && item.messages && item.messages.length > 0;
          });
          result.push(...validHistory)
        }
      }
      return result;
    }

    // 加载辩论历史
    function loadDebateHistory() {
      try {
        var validHistory = getItemsByPrefix(STORAGE_KEY);
        if (validHistory) {         
          setDebateHistory(validHistory);
        }
      } catch (e) {
        console.error("[双虾汇] 加载历史失败:", e);
      }
    }

    // 保存辩论历史
    function saveDebateHistory() {
      try {
        var currentTopic = isCustomTopic ? customTopic : selectedTopic;
        if (!currentTopic || !sessionId) return;
        var historyItem = {
          id: sessionId,
          topic: currentTopic,
          proAgent: proAgent ? proAgent.name : '未知',
          conAgent: conAgent ? conAgent.name : '未知',
          maxRounds: maxRounds,
          messages: messages.map(function(m) {
            return {
              role: m.role,
              content: m.content || '',
              timestamp: m.timestamp || new Date().toISOString()
            };
          }),
          timestamp: new Date().toISOString()
        };
        var existing = JSON.parse(localStorage.getItem(STORAGE_KEY+sessionId) || '[]');
        // 去重：同一 session 只保留最新一条
        var filtered = existing.filter(function(item) { return item.id !== historyItem.id; });
        filtered.unshift(historyItem);
        if (filtered.length > 20) {
          filtered = filtered.slice(0, 20);
        }
        localStorage.setItem(STORAGE_KEY+sessionId, JSON.stringify(filtered));
        
      } catch (e) {
        console.error("[双虾汇] 保存历史失败:", e);
      }
    }

    // 保存活跃会话（用于离开后恢复）
    function saveActiveSession() {
      try {
        if (!sessionId || !isDebateActive) return;
        var activeSession = {
          sessionId: sessionId,
          phase: phase,
          messages: messages,
          maxRounds: maxRounds,
          currentRound: currentRound,
          topic: isCustomTopic ? customTopic : selectedTopic,
          isCustomTopic: isCustomTopic,
          proAgent: proAgent,
          conAgent: conAgent,
          timestamp: new Date().toISOString()
        };
        localStorage.setItem(ACTIVE_SESSION_KEY, JSON.stringify(activeSession));
      } catch (e) {
        console.error("[双虾汇] 保存活跃会话失败:", e);
      }
    }

    // 恢复活跃会话
    function restoreActiveSession() {
      try {
        var saved = localStorage.getItem(ACTIVE_SESSION_KEY);
        if (!saved) return;
        var activeSession = JSON.parse(saved);
        if (!activeSession || !activeSession.sessionId) return;
        
        // 检查是否过期（24小时）
        var savedTime = new Date(activeSession.timestamp).getTime();
        var now = Date.now();
        if (now - savedTime > 24 * 60 * 60 * 1000) {
          localStorage.removeItem(ACTIVE_SESSION_KEY);
          return;
        }

        setIsDebateActive(true);
        setPhase(activeSession.phase || 'debating');
        setSessionId(activeSession.sessionId);
        setMessages(activeSession.messages || []);
        setMaxRounds(activeSession.maxRounds || 3);
        setCurrentRound(activeSession.currentRound || 1);
        
        if (activeSession.topic) {
          if (topics.indexOf(activeSession.topic) >= 0) {
            setSelectedTopic(activeSession.topic);
            setIsCustomTopic(false);
          } else {
            setCustomTopic(activeSession.topic);
            setIsCustomTopic(true);
          }
        }
        
        if (activeSession.proAgent) setProAgent(activeSession.proAgent);
        if (activeSession.conAgent) setConAgent(activeSession.conAgent);
      } catch (e) {
        console.error("[双虾汇] 恢复活跃会话失败:", e);
      }
    }

    // 清除活跃会话
    function clearActiveSession() {
      try {
        localStorage.removeItem(ACTIVE_SESSION_KEY);
      } catch (e) {
        console.error("[双虾汇] 清除活跃会话失败:", e);
      }
    }

    // 加载历史辩论
    function loadHistoryDebate(historyItem) {
      setIsDebateActive(true);
      setPhase('debating');
      setSessionId(historyItem.id);
      setMessages(historyItem.messages || []);
      setMaxRounds(historyItem.maxRounds || 3);
      setCurrentRound(historyItem.maxRounds || 3);
      if (historyItem.topic) {
        if (topics.indexOf(historyItem.topic) >= 0) {
          setSelectedTopic(historyItem.topic);
          setIsCustomTopic(false);
        } else {
          setCustomTopic(historyItem.topic);
          setIsCustomTopic(true);
        }
      }
      // 恢复正反方智能体（通过名称匹配）
      var proName = historyItem.proAgent || '';
      var conName = historyItem.conAgent || '';
      var matchedPro = agents.find(function(a) { return a.name === proName; });
      var matchedCon = agents.find(function(a) { return a.name === conName; });
      if (matchedPro) setProAgent(matchedPro);
      if (matchedCon) setConAgent(matchedCon);
      setShowHistory(false);
    }

    // 删除历史记录
    function deleteHistory(id) {
      try {        
        localStorage.removeItem(STORAGE_KEY+id);
        setShowHistory(false);
        loadDebateHistory();
      } catch (e) {
        console.error("[双虾汇] 删除历史失败:", e);
      }
    }

    // 选择智能体
    function selectProAgent(agent) {
      if (conAgent && conAgent.id === agent.id) {
        alert("该智能体已被选为反方");
        return;
      }
      setProAgent(agent);
    }

    function selectConAgent(agent) {
      if (proAgent && proAgent.id === agent.id) {
        alert("该智能体已被选为正方");
        return;
      }
      setConAgent(agent);
    }

    // 开始辩论
    function startDebate() {
      if (!proAgent || !conAgent) {
        alert("请选择正反方智能体");
        return;
      }
      var finalTopic = isCustomTopic ? customTopic : selectedTopic;
      if (!finalTopic || finalTopic.trim() === '') {
        alert("请选择或输入辩论主题");
        return;
      }

      setIsLoading(true);
      var currentProAgentId = proAgentRef.current ? proAgentRef.current.id : (proAgent ? proAgent.id : '');
      var currentConAgentId = conAgentRef.current ? conAgentRef.current.id : (conAgent ? conAgent.id : '');
      var currentMaxRounds = maxRoundsRef.current || maxRounds;
      
      fetch(API_BASE + "/debate/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: finalTopic,
          pro_agent_id: currentProAgentId,
          con_agent_id: currentConAgentId,
          max_rounds: currentMaxRounds
        })
      })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        if (data.success) {
          var newSessionId = data.session_id;
          setIsDebateActive(true);
          setPhase('debating');
          setSessionId(newSessionId);
          setCurrentRound(1);
          setMessages(data.session.history || []);
          setIsLoading(false);
          setTimeout(function() {
            var initialHistory = (data.session.history || []).filter(function(m) { 
              return m.role === "pro" || m.role === "con"; 
            });
            runRoundWithSession(1, newSessionId, initialHistory);
          }, 500);
        } else {
          alert(data.error || "启动失败");
          setIsLoading(false);
        }
      })
      .catch(function(err) {
        console.error("启动错误:", err);
        alert("启动辩论失败");
        setIsLoading(false);
      });
    }

    // 运行单轮辩论
    function runRoundWithSession(round, currentSessionId, currentHistory) {
      // 使用 ref 获取最新状态，避免闭包问题
      var currentMaxRounds = maxRoundsRef.current || maxRounds;
      var currentPaused = pausedRef.current;
      var currentProAgent = proAgentRef.current || proAgent;
      var currentConAgent = conAgentRef.current || conAgent;
      
      if (round > currentMaxRounds) {
        setPhase('judging');
        setMessages(function(prev) {
          return prev.concat([{
            role: 'system',
            content: '🎉 辩论结束！请评判双方表现',
            timestamp: new Date().toISOString()
          }]);
        });
        // 保存到历史
        saveDebateHistory();
        return;
      }
      
      // 检查暂停状态
      if (currentPaused) {
        console.log("[双虾汇] 辩论已暂停，等待继续...");
        var checkInterval = setInterval(function() {
          if (!pausedRef.current) {
            clearInterval(checkInterval);
            runRoundWithSession(round, currentSessionId, currentHistory);
          }
        }, 500);
        return;
      }
      
      setCurrentRound(round);
      historyRef.current = currentHistory || [];
      
      console.log("[双虾汇] runRound", round, "history:", historyRef.current.length, "maxRounds:", currentMaxRounds);
      
      if (!currentProAgent || !currentConAgent || !currentSessionId) {
        console.error("[双虾汇] 缺少必要参数");
        return;
      }

      let sysProPrompt = '第' + round + '轮，请回应反方观点,并深化你的观点'
      let sysConPrompt = '第' + round + '轮，请回应正方观点,并深化你的观点'
      if(round==1){
         sysProPrompt = '第' + round + '轮，请正方阐述你的观点'
         sysConPrompt = '第' + round + '轮，请反方阐述你的观点'
      }
      sendAgentMessageWithAgent('pro', currentProAgent, sysProPrompt, round, currentSessionId, function(proResponse) {
        if (proResponse) historyRef.current = historyRef.current.concat([proResponse]);
        
        setTimeout(function() {
          sendAgentMessageWithAgent('con', currentConAgent, sysConPrompt, round, currentSessionId, function(conResponse) {
            if (conResponse) historyRef.current = historyRef.current.concat([conResponse]);
            
            setTimeout(function() {
              runRoundWithSession(round + 1, currentSessionId, historyRef.current);
            }, 800);
          }, historyRef.current);
        }, 500);
      }, historyRef.current);
    }
    
    // 暂停辩论
    function pauseDebate() {
      setIsPaused(true);
      setMessages(function(prev) {
        return prev.concat([{
          role: 'system',
          content: '⏸️ 辩论已暂停',
          timestamp: new Date().toISOString()
        }]);
      });
    }
    
    // 继续辩论
    function continueDebate() {
      setIsPaused(false);
      setMessages(function(prev) {
        return prev.concat([{
          role: 'system',
          content: '▶️ 辩论继续',
          timestamp: new Date().toISOString()
        }]);
      });
    }
    
    // 发送消息
    function sendAgentMessageWithAgent(side, agent, text, round, currentSessionId, callback, currentHistory) {
      var currentTopic = isCustomTopicRef.current ? customTopicRef.current : selectedTopicRef.current;
      
      console.log("[双虾汇] sendAgentMessage", side, "history:", currentHistory ? currentHistory.length : 0);
      
      if (!agent || !currentSessionId) {
        console.error("[双虾汇] 参数缺失");
        return;
      }

      setMessages(function(prev) {
        return prev.concat([{
          role: side,
          content: "⏳ 思考中...",
          timestamp: new Date().toISOString(),
          round: round,
          loading: true
        }]);
      });

      // 只保留最近6条历史，避免请求过大
      var trimmedHistory = (currentHistory || []).slice(-6);

      var controller = new AbortController();
      var timeoutId = setTimeout(function() {
        controller.abort();
      }, 30000); // 30秒超时

      fetch(API_BASE + "/debate/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: currentSessionId,
          agent_id: agent.id,
          side: side,
          text: text,
          debate_topic: currentTopic,
          history: trimmedHistory
        }),
        signal: controller.signal
      })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        clearTimeout(timeoutId);
        var responseMessage = null;
        if (data.success) {
          responseMessage = {
            role: side,
            content: data.response,
            timestamp: new Date().toISOString(),
            round: round,
            is_mock: data.mock
          };
          setMessages(function(prev) {
            var filtered = prev.filter(function(m) { return !m.loading; });
            return filtered.concat([responseMessage]);
          });
        } else {
          responseMessage = {
            role: side,
            content: "❌ 失败: " + (data.error || "未知错误"),
            timestamp: new Date().toISOString(),
            round: round,
            is_error: true
          };
          setMessages(function(prev) {
            var filtered = prev.filter(function(m) { return !m.loading; });
            return filtered.concat([responseMessage]);
          });
        }
        if (callback) callback(responseMessage);
      })
      .catch(function(err) {
        clearTimeout(timeoutId);
        console.error("[双虾汇] 错误:", err);
        var errorMessage = {
          role: side,
          content: "❌ 网络错误: " + (err.message === "The user aborted a request." ? "请求超时(30秒)" : err.message),
          timestamp: new Date().toISOString(),
          round: round,
          is_error: true
        };
        setMessages(function(prev) {
          var filtered = prev.filter(function(m) { return !m.loading; });
          return filtered.concat([errorMessage]);
        });
        if (callback) callback(errorMessage);
      });
    }

    // 评判
    function submitJudgment(winner) {
      var reason = winner === 'pro' ? '正方论证更有说服力' : 
                   winner === 'con' ? '反方反驳更加有力' : '双方势均力敌';
      fetch(API_BASE + "/debate/judge", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          winner: winner,
          reason: reason
        })
      })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        if (data.success) {
          setPhase('finished');
          var newMessages = messages.concat([{
            role: 'judge',
            content: data.message,
            timestamp: new Date().toISOString()
          }]);
          setMessages(newMessages);
          // 保存到历史
          saveDebateHistory();
        }
      });
    }

    // 重置
    function resetDebate() {
      if (sessionId) {
        fetch(API_BASE + "/debate/reset", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: sessionId })
        });
      }
      setIsDebateActive(false);
      setPhase('setup');
      setMessages([]);
      setSessionId("");
      setCurrentRound(1);
      setShowHistory(false);
      clearActiveSession();
    }

    // 渲染选择界面
    function renderSelection() {
      return h('div', { style: { maxWidth: '800px', margin: '0 auto', padding: '20px' } }, [
        h('div', { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' } }, [
          h('h1', { style: { color: '#333' } }, '🦐 双虾汇'),
          h('button', {
            onClick: function() { setShowHistory(true); },
            style: { padding: '10px 20px', background: '#9b59b6', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer' }
          }, '📜 历史记录')
        ]),
        
        // 历史记录弹窗
        showHistory && h('div', {
          style: {
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex',
            alignItems: 'center', justifyContent: 'center'
          }
        }, [
          h('div', {
            style: {
              background: '#fff', borderRadius: '16px', padding: '24px',
              maxWidth: '600px', maxHeight: '80vh', overflow: 'auto', width: '90%'
            }
          }, [
            h('div', { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' } }, [
              h('h2', null, '📜 历史辩论'),
              h('button', {
                onClick: function() { setShowHistory(false); },
                style: { background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer' }
              }, '✕')
            ]),
            debateHistory.length === 0 ? 
              h('div', { style: { textAlign: 'center', color: '#999', padding: '40px' } }, '暂无历史记录') :
              debateHistory.map(function(item, idx) {
                return h('div', { key: idx, style: { 
                  border: '1px solid #ddd', borderRadius: '8px', padding: '12px', marginBottom: '12px',
                  cursor: 'pointer', background: '#f9f9f9'
                }, onClick: function() { loadHistoryDebate(item); } }, [
                  h('div', { style: { fontWeight: 'bold', marginBottom: '4px' } }, item.topic),
                  h('div', { style: { fontSize: '12px', color: '#666' } }, 
                    '🟦 ' + item.proAgent + ' vs 🟥 ' + item.conAgent + ' · ' + item.maxRounds + '轮'
                  ),
                  h('div', { style: { fontSize: '12px', color: '#999', marginTop: '4px' } }, 
                    formatFullTime(item.timestamp)
                  ),
                  h('button', {
                    onClick: function(e) { e.stopPropagation(); deleteHistory(item.id); },
                    style: { 
                      marginTop: '8px', padding: '4px 12px', background: '#e74c3c', 
                      color: '#fff', border: 'none', borderRadius: '4px', fontSize: '12px', cursor: 'pointer'
                    }
                  }, '删除')
                ]);
              })
          ])
        ]),

        h('div', { style: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' } }, [
          h('div', { style: { border: '2px solid #4a90d9', borderRadius: '12px', padding: '16px' } }, [
            h('h3', { style: { color: '#4a90d9' } }, '🟦 正方'),
            h('div', null, agents.map(function(agent) {
              var isSelected = proAgent && proAgent.id === agent.id;
              return h('button', {
                key: agent.id,
                onClick: function() { selectProAgent(agent); },
                style: {
                  display: 'block', width: '100%', padding: '10px', marginBottom: '8px',
                  border: isSelected ? '2px solid #4a90d9' : '1px solid #ddd',
                  borderRadius: '8px',
                  background: isSelected ? '#4a90d9' : '#fff',
                  color: isSelected ? '#fff' : '#333',
                  cursor: 'pointer'
                }
              }, agent.name);
            }))
          ]),
          h('div', { style: { border: '2px solid #e74c3c', borderRadius: '12px', padding: '16px' } }, [
            h('h3', { style: { color: '#e74c3c' } }, '🟥 反方'),
            h('div', null, agents.map(function(agent) {
              var isSelected = conAgent && conAgent.id === agent.id;
              return h('button', {
                key: agent.id,
                onClick: function() { selectConAgent(agent); },
                style: {
                  display: 'block', width: '100%', padding: '10px', marginBottom: '8px',
                  border: isSelected ? '2px solid #e74c3c' : '1px solid #ddd',
                  borderRadius: '8px',
                  background: isSelected ? '#e74c3c' : '#fff',
                  color: isSelected ? '#fff' : '#333',
                  cursor: 'pointer'
                }
              }, agent.name);
            }))
          ])
        ]),
        h('div', { style: { marginBottom: '20px' } }, [
          h('h3', null, '📝 辩题'),
          h('select', {
            value: isCustomTopic ? 'custom' : selectedTopic,
            onChange: function(e) { 
              if (e.target.value === 'custom') {
                setIsCustomTopic(true);
              } else {
                setIsCustomTopic(false);
                setSelectedTopic(e.target.value);
              }
            },
            style: { width: '100%', padding: '12px', borderRadius: '8px', marginBottom: '10px' }
          }, [
            h('option', { value: '' }, '请选择...'),
            topics.map(function(t) { return h('option', { key: t, value: t }, t); }),
            h('option', { value: 'custom' }, '自定义')
          ]),
          isCustomTopic ? h('input', {
            type: 'text',
            value: customTopic,
            onChange: function(e) { setCustomTopic(e.target.value); },
            placeholder: '输入辩题',
            style: { width: '100%', padding: '12px', borderRadius: '8px', border: '2px solid #ff6b6b' }
          }) : null
        ]),
        h('div', { style: { marginBottom: '20px' } }, [
          h('h3', null, '⚙️ 轮次'),
          h('select', {
            value: maxRounds,
            onChange: function(e) { setMaxRounds(parseInt(e.target.value)); },
            style: { padding: '10px', borderRadius: '8px' }
          }, (function() {
            var opts = [];
            for (var i = 3; i <= 20; i++) {
              opts.push(h('option', { key: i, value: i }, i + '轮'));
            }
            opts.push(h('option', { key: 'divider', value: '', disabled: true }, '--- 超轮次 ---'));
            for (var j = 21; j <= 50; j++) {
              opts.push(h('option', { key: j, value: j }, j + '轮'));
            }
            return opts;
          })())
        ]),
        h('button', {
          onClick: startDebate,
          disabled: isLoading || !proAgent || !conAgent || (!selectedTopic && !customTopic),
          style: {
            width: '100%', padding: '16px', 
            background: '#27ae60', color: '#fff',
            border: 'none', borderRadius: '12px', fontSize: '18px',
            cursor: 'pointer'
          }
        }, isLoading ? '启动中...' : '开始辩论')
      ]);
    }

    // 渲染辩论界面
    function renderDebate() {
      var currentTopic = isCustomTopic ? customTopic : selectedTopic;
      return h('div', { style: { maxWidth: '800px', margin: '0 auto', padding: '20px' } }, [
        h('div', { style: { 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
          color: '#fff', padding: '20px', borderRadius: '12px', marginBottom: '20px'
        }}, [
          h('h2', null, '辩论进行中'),
          h('div', null, currentTopic),
          h('div', { style: { fontSize: '20px', marginTop: '10px' } }, '第 ' + currentRound + ' / ' + maxRounds + ' 轮')
        ]),
        h('div', { style: { border: '1px solid #ddd', borderRadius: '12px', padding: '16px', minHeight: '300px', marginBottom: '20px' } }, [
          h('div', { style: { marginBottom: '16px' } }, [
            h('h3', null, '辩论记录')
          ]),
          messages.map(function(msg, idx) {
            var isPro = msg.role === 'pro';
            var isCon = msg.role === 'con';
            var isJudge = msg.role === 'judge';
            var isLoading = msg.loading;
            var style = { 
              marginBottom: '12px', padding: '12px', borderRadius: '8px',
              background: isLoading ? '#fff3e0' : isPro ? '#e3f2fd' : isCon ? '#ffeaea' : isJudge ? '#f3e5f5' : '#f8f9fa',
              borderLeft: isPro ? '4px solid #4a90d9' : isCon ? '4px solid #e74c3c' : 'none',
              opacity: isLoading ? 0.8 : 1
            };
            var content = msg.content ? escapeHtml(msg.content).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>') : '';
            return h('div', { key: idx, style: style }, [
              h('div', { style: { fontSize: '12px', color: '#666', marginBottom: '4px' } }, 
                (isPro ? '🟦 正方' : isCon ? '🟥 反方' : isJudge ? '⚖️ 判决' : '📢 系统') + 
                (isLoading ? ' ⏳ 思考中...' : ' · ' + formatTime(msg.timestamp))
              ),
              h('div', { dangerouslySetInnerHTML: { __html: content } })
            ]);
          })
        ]),
        phase === 'judging' && h('div', { style: { display: 'flex', gap: '12px' } }, [
          h('button', { onClick: function() { submitJudgment('pro'); }, style: { flex: 1, padding: '12px', background: '#4a90d9', color: '#fff', border: 'none', borderRadius: '8px' } }, '正方胜'),
          h('button', { onClick: function() { submitJudgment('draw'); }, style: { flex: 1, padding: '12px', background: '#9b59b6', color: '#fff', border: 'none', borderRadius: '8px' } }, '平局'),
          h('button', { onClick: function() { submitJudgment('con'); }, style: { flex: 1, padding: '12px', background: '#e74c3c', color: '#fff', border: 'none', borderRadius: '8px' } }, '反方胜')
        ]),
        h('div', { style: { display: 'flex', gap: '12px' } }, [
          h('button', { 
            onClick: isPaused ? continueDebate : pauseDebate,
            style: { flex: 1, padding: '12px', background: isPaused ? '#27ae60' : '#f39c12', color: '#fff', border: 'none', borderRadius: '8px' } 
          }, isPaused ? '▶️ 继续辩论' : '⏸️ 暂停辩论'),
          h('button', { 
            onClick: resetDebate, 
            style: { flex: 1, padding: '12px', background: '#95a5a6', color: '#fff', border: 'none', borderRadius: '8px' } 
          }, '🔄 重新开始')
        ])
      ]);
    }

    return h('div', null, [
      isDebateActive ? renderDebate() : renderSelection()
    ]);
  }

  // 注册路由
  if (QP.registerRoutes) {
    QP.registerRoutes(PLUGIN_ID, [{
      path: "/apps/" + PLUGIN_ID,
      component: ShuangXiaHuiApp,
      label: PLUGIN_NAME,
      icon: "🦐",
      priority: 100
    }]);
    console.log('[双虾汇] 已注册路由');
  }

  console.log('[双虾汇] v2.4.3 加载完成');
})();
