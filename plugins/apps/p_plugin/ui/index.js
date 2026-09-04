/**
 * P Plugin v5.2.0 — WS重连修复 + 诊断日志 + 防抖增强 (2026-07-28)
 * - WS 重连: 用 curRoomIdRef 消除闭包陈旧问题，socket 身份校验防止旧连接覆盖新连接
 * - 未读红点: localStorage 持久化，当前房间不计数
 * - 诊断日志: 完整 WS 生命周期日志 (connect/disconnect/reconnect/msg/dedup/unread)
 * - 乐观更新: 发送失败时自动清除临时消息
 * - 防抖: 录音按钮防连点，位置发送防重复
 * - 面板权限: 任何人可添加面板，仅房主可删除面板
 * - 频道接入弹窗: 聚焦官方聊天室，四层群聊架构
 */
(function() {
  'use strict';
  console.log('[P] === P Plugin v5.2.0 Initializing ===');
  console.log('[P] Timestamp:', new Date().toISOString());
  
  var QP = window.QwenPaw;
  if (!QP) {
    console.error('[P] ❌ window.QwenPaw not available');
    return;
  }
  if (!QP.host) {
    console.error('[P] ❌ QP.host not available');
    return;
  }
  
  var host = QP.host;
  var React = host.React;
  var antd = host.antd;
  var h = React.createElement;
  var Button = antd.Button, Input = antd.Input, Avatar = antd.Avatar;
  var Modal = antd.Modal, Select = antd.Select, Tag = antd.Tag;
  var msg = antd.message, Tooltip = antd.Tooltip, Popover = antd.Popover;
  var Badge = antd.Badge;
  
  var EMOJIS = {
    smiley: ['😀','😃','😄','😁','😅','😂','🤣','😊','😇','🙂','🙃','😉','😌','😍','🥰','😘','😗','😙','😚','😋','😛','😝','😜','🤪','🤨','🧐','🤓','😎','🥸','🤩','🥳','😏','😒','😞','😔','😟','😕','😣','😖','😫','😩','🥺','😢','😭','😤','😠','😡','🤯','😳','🥵','🥶','😱','😨','😰','😥','😓','🤗','🤔','🤭','🤫','😶','😐','😑','😬','🙄','😯','😦','😧','😮','😲','🥱','😴','🤤','😪','😵','🤐','🥴','🤢','🤮','🤧','😷','🤒','🤕','🤑','🤠','😈','👿','👹','👺','🤡','💩','👻','💀','👽','👾','🤖','🎃','😺','😸','😹','😻','😼','😽','🙀','😿','😾'],
    gesture: ['👋','🤚','🖐','✋','🖖','👌','🤌','🤏','✌️','🤞','🤟','🤘','🤙','👈','👉','👆','👇','👍','👎','✊','👊','🤛','🤜','👏','🙌','👐','🤲','🤝','🙏','💪','🦾','🦿','🦵','🦶','👂','🦻','👃','🧠','🫀','🫁','🦷','🦴','👀','👁','👅','👄','💋','🩸'],
    nature: ['🐶','🐱','🐭','🐹','🐰','🦊','🐻','🐼','🐨','🐯','🦁','🐮','🐷','🐽','🐸','🐵','🐒','🐔','🐧','🐦','🐤','🐣','🐥','🦆','🦅','🦉','🦇','🐺','🐗','🐴','🦄','🐝','🐛','🦋','🐌','🐞','🐜','🦟','🦗','🕷','🕸','🦂','🐢','🐍','🦎','🦖','🦕','🐙','🦑','🦐','🦞','🦀','🐡','🐠','🐟','🐬','🐳','🐋','🦈','🐊','🐅','🐆','🦓','🦍','🦧','🐘','🦛','🦏','🐪','🐫','🦒','🦘','🦬','🐃','🐂','🐄','🐎','🐖','🐏','🐑','🦙','🐐','🦌','🐕','🐩','🦮','🐕‍🦺','🐈','🐈‍⬛','🐓','🦃','🕊','🐇','🐁','🐀','🐿','🦫','🦔','🐾','🐉','🐲','🌵','🎄','🌲','🌳','🌴','🌱','🌿','☘️','🍀','🎍','🎋','🍃','🍂','🍁','🍄','🐚','🌾','💐','🌷','🌹','🥀','🌺','🌸','🌼','🌻','🌞','🌝','🌛','🌜','🌚','🌕','🌖','🌗','🌘','🌑','🌒','🌓','🌔','🌙','🌎','🌍','🌏','🪐','💫','⭐','🌟','✨','⚡','🔥','💥','☄️','☀️','🌤','⛅','🌥','☁️','🌦','🌧','⛈','🌩','🌨','❄️','☃️','⛄','🌬','💨','💧','💦','☔','☂️','🌊','🌫'],
    food: ['🍏','🍎','🍐','🍊','🍋','🍌','🍉','🍇','🍓','🫐','🍈','🍒','🍑','🍍','🥝','🥥','🥑','🍆','🥔','🥕','🌽','🌶','🫑','🥒','🥬','🥦','🧄','🧅','🍄','🥜','🌰','🍞','🥐','🥖','🥨','🥯','🥞','🧇','🧀','🍖','🍗','🥩','🥓','🍔','🍟','🍕','🌭','🥪','🌮','🌯','🫔','🥙','🧆','🥚','🍳','🥘','🍲','🥣','🥗','🍿','🧈','🧂','🥫','🍱','🍘','🍙','🍚','🍛','🍜','🍝','🍠','🍢','🍣','🍤','🍥','🍡','🥟','🥠','🥡','🍦','🍧','🍨','🍩','🍪','🎂','🍰','🧁','🥧','🍫','🍬','🍭','🍮','🍯','🍼','🥛','☕','🫖','🍵','🧃','🥤','🧋','🍶','🍺','🍻','🥂','🍷','🥃','🍸','🍹','🧉','🍾','🧊','🥄','🍴','🍽','🥡','🥢'],
    activity: ['⚽','🏀','🏈','⚾','🥎','🎾','🏐','🏉','🥏','🎱','🪀','🏓','🏸','🏒','🏑','🥍','🏏','🥅','⛳','🪁','🏹','🎣','🤿','🥊','🥋','🎽','🛹','🛼','🛷','⛸','🥌','🎿','⛷','🏂','🪂','🏋️‍♀️','🏋️','🏋️‍♂️','🤼‍♀️','🤼','🤼‍♂️','🤸‍♀️','🤸','🤸‍♂️','⛹️‍♀️','⛹️','⛹️‍♂️','🤺','🤾‍♀️','🤾','🤾‍♂️','🏌️‍♀️','🏌️','🏌️‍♂️','🏇','🧘‍♀️','🧘','🧘‍♂️','🏄‍♀️','🏄','🏄‍♂️','🏊‍♀️','🏊','🏊‍♂️','🤽‍♀️','🤽','🤽‍♂️','🚣‍♀️','🚣','🚣‍♂️','🧗‍♀️','🧗','🧗‍♂️','🚵‍♀️','🚵','🚵‍♂️','🚴‍♀️','🚴','🚴‍♂️','🏆','🥇','🥈','🥉','🏅','🎖','🏵','🎗','🎫','🎟','🎪','🤹‍♀️','🤹','🤹‍♂️','🎭','🩰','🎨','🎬','🎤','🎧','🎼','🎹','🥁','🪘','🎷','🎺','🪗','🎸','🪕','🎻','🎲','♟','🎯','🎳','🎮','🎰']
  };
  
  function apiFetch(path, opts) {
    opts = opts || {};
    var url = host.getApiUrl(path);
    var token = host.getApiToken ? host.getApiToken() : '';
    var headers = opts.headers || {};
    if (opts.json !== false) headers['Content-Type'] = 'application/json';
    if (token) headers['Authorization'] = 'Bearer ' + token;
    var fo = { method: opts.method || 'GET', headers: headers };
    if (opts.body) fo.body = opts.json !== false ? JSON.stringify(opts.body) : opts.body;
    return fetch(url, fo).then(function(r) { 
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    });
  }
  
  function wsUrl(path) {
    // host.getApiUrl returns "/api/..." (relative). Convert to full ws:// URL.
    var apiUrl = host.getApiUrl(path);
    // Build full ws URL from current location
    var loc = window.location;
    var wsProto = loc.protocol === 'https:' ? 'wss:' : 'ws:';
    return wsProto + '//' + loc.host + apiUrl;
  }
  
  // 表情选择器
  function EmojiPicker(p) {
    var [cat, setCat] = React.useState('smiley');
    var cats = [{k:'smiley',i:'😀',n:'表情'},{k:'gesture',i:'👋',n:'手势'},{k:'nature',i:'🐶',n:'自然'},{k:'food',i:'🍎',n:'食物'},{k:'activity',i:'⚽',n:'活动'}];
    return h('div',{style:{width:320,padding:10,background:'#fff',borderRadius:8}},[
      h('div',{style:{display:'flex',gap:6,marginBottom:10,borderBottom:'1px solid #eee',paddingBottom:8}},
        cats.map(function(c){return h('div',{key:c.k,title:c.n,
          style:{width:38,height:38,borderRadius:8,background:cat===c.k?'#07C160':'#f5f5f5',color:cat===c.k?'white':'#333',display:'flex',alignItems:'center',justifyContent:'center',fontSize:20,cursor:'pointer'},
          onClick:function(){setCat(c.k);}},c.i);})),
      h('div',{style:{display:'flex',flexWrap:'wrap',gap:5,maxHeight:200,overflow:'auto'}},
        EMOJIS[cat].map(function(e){return h('div',{key:e,
          style:{width:34,height:34,borderRadius:6,display:'flex',alignItems:'center',justifyContent:'center',fontSize:20,cursor:'pointer'},
          onClick:function(){p.onSelect(e);}},e);}))
    ]);
  }
  
  // @提及下拉 - 支持智能体和用户
  function MentionDropdown(p) {
    var agents = p.agents || [];
    var users = p.users || [];
    var query = p.query || '';
    var sel = p.sel || 0;
    var type = p.type || 'agents';
    
    // 过滤智能体和用户
    var filteredAgents = agents.filter(function(a){return a.name.toLowerCase().indexOf(query.toLowerCase())>=0;});
    var filteredUsers = users.filter(function(u){return u.name.toLowerCase().indexOf(query.toLowerCase())>=0;});
    
    var allItems = [];
    if(filteredAgents.length > 0) {
      allItems.push({type:'header',label:'🤖 智能体'});
      filteredAgents.forEach(function(a){allItems.push({type:'agent',data:a});});
    }
    if(filteredUsers.length > 0) {
      allItems.push({type:'header',label:'👤 在线用户'});
      filteredUsers.forEach(function(u){allItems.push({type:'user',data:u});});
    }
    
    if(!allItems.length) return null;
    
    return h('div',{style:{position:'absolute',bottom:'100%',left:0,right:0,background:'white',border:'1px solid #e8e8e8',borderRadius:8,maxHeight:250,overflow:'auto',zIndex:100,boxShadow:'0 -4px 12px rgba(0,0,0,0.15)',marginBottom:4}},
      allItems.map(function(item,i){
        if(item.type === 'header') {
          return h('div',{key:'header-'+i,style:{padding:'6px 12px',fontSize:12,color:'#999',background:'#f5f5f5',fontWeight:600}},item.label);
        }
        var isAgent = item.type === 'agent';
        var data = item.data;
        return h('div',{key:data.id||i,
          style:{padding:'10px 12px',display:'flex',alignItems:'center',gap:10,cursor:'pointer',background:i===sel?'#e6f7ff':'transparent',borderBottom:'1px solid #f0f0f0'},
          onClick:function(){p.onSelect(data,isAgent);}},
          [h('div',{style:{width:32,height:32,borderRadius:'50%',background:isAgent?(data.color||'#07C160'):'#1890ff',display:'flex',alignItems:'center',justifyContent:'center',fontSize:16,color:'white'}},isAgent?(data.icon||'🤖'):'👤'),
          h('div',{style:{flex:1}},[h('div',{style:{fontSize:14,fontWeight:500}},data.name),h('div',{style:{fontSize:11,color:'#999'}},isAgent?'智能体':'用户')])]);}));
  }
  
  // 智能体选择器（多选）
  function AgentSelector(p) {
    var [agents, setAgents] = React.useState([]);
    var [loading, setLoading] = React.useState(true);
    var [selected, setSelected] = React.useState([]);
    React.useEffect(function(){
      apiFetch('/plugins/p_plugin/agents').then(function(d) {
        var list = (d.agents||[]).filter(function(a) {
          return !p.roomAgents.some(function(ra){return ra.id===a.id;});
        });
        setAgents(list); setLoading(false);
      }).catch(function(){setLoading(false);});
    },[]);
    function toggle(a) {
      var idx = selected.indexOf(a.id);
      if(idx>=0) setSelected(selected.filter(function(id){return id!==a.id;}));
      else setSelected([...selected,a.id]);
    }
    function addSel() {
      selected.forEach(function(id) {
        var a = agents.find(function(x){return x.id===id;});
        if(a) p.onAdd(a);
      });
      setSelected([]);
    }
    return h('div',null,[
      h('div',{style:{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:16}},[
        h('div',{},[h('div',{style:{fontSize:16,fontWeight:600}},'选择智能体'),h('div',{style:{fontSize:12,color:'#999',marginTop:4}},'可多选，选中的智能体将加入群聊')]),
        h('div',{style:{display:'flex',gap:8}},[
          h(Button,{size:'small',disabled:selected.length===0,type:'primary',onClick:addSel},'添加选中 ('+selected.length+')'),
          h(Button,{size:'small',onClick:function(){setSelected(agents.map(function(a){return a.id;}));}},'全选')
        ])
      ]),
      loading ? h('div',{style:{textAlign:'center',padding:40,color:'#999'}},'正在加载智能体...') :
      agents.length===0 ? h('div',{style:{textAlign:'center',padding:40,color:'#999'}},'暂无可添加的智能体') :
      h('div',{style:{maxHeight:400,overflow:'auto'}},agents.map(function(a){
        var sel = selected.indexOf(a.id)>=0;
        return h('div',{key:a.id,
          style:{display:'flex',alignItems:'center',padding:12,marginBottom:8,background:sel?'#e6f7ff':'#fafafa',border:sel?'2px solid #07C160':'1px solid #e8e8e8',borderRadius:10,cursor:'pointer',transition:'all 0.2s'},
          onClick:function(){toggle(a);}},
          [h('div',{style:{width:44,height:44,borderRadius:'50%',background:a.color||'#07C160',display:'flex',alignItems:'center',justifyContent:'center',fontSize:22,marginRight:12,flexShrink:0}},a.icon||'🤖'),
          h('div',{style:{flex:1}},[h('div',{style:{fontSize:15,fontWeight:600,marginBottom:2}},a.name),h('div',{style:{fontSize:12,color:'#999'}},a.id),a.description?h('div',{style:{fontSize:12,color:'#666',marginTop:4}},a.description):null]),
          h('div',{style:{width:24,height:24,borderRadius:'50%',border:sel?'2px solid #07C160':'2px solid #ddd',background:sel?'#07C160':'white',display:'flex',alignItems:'center',justifyContent:'center',color:'white',fontSize:12,flexShrink:0}},sel?'✓':'')]);
      }))
    ]);
  }
  
  // 主页面
  function PPage(props) {
    var onBack = props.onBack;
    var [uid, setUid] = React.useState(function(){var v=localStorage.getItem('p_plugin_uid');if(v)return v;v='u'+Date.now().toString(36);localStorage.setItem('p_plugin_uid',v);return v;});
    var [nick, setNick] = React.useState(function(){return localStorage.getItem('p_plugin_nick')||'用户';});
    var [rooms, setRooms] = React.useState([]);
    var [curRoom, setCurRoom] = React.useState(null);
    var [msgs, setMsgs] = React.useState([]);
    var [input, setInput] = React.useState('');
    var [sending, setSending] = React.useState(false);
    var [roomAgents, setRoomAgents] = React.useState([]);
    var [showAgentModal, setShowAgentModal] = React.useState(false);
    var [showCreate, setShowCreate] = React.useState(false);
    var [showSearch, setShowSearch] = React.useState(false);
    var [showEmoji, setShowEmoji] = React.useState(false);
    var [showSettings, setShowSettings] = React.useState(false);
    var [newRN, setNewRN] = React.useState('');
    var [wsStatus, setWsStatus] = React.useState('disconnected');
    var [agentTyping, setAgentTyping] = React.useState([]);
    var [mentionQuery, setMentionQuery] = React.useState('');
    var [showMention, setShowMention] = React.useState(false);
    var [mentionIndex, setMentionIndex] = React.useState(0);
    var [mentionType, setMentionType] = React.useState('agents'); // 'agents' or 'users'
    
    // 从消息中提取最近发言的用户（去重）
    var roomUsers = React.useMemo(function(){
      if(!msgs || !msgs.length) return [];
      var userMap = {};
      // 倒序遍历，保留最近发言的用户
      for(var i = msgs.length - 1; i >= 0; i--) {
        var m = msgs[i];
        if(m.sender_id && m.sender_name && !m.sender_id.startsWith('agent_') && m.sender_id !== 'system') {
          if(!userMap[m.sender_id]) {
            userMap[m.sender_id] = {id: m.sender_id, name: m.sender_name, lastSeen: m.timestamp};
          }
        }
      }
      return Object.values(userMap).slice(0, 20); // 最多显示20个用户
    }, [msgs]);
    var [searchQuery, setSearchQuery] = React.useState('');
    var [searchResults, setSearchResults] = React.useState([]);
    var [theme, setTheme] = React.useState(localStorage.getItem('p_plugin_theme')||'light');
    var [showWeChat, setShowWeChat] = React.useState(false);
    var [pchatStatus, setPchatStatus] = React.useState({installed:false,in_official_room:false,loading:false});
    var [showShare, setShowShare] = React.useState(false);
    var [sharePassword, setSharePassword] = React.useState('');
    var [shareExpiry, setShareExpiry] = React.useState(0);
    var [shareLink, setShareLink] = React.useState('');
    var [shareToken, setShareToken] = React.useState('');
    var [shares, setShares] = React.useState([]);
    var [shareCreating, setShareCreating] = React.useState(false);
    var [recording, setRecording] = React.useState(false);
    var [locating, setLocating] = React.useState(false);
    // ── Announcement & Game Agents ──
    var [announcement, setAnnouncement] = React.useState('');
    var [showAnnouncement, setShowAnnouncement] = React.useState(true);
    var [editingAnnouncement, setEditingAnnouncement] = React.useState(false);
    var [announcementDraft, setAnnouncementDraft] = React.useState('');
    var [gameAgentsStatus, setGameAgentsStatus] = React.useState(null);
    var [installingAgents, setInstallingAgents] = React.useState(false);
    // ── Scene System ──
    var [currentScene, setCurrentScene] = React.useState(null);
    var [showSceneSelector, setShowSceneSelector] = React.useState(false);
    var [availableScenes, setAvailableScenes] = React.useState([]);
    // ── Inventory System ──
    var [inventory, setInventory] = React.useState({items:[],clues:[],achievements:[]});
    var [showInventory, setShowInventory] = React.useState(false);
    var [quests, setQuests] = React.useState({active:[],completed:[]});
    var [showQuests, setShowQuests] = React.useState(false);
    var wsRef = React.useRef(null);
    var curRoomIdRef = React.useRef(null);  // 当前房间 ID（用于 WS 重连判断）
    var msgsEndRef = React.useRef(null);
    var mediaRecRef = React.useRef(null);
    var voiceChunksRef = React.useRef([]);
    var isCreator = curRoom && (curRoom.creator_id===uid || curRoom.type==='official');
    // 同步 ref 到最新房间 ID（解决闭包陈旧问题）
    curRoomIdRef.current = curRoom ? curRoom.id : null;
    // ── Panel system (Tailchat-style Discover) ──
    var [roomPanels, setRoomPanels] = React.useState([]);
    var [curPanel, setCurPanel] = React.useState(null);
    var [showAddPanel, setShowAddPanel] = React.useState(false);
    var [newPanelUrl, setNewPanelUrl] = React.useState('');
    var [newPanelName, setNewPanelName] = React.useState('');
    var [addPanelType, setAddPanelType] = React.useState('webview');
    // ── Network Code / Discover (Give U Face IPv6 fusion) ──
    var [ncInput, setNcInput] = React.useState('');
    var [ncResult, setNcResult] = React.useState(null);
    var [ncMyCodes, setNcMyCodes] = React.useState([]);
    var [ncServices, setNcServices] = React.useState([]);
    var [ncLoading, setNcLoading] = React.useState(false);
    var [discoverUrlInp, setDiscoverUrlInp] = React.useState('');
    var [discoverUrlRes, setDiscoverUrlRes] = React.useState(null);
    
    var C = theme==='dark' ? {
      primary:'#07C160',bg:'#111',card:'#1e1e1e',sidebar:'#1a1a1a',header:'#000',
      text:'#eee',sec:'#888',border:'#333',bm:'#07C160',bo:'#2a2a2a'
    } : {
      primary:'#07C160',bg:'#EDEDED',card:'#FFF',sidebar:'#FFF',header:'#2E2E2E',
      text:'#191919',sec:'#999',border:'#E5E5E5',bm:'#95EC69',bo:'#FFF'
    };
    
    function fetchRooms(){apiFetch('/plugins/p_plugin/rooms?user_id='+uid).then(function(d){setRooms(d.rooms||[]);}).catch(function(){});}
    function fetchMsgs(){if(!curRoom)return;apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/messages?limit=100').then(function(d){setMsgs(d.messages||[]);});}
    
    function connectWs(){
      var roomId = curRoomIdRef.current;
      if(!roomId||wsRef.current)return;
      console.log('[P WS] 🔌 connecting to room', roomId);
      var ws = new WebSocket(wsUrl('/plugins/p_plugin/ws/'+uid));
      wsRef.current=ws;setWsStatus('connecting');
      ws.onopen=function(){
        console.log('[P WS] ✅ connected, joining room', roomId);
        setWsStatus('connected');
        ws.send(JSON.stringify({type:'join',room_id:roomId}));
      };
      ws.onmessage=function(e){
        try{
          var d=JSON.parse(e.data);
          var currentRoom = curRoomIdRef.current;
          if(d.type==='new_message'){
            if(d.room_id===currentRoom){
              setMsgs(function(p){
                // 去重：检查消息ID或相同用户+内容+时间（5秒内）
                var exists=p.some(function(m){
                  if(m.id===d.message.id)return true;
                  // 额外检查：相同用户、相同内容、5秒内发送的消息
                  if(m.sender_id===d.message.sender_id && 
                     m.content===d.message.content &&
                     Math.abs(new Date(m.timestamp)-new Date(d.message.timestamp))<5000)return true;
                  return false;
                });
                if(exists)console.log('[P WS] ♻ DEDUP msg',d.message.id);
                else console.log('[P WS] ← msg', d.message.sender_name||'?', (d.message.content||'').substring(0,50));
                return exists?p:[...p,d.message];
              });
            }
            else{
              incUnread(d.room_id);
              console.log('[P WS] 🔴 UNREAD +1 room', d.room_id, '(current=', currentRoom,')');
            }
          }
          else if(d.type==='agent_typing'){
            console.log('[P WS] ⌨ typing:', d.agent_name, d.typing?'start':'stop');
            setAgentTyping(function(p){return d.typing?[...new Set([...p,d.agent_name])]:p.filter(function(n){return n!==d.agent_name;});});
          }
          else if(d.type==='room_update'){
            console.log('[P WS] 🔄 room_update');
            fetchRooms();
            if(currentRoom){
              apiFetch('/plugins/p_plugin/rooms/'+currentRoom).then(function(d){
                setCurRoom(d);setRoomAgents(d.agents||[]);setRoomPanels(d.panels||[]);
                if(curPanel&&!(d.panels||[]).some(function(p){return p.id===curPanel.id;})){setCurPanel((d.panels||[])[0]||null);}
              });
            }
          }
          else{console.log('[P WS] ← unknown type:', d.type);}
        }catch(err){console.error('[P WS] ❌ parse error:', err, e.data.substring(0,200));}
      };
      ws.onclose=function(ev){
        console.log('[P WS] 🔌 disconnected code='+ev.code+' reason='+(ev.reason||'none')+' wasClean='+ev.wasClean);
        setWsStatus('disconnected');
        // 只清当前 socket 的引用（防止旧 socket 覆盖新连接）
        if(wsRef.current===ws) wsRef.current=null;
        // 5秒后自动重连（用 ref 读最新房间，避免闭包陈旧）
        setTimeout(function(){
          var rId = curRoomIdRef.current;
          console.log('[P WS] ⏳ reconnect check — room='+rId+' hasWs='+!!wsRef.current);
          if(rId&&!wsRef.current) connectWs();
        },5000);
      };
      ws.onerror=function(ev){
        console.error('[P WS] ❌ error event, will close');
        ws.close();
      };
    }
    
    React.useEffect(function(){if(wsRef.current){wsRef.current.close();wsRef.current=null;}setAgentTyping([]);if(curRoom){fetchMsgs();setTimeout(connectWs,200);
      apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/panels').then(function(d){
        var panels=d.panels||[];setRoomPanels(panels);
        if(!curPanel||!panels.some(function(p){return p.id===curPanel.id;})){setCurPanel(panels[0]||null);}
      }).catch(function(){});
    }},[curRoom&&curRoom.id]);
    React.useEffect(function(){fetchRooms();},[]);
    React.useEffect(function(){
      if(curPanel&&curPanel.type==='custom'){
        // Only load Network Code/Discover functionality for specific panels
        if(curPanel.name.includes('网络搜索') || curPanel.name.includes('🌐 发现') ||
           curPanel.icon === '🌐' || curPanel.icon === '💬'){
          loadMyNC();
          loadDiscoverServices();
        }
      }
    },[curPanel&&curPanel.id]);
        React.useEffect(function(){if(msgsEndRef.current)msgsEndRef.current.scrollIntoView({behavior:'smooth'});},[msgs,agentTyping]);
    React.useEffect(function(){setRoomAgents(curRoom?(curRoom.agents||[]):[]);},[curRoom]);
    // Fetch announcement when room changes
    React.useEffect(function(){
      if(!curRoom){setAnnouncement('');setGameAgentsStatus(null);return;}
      apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/announcement').then(function(d){
        setAnnouncement(d.announcement||'');
        setShowAnnouncement(!!d.announcement);
      }).catch(function(){setAnnouncement('');});
      // Check game agents status for rooms with 0 agents
      apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/game-agents-status').then(function(d){
        setGameAgentsStatus(d);
      }).catch(function(){setGameAgentsStatus(null);});
      // Load scene
      apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/scene').then(function(d){
        setCurrentScene(d.scene);
      }).catch(function(){});
      // Load inventory
      apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/inventory/'+uid).then(function(d){
        setInventory({items:d.items||[],clues:d.clues||[],achievements:d.achievements||[]});
      }).catch(function(){});
      // Load quests
      apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/quests/'+uid).then(function(d){
        setQuests({active:d.active||[],completed:d.completed||[]});
      }).catch(function(){});
    },[curRoom&&curRoom.id]);
    // Load available scenes
    React.useEffect(function(){
      apiFetch('/plugins/p_plugin/scenes').then(function(d){
        setAvailableScenes(d.scenes||[]);
      }).catch(function(){});
    },[]);
    // P-Chat Agent 状态检查 — 频道弹窗打开时查询
    React.useEffect(function(){
      if(!showWeChat) return;
      setPchatStatus(function(ps){return{...ps,loading:true};});
      apiFetch('/plugins/p_plugin/agents/pchat/status').then(function(d){
        setPchatStatus({installed:d.installed,in_official_room:d.in_official_room,loading:false});
      }).catch(function(){setPchatStatus({installed:false,in_official_room:false,loading:false});});
    },[showWeChat]);

    // ── Panel management ──
    function addPanel(){
      if(!curRoom){msg.warning('No room selected');return;}
      if(!newPanelUrl.trim()&&addPanelType==='webview'){msg.warning('Please enter a URL');return;}
      var name=newPanelName.trim();
      if (!name) {
        if (addPanelType === 'webview') {
          name = '🌐 ' + newPanelUrl.trim().replace(/^https?:\/\//,'').replace(/\/.*/,'');
        } else if (addPanelType === 'custom') {
          name = '📝 Custom Panel';
        } else {
          name = '💬 Chat Panel';
        }
      }
      var panelData = {
        user_id: uid,
        type: addPanelType,
        name: name,
        icon: addPanelType==='webview'?'🌐':(addPanelType==='custom'?'📝':'💬')
      };

      if(addPanelType === 'webview'){
        panelData.url = newPanelUrl.trim();
      } else if(addPanelType === 'custom'){
        panelData.html = newPanelUrl.trim(); // HTML content goes in html field for custom panels
      }

      apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/panels',{method:'POST',body:panelData})
        .then(function(d){if(d.success){msg.success('Panel added!');setNewPanelUrl('');setNewPanelName('');setShowAddPanel(false);
          apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/panels').then(function(r){setRoomPanels(r.panels||[]);});}
        }).catch(function(e){msg.error('Add failed');});
    }
    function removePanel(panel){
      if(!curRoom||!isCreator){msg.warning('Only room creator can remove panels');return;}
      Modal.confirm({title:'Confirm',content:'Remove panel '+panel.name+'?',okText:'Remove',okType:'danger',cancelText:'Cancel',
        onOk:function(){
          apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/panels/'+panel.id,{method:'DELETE',body:{user_id:uid}})
            .then(function(d){if(d.success){msg.success('Removed');apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/panels').then(function(r){
              var panels=r.panels||[];setRoomPanels(panels);if(curPanel&&curPanel.id===panel.id)setCurPanel(panels[0]||null);
            });}}).catch(function(e){msg.error('Remove failed');});
        }});
    }
    
    // ── Network Code / Discover functions ──
    function discoverAddUrl(){
      var url=discoverUrlInp.trim();if(!url){msg.warning('请输入网址');return;}
      if(!curRoom){msg.warning('请先选择房间');return;}
      if(!url.startsWith('http://')&&!url.startsWith('https://'))url='https://'+url;
      var name='🌐 '+url.replace(/^https?:\/\//,'').replace(/\/.*/,'');
      apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/panels',{method:'POST',body:{user_id:uid,type:'webview',name:name,url:url,icon:'🌐'}})
        .then(function(d){if(d.success){setDiscoverUrlRes('✅ 已添加面板「'+name+'」');setDiscoverUrlInp('');
          apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/panels').then(function(r){setRoomPanels(r.panels||[]);});}
        }).catch(function(){setDiscoverUrlRes('❌ 添加失败');});
    }
    function registerNC(){
      setNcLoading(true);
      apiFetch('/plugins/p_plugin/discover/codes/register',{method:'POST',body:{user_id:uid,nickname:nick||uid}})
        .then(function(d){if(d.success){setNcResult({type:'register',data:d});loadMyNC();}})
        .catch(function(){setNcResult({type:'error',msg:'注册失败'});}).finally(function(){setNcLoading(false);});
    }
    function queryNC(){
      var code=ncInput.trim().toUpperCase();if(!code){msg.warning('请输入识别码');return;}
      setNcLoading(true);
      apiFetch('/plugins/p_plugin/discover/codes/query?code='+encodeURIComponent(code))
        .then(function(d){if(d.success&&d.exists){setNcResult({type:'query',data:d});}else{setNcResult({type:'notfound',msg:'未找到识别码（可能已过期）'});}})
        .catch(function(){setNcResult({type:'error',msg:'查询失败'});}).finally(function(){setNcLoading(false);});
    }
    function connectNC(code){
      apiFetch('/plugins/p_plugin/discover/codes/connect',{method:'POST',body:{code:code,connector_id:uid,connector_nick:nick||uid}})
        .then(function(d){if(d.success){msg.success('已连接 '+d.owner_nick);}else{msg.error(d.error||'连接失败');}})
        .catch(function(){msg.error('连接失败');});
    }
    function revokeNC(code){
      apiFetch('/plugins/p_plugin/discover/codes/revoke',{method:'POST',body:{session_code:code,user_id:uid}})
        .then(function(d){if(d.success){msg.success('已撤销');loadMyNC();}})
        .catch(function(){msg.error('撤销失败');});
    }
    function loadMyNC(){
      apiFetch('/plugins/p_plugin/discover/codes/my?user_id='+encodeURIComponent(uid))
        .then(function(d){setNcMyCodes(d.codes||[]);}).catch(function(){});
    }
    function loadDiscoverServices(){
      apiFetch('/plugins/p_plugin/discover/codes/discover')
        .then(function(d){setNcServices(d.services||[]);}).catch(function(){});
    }
    
    function sendMsg(){
      if(!input.trim()||!curRoom||sending)return;
      var content=input;
      var mentions=[];
      var re=/@([\w\u4e00-\u9fff\-]+)/g,m;
      while((m=re.exec(content))!==null){roomAgents.forEach(function(a){if(a.name===m[1]||a.id===m[1])mentions.push(a.id);});}
      
      // 乐观更新：立即显示消息
      var tempMsg={id:'opt_'+Date.now(),room_id:curRoom.id,sender_id:uid,sender_name:nick,content:content,type:'text',mentions:mentions,timestamp:new Date().toISOString()};
      setMsgs(function(p){return[...p,tempMsg];});
      setInput('');setSending(true);
      
      apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/messages',{method:'POST',body:{room_id:curRoom.id,user_id:uid,nickname:nick,content:content,mentions:mentions}})
        .then(function(resp){
          setSending(false);
          // 用服务器返回的真实消息替换乐观消息
          if(resp&&resp.id){setMsgs(function(p){return p.map(function(m){return m.id===tempMsg.id?resp:m;});});}
          else{setMsgs(function(p){return p.filter(function(m){return m.id!==tempMsg.id;});});}
        }).catch(function(err){msg.error('发送失败');setSending(false);
          // 失败时清除乐观消息，避免残留
          setMsgs(function(p){return p.filter(function(m){return m.id!==tempMsg.id;});});
        });
    }
    function createRoom(){if(!newRN.trim())return;
apiFetch('/plugins/p_plugin/rooms/create',{method:'POST',body:{name:newRN.trim(),type:'public',user_id:uid,nickname:nick}})
.then(function(d){msg.success('房间创建成功！');setNewRN('');setShowCreate(false);fetchRooms();if(d&&d.id)setCurRoom(d);})
.catch(function(e){msg.error('创建失败: '+(e&&e.message||'网络错误'));});}
    function addAgent(a){if(!curRoom){msg.warning('请先选择房间');return;}apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/agents/add',{method:'POST',body:{room_id:curRoom.id,user_id:uid,agent:a}}).then(function(d){if(d.success){msg.success('已添加: '+a.name);fetchRooms();apiFetch('/plugins/p_plugin/rooms/'+curRoom.id).then(function(r){setCurRoom(r);setRoomAgents(r.agents||[]);});}}).catch(function(){msg.error('添加失败');});}
    function removeAgent(a){if(!curRoom||!isCreator){msg.warning('只有房主可以移除智能体');return;}apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/agents/remove',{method:'POST',body:{room_id:curRoom.id,user_id:uid,agent_id:a.id}}).then(function(){msg.success('已移除: '+a.name);setRoomAgents(roomAgents.filter(function(x){return x.id!==a.id;}));}).catch(function(e){msg.error(e.message||'移除失败');});}
    function shareRoom(){if(!curRoom)return;setShareLink('');setShareToken('');setSharePassword('');setShareExpiry(0);setShowShare(true);fetchShares();}
    function deleteRoom(){
      if(!curRoom)return;
      if(curRoom.type==='official'){msg.warning('官方聊天室不能删除');return;}
      if(!isCreator){msg.warning('只有房主可以删除房间');return;}
      Modal.confirm({title:'确认删除',content:'确定删除房间「'+curRoom.name+'」？删除后无法恢复，所有消息和文件将被清除。',okText:'确定删除',okType:'danger',cancelText:'取消',
        onOk:function(){
          apiFetch('/plugins/p_plugin/rooms/'+curRoom.id,{method:'DELETE',body:{user_id:uid}})
            .then(function(d){if(d.success){msg.success('已删除: '+d.deleted);setCurRoom(null);fetchRooms();}})
            .catch(function(e){msg.error('删除失败: '+(e&&e.message||'网络错误'));});
        }});
    }
    function fetchShares(){apiFetch('/plugins/p_plugin/shares').then(function(d){setShares(d.shares||[]);}).catch(function(){});}
    function createShareLink(){
      if(!curRoom||shareCreating)return;
      setShareCreating(true);
      apiFetch('/plugins/p_plugin/share/'+curRoom.id,{method:'POST',body:{password:sharePassword,expiry_days:shareExpiry}})
        .then(function(d){
          setShareCreating(false);
          if(d.success){setShareLink(d.share_url);setShareToken(d.token);msg.success('分享链接已生成！');fetchShares();}
          else{msg.error(d.detail||'生成失败');}
        }).catch(function(){setShareCreating(false);msg.error('生成失败');});
    }
    function revokeShare(token){
      apiFetch('/plugins/p_plugin/share/'+token,{method:'DELETE'}).then(function(d){
        if(d.success){msg.success('已撤销: '+d.room_name);fetchShares();}else{msg.error('撤销失败');}
      }).catch(function(){msg.error('撤销失败');});
    }
    function copyShareLink(url){
      var fullUrl = url.indexOf('http')===0 ? url : (window.location.origin + url);
      if(navigator.clipboard){navigator.clipboard.writeText(fullUrl).then(function(){msg.success('已复制！');});}
      else{var ta=document.createElement('textarea');ta.value=fullUrl;document.body.appendChild(ta);ta.select();document.execCommand('copy');document.body.removeChild(ta);msg.success('已复制！');}
    }
    function searchMsgs(){if(!searchQuery.trim()){setSearchResults([]);return;}var q=searchQuery.toLowerCase();setSearchResults(msgs.filter(function(m){return m.content&&m.content.toLowerCase().indexOf(q)>=0;}));}
    
    // ── 文件上传 & 媒体处理 ──
    function fileUploadApi(url, formData) {
      var token = host.getApiToken ? host.getApiToken() : '';
      return fetch(host.getApiUrl(url), {
        method: 'POST',
        headers: token ? { 'Authorization': 'Bearer ' + token } : {},
        body: formData
      }).then(function(r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); });
    }
    
    // 文件上传后端自动创建消息+广播，由 WebSocket 推送真实消息，无需前端乐观更新
    function sendFileMsg(fileData, type) {
      // The upload endpoint (/files/upload, /images/upload) already creates
      // and broadcasts the message. WebSocket will deliver to all clients.
      // No optimistic message needed — avoids duplicates.
      msg.success((type==='image'?'图片':type==='voice'?'语音':type==='video'?'视频':'文件')+'上传成功，等待同步...');
    }
    
    function handleFileUpload(e) {
      var files = e.target&&e.target.files; if(!files||!files.length) return;
      if(!curRoom){msg.warning('请先选择房间');return;}
      for (var i=0;i<files.length;i++){(function(file){
        var fd=new FormData();
        fd.append('file',file);
        fd.append('room_id',curRoom.id);
        fd.append('user_id',uid);
        fd.append('nickname',nick);
        fileUploadApi('/plugins/p_plugin/files/upload',fd).then(function(d){
          if(d.success||d.file_id) sendFileMsg(d,'file');
          else msg.error('上传失败');
        }).catch(function(){msg.error('上传失败');});
      })(files[i]);}
      e.target.value='';
    }
    function handleImageUpload(e) {
      var files=e.target&&e.target.files; if(!files||!files.length) return;
      if(!curRoom){msg.warning('请先选择房间');return;}
      for(var i=0;i<files.length;i++){(function(file){
        var fd=new FormData();
        fd.append('file',file);
        fd.append('room_id',curRoom.id);
        fd.append('user_id',uid);
        fd.append('nickname',nick);
        fileUploadApi('/plugins/p_plugin/files/upload',fd).then(function(d){
          if(d.success||d.file_id) sendFileMsg(d,'image');
          else msg.error('上传失败');
        }).catch(function(){msg.error('上传失败');});
      })(files[i]);}
      e.target.value='';
    }
    function handleVideoUpload(e) {
      var files=e.target&&e.target.files; if(!files||!files.length) return;
      if(!curRoom){msg.warning('请先选择房间');return;}
      for(var i=0;i<files.length;i++){(function(file){
        var fd=new FormData();
        fd.append('file',file);
        fd.append('room_id',curRoom.id);
        fd.append('user_id',uid);
        fd.append('nickname',nick);
        fileUploadApi('/plugins/p_plugin/files/upload',fd).then(function(d){
          if(d.success||d.file_id) sendFileMsg(d,'video');
          else msg.error('上传失败');
        }).catch(function(){msg.error('上传失败');});
      })(files[i]);}
      e.target.value='';
    }
    
    // ── Announcement (公告栏) ──
    function saveAnnouncement(){
      if(!curRoom)return;
      apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/announcement',{method:'PUT',body:{user_id:uid,content:announcementDraft}})
        .then(function(d){if(d.success){setAnnouncement(d.announcement);setEditingAnnouncement(false);msg.success('公告已更新');}})
        .catch(function(e){msg.error('保存失败');});
    }
    
    // ── Game Agent Installation (一键安装游戏智能体) ──
    function installGameAgents(){
      if(!curRoom||installingAgents)return;
      setInstallingAgents(true);
      apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/install-game-agents',{method:'POST',body:{user_id:uid,game_type:'misty_town'}})
        .then(function(d){
          setInstallingAgents(false);
          if(d.success){
            msg.success(d.message||'游戏智能体安装完成');
            // Refresh room data
            fetchRooms();
            apiFetch('/plugins/p_plugin/rooms/'+curRoom.id).then(function(r){
              setCurRoom(r);setRoomAgents(r.agents||[]);
            });
            // Refresh game agents status
            apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/game-agents-status').then(function(s){setGameAgentsStatus(s);}).catch(function(){});
            // Refresh announcement
            apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/announcement').then(function(a){setAnnouncement(a.announcement||'');setShowAnnouncement(!!a.announcement);}).catch(function(){});
          }else{msg.error(d.detail||'安装失败');}
        }).catch(function(){setInstallingAgents(false);msg.error('安装失败');});
    }
    
    // ── Scene System ──
    function changeScene(sceneId){
      if(!curRoom)return;
      apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/scene',{method:'PUT',body:{user_id:uid,scene_id:sceneId}})
        .then(function(d){if(d.success){setCurrentScene(d.scene);setShowSceneSelector(false);msg.success('场景已切换');}})
        .catch(function(){msg.error('切换失败');});
    }
    
    // ── Inventory & Quests ──
    function refreshInventory(){
      if(!curRoom)return;
      apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/inventory/'+uid).then(function(d){
        setInventory({items:d.items||[],clues:d.clues||[],achievements:d.achievements||[]});
      }).catch(function(){});
    }
    function refreshQuests(){
      if(!curRoom)return;
      apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/quests/'+uid).then(function(d){
        setQuests({active:d.active||[],completed:d.completed||[]});
      }).catch(function(){});
    }
    
    var [voiceBusy, setVoiceBusy] = React.useState(false);
    function toggleVoiceRecord() {
      if (recording) {
        // Stop recording
        if (mediaRecRef.current && mediaRecRef.current.state === 'recording') {
          mediaRecRef.current.stop();
        }
        setRecording(false);
      } else {
        // 防连点
        if (voiceBusy) return;
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          msg.warning('浏览器不支持录音'); return;
        }
        setVoiceBusy(true);
        navigator.mediaDevices.getUserMedia({audio:true}).then(function(stream){
          voiceChunksRef.current = [];
          var mr;
          try {
            mr = new MediaRecorder(stream, {mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : 'audio/webm'});
          } catch(ex) {
            mr = new MediaRecorder(stream);
          }
          mediaRecRef.current = mr;
          mr.ondataavailable = function(e) { if (e.data && e.data.size > 0) voiceChunksRef.current.push(e.data); };
          mr.onstop = function() {
            stream.getTracks().forEach(function(t){t.stop();});
            if(!curRoom){msg.warning('请先选择房间');setRecording(false);return;}
            var blob = new Blob(voiceChunksRef.current, {type: mr.mimeType || 'audio/webm'});
            var fd = new FormData();
            fd.append('file', blob, 'voice_' + Date.now() + '.webm');
            fd.append('room_id',curRoom.id);
            fd.append('user_id',uid);
            fd.append('nickname',nick);
            fileUploadApi('/plugins/p_plugin/files/upload', fd).then(function(d){
              if(d.success||d.file_id) sendFileMsg(d,'voice');
              else msg.error('上传失败');
            }).catch(function(){msg.error('录音上传失败');});
          };
          mr.start();
          setRecording(true);
          setVoiceBusy(false);
        }).catch(function(){msg.warning('无法访问麦克风');setVoiceBusy(false);});
      }
    }
    
    function sendLocation() {
      if (!navigator.geolocation) { msg.warning('浏览器不支持定位'); return; }
      if (locating || sending||!curRoom) return;  // 防重复
      setLocating(true);
      msg.loading('正在获取位置...', 0);
      navigator.geolocation.getCurrentPosition(function(pos){
        msg.destroy();setLocating(false);
        var lat=pos.coords.latitude, lng=pos.coords.longitude;
        var content='📍 位置: ['+lat.toFixed(6)+','+lng.toFixed(6)+']';
        var tempMsg={id:'opt_'+Date.now(),room_id:curRoom.id,sender_id:uid,sender_name:nick,
          content:content,type:'location',latitude:lat,longitude:lng,timestamp:new Date().toISOString()};
        setMsgs(function(p){return[...p,tempMsg];});
        apiFetch('/plugins/p_plugin/rooms/'+curRoom.id+'/messages',{
          method:'POST',
          body:{room_id:curRoom.id,user_id:uid,nickname:nick,content:content,type:'location',latitude:lat,longitude:lng}
        }).then(function(resp){
          if(resp&&resp.id){setMsgs(function(p){return p.map(function(m){return m.id===tempMsg.id?resp:m;});});}
          else{setMsgs(function(p){return p.filter(function(m){return m.id!==tempMsg.id;});});}
        }).catch(function(){msg.error('发送失败');setMsgs(function(p){return p.filter(function(m){return m.id!==tempMsg.id;});});});
      },function(){msg.destroy();setLocating(false);msg.error('无法获取位置');},{enableHighAccuracy:true,timeout:10000});
    }
    
    function handleInputChange(e){
      var v=e.target.value;setInput(v);
      var at=v.lastIndexOf('@');
      if(at>=0){var q=v.substring(at+1);if(!q.includes(' ')){setMentionQuery(q);setShowMention(true);setMentionIndex(0);}else{setShowMention(false);}}
      else{setShowMention(false);}
    }
    function handleKeyDown(e){
      if(showMention){
        // 计算所有可选项（智能体+用户）
        var filteredAgents = roomAgents.filter(function(a){return a.name.toLowerCase().indexOf(mentionQuery.toLowerCase())>=0;});
        var filteredUsers = roomUsers.filter(function(u){return u.name.toLowerCase().indexOf(mentionQuery.toLowerCase())>=0;});
        var totalItems = filteredAgents.length + filteredUsers.length;
        if(totalItems === 0) return;
        
        if(e.key==='ArrowDown'){e.preventDefault();setMentionIndex((mentionIndex+1)%totalItems);}
        else if(e.key==='ArrowUp'){e.preventDefault();setMentionIndex((mentionIndex-1+totalItems)%totalItems);}
        else if(e.key==='Enter'){
          e.preventDefault();
          var selectedItem;
          if(mentionIndex < filteredAgents.length) {
            selectedItem = {data: filteredAgents[mentionIndex], isAgent: true};
          } else {
            selectedItem = {data: filteredUsers[mentionIndex - filteredAgents.length], isAgent: false};
          }
          if(selectedItem && selectedItem.data) {
            var at=input.lastIndexOf('@');
            setInput(input.substring(0,at)+'@'+selectedItem.data.name+' ');
            setShowMention(false);
          }
        }
        else if(e.key==='Escape'){setShowMention(false);}
      }
    }
    
    var [unread, setUnread] = React.useState(function(){
      try{return JSON.parse(localStorage.getItem('p_plugin_unread')||'{}');}catch(e){return {};}
    });
    function saveUnread(u){localStorage.setItem('p_plugin_unread',JSON.stringify(u));}
    function incUnread(roomId){
      if(curRoom&&curRoom.id===roomId)return;
      setUnread(function(prev){var next={...prev};next[roomId]=(next[roomId]||0)+1;saveUnread(next);return next;});
    }
    function clearUnread(roomId){
      setUnread(function(prev){var next={...prev};next[roomId]=0;saveUnread(next);return next;});
    }
    // 通讯录
    var [addrBook, setAddrBook] = React.useState(function(){try{return JSON.parse(localStorage.getItem('p_plugin_addrbook')||'[]');}catch(e){return[];}});
    var [showAddrBook, setShowAddrBook] = React.useState(false);
    var [addrName, setAddrName] = React.useState('');
    var [addrPhone, setAddrPhone] = React.useState('');
    var [addrNote, setAddrNote] = React.useState('');
    var [addrType, setAddrType] = React.useState('friend');
    function saveAddrBook(a){localStorage.setItem('p_plugin_addrbook',JSON.stringify(a));setAddrBook(a);}
    function addContact(){if(!addrName.trim())return;var entry={name:addrName.trim(),phone:addrPhone.trim(),note:addrNote.trim(),type:addrType,addedAt:new Date().toISOString()};saveAddrBook([...addrBook,entry]);setAddrName('');setAddrPhone('');setAddrNote('');setAddrType('friend');}
    function delContact(idx){saveAddrBook(addrBook.filter(function(_,i){return i!==idx;}));}
    // 分享房间记录到通讯录
    function addSharedRoomToAddr(roomName,roomId){
      if(!roomName)return;
      var url='/api/plugins/p_plugin/web/'+roomId;
      var exists=addrBook.some(function(e){return e.note===roomId&&e.type==='room';});
      if(exists){msg.info('已在通讯录中');return;}
      saveAddrBook([...addrBook,{name:roomName,phone:'',note:roomId,type:'room',link:url,addedAt:new Date().toISOString()}]);
      msg.success('已加入通讯录');
    }
    
    var isConn = wsStatus==='connected';
    var sc = isConn?'#07C160':'#FF4D4F';
    
    return h('div',{style:{height:'100%',display:'flex',background:C.bg,fontFamily:'-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif'}},[
      // 侧边栏
      h('div',{style:{width:280,background:C.sidebar,borderRight:'1px solid '+C.border,display:'flex',flexDirection:'column',flexShrink:0}},[
        h('div',{style:{padding:'14px 16px',background:C.header,display:'flex',justifyContent:'space-between',alignItems:'center'}},[
          h('span',{style:{color:'#FFF',fontSize:18,fontWeight:700}},'P 群聊'),
          h('div',{style:{display:'flex',gap:8}},[
            h('span',{style:{color:'#FFF',cursor:'pointer',fontSize:22,lineHeight:'22px'},onClick:function(){setShowCreate(true);}},'+'),
            onBack?h('span',{style:{color:'#FFF',cursor:'pointer',fontSize:18},onClick:onBack},'←'):null
          ])
        ]),
        h('div',{style:{padding:'10px 16px',background:'#F7F7F7',borderBottom:'1px solid '+C.border,display:'flex',alignItems:'center',gap:10}},[
          h(Avatar,{size:30,style:{background:C.primary,flexShrink:0}},nick.charAt(0)),
          h('span',{style:{fontSize:14,fontWeight:500,flex:1}},nick),
          h('span',{style:{fontSize:11,color:'#999',cursor:'pointer'},onClick:function(){setShowSettings(true);}},'⚙️')
        ]),
        h('div',{style:{flex:1,overflow:'auto'}},
          rooms.length===0?h('div',{style:{padding:40,textAlign:'center',color:C.sec}},'暂无房间，点击 + 创建'):
          rooms.map(function(r){
            var active=curRoom&&curRoom.id===r.id;
            var uc=unread[r.id]||0;
            return h('div',{key:r.id,style:{display:'flex',alignItems:'center',padding:'12px 16px',background:active?'#E8E8E8':C.card,borderBottom:'1px solid '+C.border,cursor:'pointer'},
              onClick:function(){setCurRoom(r);clearUnread(r.id);}},
              [h('div',{style:{position:'relative',flexShrink:0,marginRight:12}},
                [h(Avatar,{size:44,style:{background:r.type==='official'?C.primary:'#10AEFF'}},r.name.charAt(0)),
                 uc>0?h('span',{style:{position:'absolute',top:-2,right:-2,width:16,height:16,borderRadius:'50%',background:'#FF4D4F',border:'2px solid #fff',display:'flex',alignItems:'center',justifyContent:'center',fontSize:10,color:'#fff',fontWeight:700,lineHeight:1}},uc>99?'99+':uc):null]),
              h('div',{style:{flex:1,overflow:'hidden'}},[h('div',{style:{fontSize:15,fontWeight:600,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}},r.name),
              h('div',{style:{fontSize:12,color:C.sec,marginTop:2}},(r.agents||[]).length+' 个智能体 · '+(r.type==='official'?'官方':'自定义'))])]);
          })),
        // 通讯录
        h('div',{style:{padding:'8px 16px',borderTop:'1px solid '+C.border,display:'flex',alignItems:'center',gap:8,cursor:'pointer',fontSize:12,color:'#333'},onClick:function(){setShowAddrBook(true);}},[
          h('span',{style:{fontSize:16}},'📞'),
          h('span',{style:{flex:1}},'通讯录'),
          h('span',{style:{fontSize:12,color:C.sec}},addrBook.length+' 条 →')
        ]),
        // 频道接入
        h('div',{style:{padding:'8px 16px',borderTop:'1px solid '+C.border,display:'flex',alignItems:'center',gap:8,cursor:'pointer',fontSize:12,color:'#576B95'},onClick:function(){setShowWeChat(true);}},[
          h('span',{style:{fontSize:16}},'🌐'),
          h('span',{style:{flex:1}},'频道接入'),
          h('span',{style:{fontSize:12,color:C.sec}},'→')
        ]),
        // 连接状态
        h('div',{style:{padding:'10px 16px',borderTop:'1px solid '+C.border,fontSize:11,display:'flex',alignItems:'center',gap:8}},[
          h('span',{style:{width:10,height:10,borderRadius:5,background:isConn?'#07C160':'#FF4D4F',display:'inline-block',flexShrink:0,boxShadow:isConn?'0 0 6px #07C160':'0 0 6px #FF4D4F'}}),
          h('span',{style:{fontWeight:700,color:isConn?'#07C160':'#FF4D4F',fontSize:12}},isConn?'ON':'OFF'),
          h('span',{style:{color:C.sec,marginLeft:4}},isConn?'WebSocket 已连接':'WebSocket 未连接')
        ])
      ]),
      // 主聊天区
      h('div',{style:{flex:1,display:'flex',flexDirection:'column'}},curRoom?[
        // ── Panel tab bar (Tailchat-style) ──
        h('div',{style:{padding:'6px 12px',background:C.card,borderBottom:'1px solid '+C.border,display:'flex',alignItems:'center',gap:4,overflow:'auto',minHeight:44}},
          roomPanels.map(function(p){
            var active=curPanel&&curPanel.id===p.id;
            var shortName=p.name.replace(/[^\x00-\x7f]/g,'').substring(0,8)||p.name;
            return h('div',{key:p.id,title:p.name+(p.url?'\n'+p.url:''),
              style:{display:'flex',alignItems:'center',gap:4,padding:'6px 12px',borderRadius:20,background:active?C.primary:'#f5f5f5',color:active?'#fff':'#333',cursor:'pointer',fontSize:13,whiteSpace:'nowrap',flexShrink:0,transition:'all 0.2s',border:active?'2px solid '+C.primary:'2px solid transparent'},
              onClick:function(){setCurPanel(p);}},
              h('span',{style:{fontSize:15}},p.icon||'💬'),
              h('span',{},shortName));
          }),
          h('div',{style:{display:'flex',alignItems:'center',padding:'6px 10px',borderRadius:20,border:'2px dashed #d9d9d9',color:'#999',cursor:'pointer',fontSize:18,marginLeft:4,flexShrink:0},onClick:function(){setNewPanelUrl('');setNewPanelName('');setShowAddPanel(true);}},'+'),
          curPanel&&curPanel.type!=='chat'?h(Button,{size:'small',danger:true,style:{fontSize:11,padding:'2px 8px',marginLeft:4,flexShrink:0},onClick:function(){removePanel(curPanel);}},'🗑️'):null
        ),
        // ── Panel content ──
        curPanel&&curPanel.type==='webview'?
          h('div',{style:{flex:1,display:'flex',flexDirection:'column',background:'#fff'}},[
            h('div',{style:{padding:'6px 12px',background:'#f5f5f5',borderBottom:'1px solid #eee',display:'flex',alignItems:'center',gap:8,fontSize:12}},[
              h('span',{style:{color:'#07C160',fontWeight:600}},'🌐'),
              h('span',{style:{color:'#666',flex:1,wordBreak:'break-all'}},curPanel.url||''),
              h(Button,{size:'small',type:'link',onClick:function(){window.open(curPanel.url||'','_blank');}},'↗️ New Window')
            ]),
            h('iframe',{src:curPanel.url||'',style:{flex:1,border:'none',width:'100%',height:'100%'},sandbox:'allow-scripts allow-same-origin allow-forms allow-popups',title:curPanel.name})
          ]):
        curPanel&&curPanel.type==='custom'?
          h('div',{style:{flex:1,overflow:'auto',padding:'16px',background:'#f5f5f5'}},
            // Render the custom HTML content
            h('div',{dangerouslySetInnerHTML:{__html: curPanel.html || ''}})
          ):
        [
        h('div',{style:{padding:'10px 16px',background:C.card,borderBottom:'1px solid '+C.border,display:'flex',justifyContent:'space-between',alignItems:'center'}},[
          h('div',{style:{display:'flex',alignItems:'center',gap:10}},[
            h('span',{style:{fontSize:17,fontWeight:700}},curRoom.name),
            h(Tag,{color:curRoom.type==='official'?'green':'blue'},curRoom.type==='official'?'官方':'自定义'),
            isCreator?h(Tag,{color:'gold'},'👑 房主'):h(Tag,{},'成员'),
            h('span',{style:{fontSize:12,color:C.sec}},roomAgents.length+' 个智能体'),
            // 当前场景显示（所有用户可点击查看，只有房主可切换）
            currentScene?h(Tag,{color:'purple',style:{cursor:'pointer'},onClick:function(){setShowSceneSelector(true);}},currentScene.icon+' '+currentScene.name):null
          ]),
          h('div',{style:{display:'flex',gap:6}},[
            // 道具背包按钮
            h(Button,{size:'small',onClick:function(){setShowInventory(true);}},'🎒 背包('+(inventory.items.length+inventory.clues.length)+')'),
            // 任务按钮
            h(Button,{size:'small',onClick:function(){setShowQuests(true);}},'📜 任务('+quests.active.length+')'),
            h(Button,{size:'small',onClick:function(){setShowSearch(true);}},'🔍 搜索'),
            h(Button,{size:'small',onClick:shareRoom},'🔗 分享'),
            isCreator&&curRoom.type!=='official'?h(Button,{size:'small',danger:true,onClick:deleteRoom},'🗑️ 删除'):null,
            h(Button,{size:'small',type:'primary',style:{background:C.primary},onClick:function(){setShowAgentModal(true);}},'➕ 管理智能体 ('+roomAgents.length+')')
          ])
        ]),
        // ── 公告栏 (Announcement Bar) ──
        announcement&&!editingAnnouncement?h('div',{style:{background:theme==='dark'?'#1a1a2e':'#fffbe6',borderBottom:'1px solid '+(theme==='dark'?'#333':'#ffe58f'),padding:'8px 16px',display:'flex',alignItems:'flex-start',gap:8}},[
          h('span',{style:{fontSize:16,flexShrink:0,marginTop:2}},'📌'),
          h('div',{style:{flex:1,fontSize:13,color:theme==='dark'?'#ddd':'#8c6900',lineHeight:'1.6',whiteSpace:'pre-wrap',maxHeight:120,overflow:'auto'}},announcement),
          h('div',{style:{display:'flex',gap:4,flexShrink:0}},[
            isCreator?h(Button,{size:'small',style:{fontSize:11},onClick:function(){setAnnouncementDraft(announcement);setEditingAnnouncement(true);}},'✏️'):null,
            h(Button,{size:'small',style:{fontSize:11},onClick:function(){setShowAnnouncement(false);}},'✕')
          ])
        ]):null,
        // ── 公告编辑模式 ──
        editingAnnouncement?h('div',{style:{background:theme==='dark'?'#1a1a2e':'#fffbe6',borderBottom:'1px solid '+(theme==='dark'?'#333':'#ffe58f'),padding:'12px 16px'}},[
          h('div',{style:{fontSize:13,fontWeight:600,marginBottom:8,color:theme==='dark'?'#ddd':'#8c6900'}},'📝 编辑公告'),
          h(Input.TextArea,{value:announcementDraft,onChange:function(e){setAnnouncementDraft(e.target.value);},autoSize:{minRows:2,maxRows:6},style:{marginBottom:8},placeholder:'输入公告内容...'}),
          h('div',{style:{display:'flex',gap:6}},[
            h(Button,{size:'small',type:'primary',onClick:saveAnnouncement},'💾 保存'),
            h(Button,{size:'small',onClick:function(){setEditingAnnouncement(false);}},'取消')
          ])
        ]):null,
        // ── 一键安装游戏智能体 (当房间无智能体且有游戏模板时) ──
        curRoom&&roomAgents.length===0&&gameAgentsStatus&&!gameAgentsStatus.all_installed?h('div',{style:{background:theme==='dark'?'#1a2332':'#e6f7ff',borderBottom:'1px solid '+(theme==='dark'?'#333':'#91d5ff'),padding:'12px 16px',display:'flex',alignItems:'center',gap:12}},[
          h('span',{style:{fontSize:28}},'🎮'),
          h('div',{style:{flex:1}},[
            h('div',{style:{fontSize:14,fontWeight:600,color:theme==='dark'?'#fff':'#0050b3'}},'安装游戏智能体'),
            h('div',{style:{fontSize:12,color:theme==='dark'?'#aaa':'#333'}},'此房间还没有智能体。一键安装 AI 角色，开始互动游戏！')
          ]),
          h(Button,{type:'primary',loading:installingAgents,onClick:installGameAgents,style:{background:'#FF6B6B',borderColor:'#FF6B6B',flexShrink:0}},'🚀 一键安装')
        ]):null,
        h('div',{style:{flex:1,overflow:'auto',padding:'12px 0'}},
          msgs.length===0&&agentTyping.length===0?
          h('div',{style:{height:'100%',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',color:C.sec}},[
            h('div',{style:{fontSize:48,marginBottom:12}},'💬'),
            h('div',{style:{fontSize:16}},'选择一个房间开始聊天')
          ]):
          msgs.map(function(msg){
            if(msg.type==='system') return h('div',{key:msg.id,style:{textAlign:'center',margin:'12px 0'}},h(Tag,{},msg.content));
            var isMe=msg.sender_id===uid;
            var isAgent=roomAgents.some(function(a){return a.id===msg.sender_id;});
            var agent=roomAgents.find(function(a){return a.id===msg.sender_id;});
            var isFile=msg.type==='file'||msg.file_id;
            var isImage=msg.type==='image'||(msg.file_id&&msg.file_name&&(msg.file_name.match(/\.(png|jpg|jpeg|gif|webp|svg|bmp)$/i)));
            return h('div',{key:msg.id,style:{display:'flex',flexDirection:isMe?'row-reverse':'row',marginBottom:14,padding:'0 16px'}},[
              h(Avatar,{size:34,style:{background:isAgent?(agent&&agent.color||'#10AEFF'):(isMe?C.primary:'#95EC69'),margin:isMe?'0 0 0 10px':'0 10px 0 0',flexShrink:0}},isAgent?(agent&&agent.icon||'🤖'):msg.sender_name.charAt(0)),
              h('div',{style:{maxWidth:'70%'}},[
                h('div',{style:{fontSize:11,color:C.sec,marginBottom:4,display:'flex',alignItems:'center',gap:6,flexDirection:isMe?'row-reverse':'row'}},[
                  h('span',{style:{fontWeight:500}},msg.sender_name),
                  isAgent?h(Tag,{color:'blue',style:{fontSize:10,padding:'0 4px',lineHeight:'16px'}},'AI'):null,
                  h('span',{},new Date(msg.timestamp).toLocaleTimeString())
                ]),
                isImage?h('div',{style:{padding:'8px 12px',background:isMe?C.bm:C.bo,borderRadius:12}},[
                  h('div',{style:{fontSize:14,marginBottom:8}},msg.content||'🖼️ 图片'),
                  h('img',{src:'/api/plugins/p_plugin/files/'+msg.file_id+'/preview',style:{maxWidth:'100%',maxHeight:300,borderRadius:8,cursor:'pointer'},onClick:function(){window.open('/api/plugins/p_plugin/files/'+msg.file_id+'/download','_blank');}})
                ]):isFile?h('div',{style:{padding:'8px 12px',background:isMe?C.bm:C.bo,borderRadius:12}},[
                  h('div',{style:{fontSize:14,marginBottom:6}},msg.content||'📎 文件'),
                  h('div',{style:{display:'flex',gap:6,alignItems:'center'}},[
                    h('span',{style:{fontSize:12,color:C.sec,wordBreak:'break-all'}},msg.file_name||'文件'),
                    msg.file_size?h('span',{style:{fontSize:11,color:C.sec}},msg.file_size>1024?Math.round(msg.file_size/1024)+'KB':msg.file_size+'B'):null,
                    h(Button,{size:'small',type:'link',style:{padding:'0 4px',fontSize:12},onClick:function(){window.open('/api/plugins/p_plugin/files/'+msg.file_id+'/download','_blank');}},'⬇️ 下载')
                  ])
                ]):h('div',{style:{padding:'8px 12px',background:isMe?C.bm:C.bo,borderRadius:12,color:isMe?'#000':C.text,fontSize:14,lineHeight:1.5,wordBreak:'break-word'}},msg.content)
              ])
            ]);
          }),
          h('div',{ref:msgsEndRef})
        ),
        // 输入区
        h('div',{style:{padding:'10px 16px',background:C.card,borderTop:'1px solid '+C.border,position:'relative'}},[
          agentTyping.length>0?h('div',{style:{fontSize:12,color:C.sec,marginBottom:6}},'🤖 '+agentTyping.join(', ')+' 正在输入...'):null,
          h('div',{style:{display:'flex',gap:8,position:'relative'}},[
            h(Popover,{content:h(EmojiPicker,{onSelect:function(e){setInput(input+e);setShowEmoji(false);}}),trigger:'click',open:showEmoji,onOpenChange:setShowEmoji},
              h(Button,{size:'small',style:{border:'none',fontSize:18,flexShrink:0}},'😀')),
            h(Input.TextArea,{value:input,onChange:handleInputChange,onKeyDown:handleKeyDown,
              onPressEnter:function(e){if(!e.shiftKey){e.preventDefault();sendMsg();}},
              placeholder:'输入消息，@提及智能体...',autoSize:{minRows:1,maxRows:4},style:{flex:1}}),
            h(Button,{type:'primary',style:{background:C.primary,flexShrink:0},loading:sending,onClick:sendMsg},'发送'),
            showMention&&(roomAgents.length>0||roomUsers.length>0)?h(MentionDropdown,{agents:roomAgents,users:roomUsers,query:mentionQuery,sel:mentionIndex,onSelect:function(data,isAgent){var at=input.lastIndexOf('@');setInput(input.substring(0,at)+'@'+data.name+' ');setShowMention(false);}}):null
          ]),
          // ── 工具栏：文件、图片、拍照、语音、视频、位置 ──
          h('div',{style:{display:'flex',gap:2,marginTop:6,flexWrap:'wrap'}},[
            h(Button,{size:'small',type:'text',style:{fontSize:12,padding:'2px 8px',color:C.sec,borderRadius:4},title:'发送文件',onClick:function(){try{document.getElementById('p_file_input').click();}catch(e){}}},h('span',{style:{fontSize:13,marginRight:2}},'📎'),'文件'),
            h(Button,{size:'small',type:'text',style:{fontSize:12,padding:'2px 8px',color:C.sec,borderRadius:4},title:'发送图片',onClick:function(){try{document.getElementById('p_img_input').click();}catch(e){}}},h('span',{style:{fontSize:13,marginRight:2}},'🖼️'),'图片'),
            h(Button,{size:'small',type:'text',style:{fontSize:12,padding:'2px 8px',color:C.sec,borderRadius:4},title:'拍照',onClick:function(){try{document.getElementById('p_cam_input').click();}catch(e){}}},h('span',{style:{fontSize:13,marginRight:2}},'📷'),'拍照'),
            h(Button,{size:'small',type:'text',style:{fontSize:12,padding:'2px 8px',color:recording?'#FF4D4F':C.sec,borderRadius:4},title:'语音消息',onClick:toggleVoiceRecord},h('span',{style:{fontSize:13,marginRight:2}},recording?'🔴':'🎤'),recording?'录音中...':'语音'),
            h(Button,{size:'small',type:'text',style:{fontSize:12,padding:'2px 8px',color:C.sec,borderRadius:4},title:'发送视频',onClick:function(){try{document.getElementById('p_vid_input').click();}catch(e){}}},h('span',{style:{fontSize:13,marginRight:2}},'📹'),'视频'),
            h(Button,{size:'small',type:'text',style:{fontSize:12,padding:'2px 8px',color:C.sec,borderRadius:4},title:'发送位置',onClick:sendLocation},h('span',{style:{fontSize:13,marginRight:2}},'📍'),'位置'),
            // 隐藏的文件输入
            h('input',{id:'p_file_input',type:'file',multiple:'multiple',style:{display:'none'},onChange:handleFileUpload}),
            h('input',{id:'p_img_input',type:'file',accept:'image/*',multiple:'multiple',style:{display:'none'},onChange:handleImageUpload}),
            h('input',{id:'p_cam_input',type:'file',accept:'image/*',capture:'camera',style:{display:'none'},onChange:handleImageUpload}),
            h('input',{id:'p_vid_input',type:'file',accept:'video/*',style:{display:'none'},onChange:handleVideoUpload})
          ])
        ])
      ]
      ]:[h('div',{style:{flex:1,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',color:C.sec}},[
        h('div',{style:{fontSize:56,marginBottom:16}},'💬'),
        h('div',{style:{fontSize:18,fontWeight:600,marginBottom:8}},'P 群聊'),
        h('div',{style:{fontSize:14}},'选择或创建一个房间开始聊天')
      ])]),
      // 智能体管理弹窗
      h(Modal,{title:null,open:showAgentModal,onCancel:function(){setShowAgentModal(false);},footer:null,width:560,bodyStyle:{padding:20}},[
        h('div',{style:{marginBottom:16}},[h('div',{style:{fontSize:16,fontWeight:600,marginBottom:8}},'当前智能体'),roomAgents.length===0?h('div',{style:{color:'#999',padding:'8px 0'}},'暂无智能体'):roomAgents.map(function(a){return h('div',{key:a.id,style:{display:'flex',alignItems:'center',padding:'8px 12px',background:'#fafafa',borderRadius:8,marginBottom:6}},[h('div',{style:{width:32,height:32,borderRadius:'50%',background:a.color||'#07C160',display:'flex',alignItems:'center',justifyContent:'center',fontSize:16,color:'white',marginRight:10}},a.icon||'🤖'),h('div',{style:{flex:1}},[h('div',{style:{fontSize:14,fontWeight:500}},a.name),h('div',{style:{fontSize:11,color:'#999'}},a.id)]),isCreator?h(Button,{size:'small',danger:true,onClick:function(){removeAgent(a);}},'移除'):null]);})]),
        h('div',{style:{borderTop:'1px solid #eee',paddingTop:16,marginBottom:8}},[h('div',{style:{fontSize:16,fontWeight:600,marginBottom:12}},'添加智能体'),h(AgentSelector,{roomAgents:roomAgents,onAdd:addAgent})])
      ]),
      // 创建房间弹窗
      h(Modal,{title:'创建房间',open:showCreate,onOk:createRoom,onCancel:function(){setShowCreate(false);}},[
        h('div',{style:{marginBottom:16}},[h('label',{},'房间名称'),h(Input,{value:newRN,onChange:function(e){setNewRN(e.target.value);},placeholder:'输入房间名称'})]),
        h('div',{},[h('label',{},'密码（可选）'),h(Input.Password,{})])
      ]),
      // 搜索弹窗
      h(Modal,{title:'搜索消息',open:showSearch,onCancel:function(){setShowSearch(false);},footer:null,width:600},[
        h('div',{style:{display:'flex',gap:8,marginBottom:16}},[h(Input,{value:searchQuery,onChange:function(e){setSearchQuery(e.target.value);},onPressEnter:searchMsgs,placeholder:'搜索消息...',prefix:'🔍',allowClear:true,style:{flex:1}}),h(Button,{type:'primary',onClick:searchMsgs},'搜索')]),
        searchResults.length>0?searchResults.map(function(m){return h('div',{key:m.id,style:{padding:'10px 12px',cursor:'pointer',borderBottom:'1px solid #f0f0f0'},onClick:function(){setShowSearch(false);}},[h('div',{style:{fontSize:12,color:'#666',marginBottom:4,display:'flex',justifyContent:'space-between'}},[h('span',{},m.sender_name),h('span',{},new Date(m.timestamp).toLocaleString())]),h('div',{style:{fontSize:14}},m.content)]);}):searchQuery?h('div',{style:{textAlign:'center',padding:20,color:'#999'}},'未找到结果'):null
      ]),
      // 频道接入弹窗
      h(Modal,{title:null,open:showWeChat,onCancel:function(){setShowWeChat(false);},footer:null,width:520,bodyStyle:{padding:24}},[
        h('div',{style:{textAlign:'center',marginBottom:20}},[
          h('div',{style:{fontSize:40,marginBottom:8}},'🌐'),
          h('div',{style:{fontSize:18,fontWeight:700}},'频道接入'),
          h('div',{style:{fontSize:13,color:'#999',marginTop:4}},'P 插件通过官方聊天室实现 AI 群聊，支持自由管理智能体')
        ]),
        h('div',{style:{background:'#f6ffed',border:'1px solid #b7eb8f',borderRadius:8,padding:14,marginBottom:12}},[
          h('div',{style:{fontSize:14,color:'#389e0d',fontWeight:600,marginBottom:6}},'✅ 当前接入方式：官方聊天室'),
          h('div',{style:{fontSize:12,color:'#666',lineHeight:1.8}},'系统启动时自动创建，包含全部本地智能体。你可以自由增减智能体、删除房间。')
        ]),
        // ── P-Chat Agent 安装 ──
        h('div',{style:{background:pchatStatus.installed?'#e6f7ff':'#fff2e8',borderRadius:8,padding:14,marginBottom:12,border:'1px solid '+(pchatStatus.installed?'#91d5ff':'#ffd591')}},[
          h('div',{style:{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:8}},[
            h('div',{style:{fontSize:14,fontWeight:600,color:pchatStatus.installed?'#1890ff':'#fa8c16'}},'🤖 P-Chat 群聊助手'),
            pchatStatus.installed?h(Tag,{color:'blue'},'已安装'):h(Tag,{color:'orange'},'未安装')
          ]),
          h('div',{style:{fontSize:12,color:'#666',lineHeight:1.8,marginBottom:10}},
            'P-Chat 是 P 插件的专用群聊智能体。安装后它会自动加入官方聊天室，并可绑定到微信/钉钉/飞书等频道实现跨平台 AI 群聊。'),
          pchatStatus.installed?[
            pchatStatus.in_official_room?h('div',{style:{fontSize:12,color:'#52c41a',marginBottom:10}},'✅ 已在官方聊天室中'):
            h('div',{style:{fontSize:12,color:'#faad14',marginBottom:10}},'⚠️ 未在官方聊天室中（请手动添加或重启 P 插件）'),
            h('div',{style:{display:'flex',gap:8}},[
              h(Button,{size:'small',type:'primary',ghost:true,onClick:function(){setPchatStatus(function(ps){return{...ps,loading:true};});
                apiFetch('/plugins/p_plugin/agents/pchat/install').then(function(d){
                  setPchatStatus({installed:true,in_official_room:true,loading:false});
                  if(d.status==='already_installed') msg.info('P-Chat 已安装！');
                  else msg.success(d.message||'安装成功！');
                }).catch(function(){setPchatStatus(function(ps){return{...ps,loading:false};});msg.error('操作失败');});}},
                '🔄 重新安装 / 加入房间'),
              h(Button,{size:'small',danger:true,ghost:true,onClick:function(){
                Modal.confirm({title:'卸载确认',content:'确定卸载 P-Chat 群聊助手？卸载后需重新安装。',okText:'确定卸载',okType:'danger',cancelText:'取消',
                  onOk:function(){setPchatStatus(function(ps){return{...ps,loading:true};});
                    apiFetch('/plugins/p_plugin/agents/pchat/uninstall',{method:'DELETE'}).then(function(d){
                      setPchatStatus({installed:false,in_official_room:false,loading:false});
                      msg.success(d.message||'已卸载');
                    }).catch(function(){setPchatStatus(function(ps){return{...ps,loading:false};});msg.error('卸载失败');});
                  }});}},
                '🗑️ 卸载')
            ])
          ]:h(Button,{type:'primary',loading:pchatStatus.loading,onClick:function(){
            setPchatStatus(function(ps){return{...ps,loading:true};});
            apiFetch('/plugins/p_plugin/agents/pchat/install',{method:'POST'}).then(function(d){
              setPchatStatus({installed:true,in_official_room:true,loading:false});
              msg.success(d.message||'安装成功！');
              // Refresh rooms to show P-Chat in official room
              fetchRooms();
            }).catch(function(e){setPchatStatus(function(ps){return{...ps,loading:false};});msg.error('安装失败: '+(e&&e.message||'网络错误'));});
          }},'🚀 一键安装 P-Chat 群聊助手')
        ]),
        h('div',{style:{background:'#ede9fe',borderRadius:8,padding:14,marginBottom:12}},[
          h('div',{style:{fontSize:12,color:'#7c3aed',fontWeight:500,marginBottom:8}},'🏗️ 四层群聊架构（供后续扩展频道）'),
          h('div',{style:{fontSize:12,color:'#555',lineHeight:2.0}},[
            h('div',{style:{display:'flex',alignItems:'flex-start',gap:6,marginBottom:4}},[
              h('span',{style:{background:'#7c3aed',color:'#fff',borderRadius:10,width:18,height:18,fontSize:10,display:'inline-flex',alignItems:'center',justifyContent:'center',flexShrink:0}},'1'),
              h('div',null,[h('b',null,'Channel Driver'),' — 频道驱动层。QwenPaw 内置的频道适配器（微信/钉钉/飞书/QQ/Telegram），负责接收外部平台消息并转发给智能体。'])
            ]),
            h('div',{style:{display:'flex',alignItems:'flex-start',gap:6,marginBottom:4}},[
              h('span',{style:{background:'#7c3aed',color:'#fff',borderRadius:10,width:18,height:18,fontSize:10,display:'inline-flex',alignItems:'center',justifyContent:'center',flexShrink:0}},'2'),
              h('div',null,[h('b',null,'Agent Binding'),' — 智能体绑定。在 Control → Channels 中为该频道指定一个或多个智能体，所有频道消息会自动 @ 到这个智能体。'])
            ]),
            h('div',{style:{display:'flex',alignItems:'flex-start',gap:6,marginBottom:4}},[
              h('span',{style:{background:'#7c3aed',color:'#fff',borderRadius:10,width:18,height:18,fontSize:10,display:'inline-flex',alignItems:'center',justifyContent:'center',flexShrink:0}},'3'),
              h('div',null,[h('b',null,'P-Chat Agent'),' — 群聊助手智能体。这是 P 插件注册的"P-Chat"智能体，负责解析群聊指令（创建房间/加入房间/发送消息/@提及）、管理群聊上下文。'])
            ]),
            h('div',{style:{display:'flex',alignItems:'flex-start',gap:6,marginBottom:0}},[
              h('span',{style:{background:'#7c3aed',color:'#fff',borderRadius:10,width:18,height:18,fontSize:10,display:'inline-flex',alignItems:'center',justifyContent:'center',flexShrink:0}},'4'),
              h('div',null,[h('b',null,'P Plugin Backend'),' — P 插件后端。提供群聊 API（房间管理/消息存储/WebSocket 广播），将智能体回复广播到所有在线成员。'])
            ])
          ]),
          h('div',{style:{borderTop:'1px solid #ddd6fe',marginTop:10,paddingTop:8,fontSize:11,color:'#7c3aed',lineHeight:1.6}},'🔁 消息流程：用户在微信发言 → Driver 接收 → Agent Binding 路由 → P-Chat 智能体处理 → P 插件 API 广播 → 所有成员实时收到回复')
        ]),
        h('div',{style:{background:'#fffbe6',borderRadius:8,padding:14}},[
          h('div',{style:{fontSize:12,color:'#d48806',fontWeight:500,marginBottom:6}},'💡 未来扩展更多频道时的配置步骤'),
          h('div',{style:{fontSize:12,color:'#666',lineHeight:1.8}},'1️⃣ 前往 QwenPaw → 控制台 → Control → Channels'),
          h('div',{style:{fontSize:12,color:'#666',lineHeight:1.8}},'2️⃣ 选择要接入的频道（微信/钉钉/飞书等），填写配置'),
          h('div',{style:{fontSize:12,color:'#666',lineHeight:1.8}},'3️⃣ 在该频道配置中绑定智能体，选择"P-Chat 群聊助手"'),
          h('div',{style:{fontSize:12,color:'#666',lineHeight:1.8}},'4️⃣ 用户在频道中对智能体说「创建房间」或「发送群聊消息」')
        ]),
        h('div',{style:{textAlign:'center',marginTop:16}},[
          h(Button,{type:'primary',onClick:function(){setShowWeChat(false);}},'知道了')
        ])
      ]),
      // 设置弹窗
      h(Modal,{title:'设置',open:showSettings,onCancel:function(){setShowSettings(false);},footer:null,width:400},[
        h('div',{style:{padding:'10px 0'}},[
          h('div',{style:{marginBottom:20}},[h('div',{style:{fontSize:14,fontWeight:500,marginBottom:8}},'主题'),h('div',{style:{display:'flex',gap:8}},[h(Button,{type:theme==='light'?'primary':'default',onClick:function(){setTheme('light');localStorage.setItem('p_plugin_theme','light');}},'浅色'),h(Button,{type:theme==='dark'?'primary':'default',onClick:function(){setTheme('dark');localStorage.setItem('p_plugin_theme','dark');}},'深色')])]),
          h('div',{style:{marginBottom:20}},[h('div',{style:{fontSize:14,fontWeight:500,marginBottom:8}},'昵称'),h(Input,{value:nick,onChange:function(e){setNick(e.target.value);localStorage.setItem('p_plugin_nick',e.target.value);}})]),
          h('div',{style:{marginBottom:20}},[h('div',{style:{fontSize:14,fontWeight:500,marginBottom:8}},'用户ID'),h(Input,{value:uid,onChange:function(e){var newUid=e.target.value;setUid(newUid);if(newUid){localStorage.setItem('p_plugin_uid',newUid);msg.success('用户ID已更新');}},placeholder:'输入用户ID（如微信ID）'}),h('div',{style:{fontSize:11,color:'#999',marginTop:4}},'修改后可管理对应用户创建的房间，建议刷新页面以确保所有功能正常')])
        ])
      ]),
      // ── 分享弹窗 ──
      h(Modal,{title:null,open:showShare,onCancel:function(){setShowShare(false);},footer:null,width:540,bodyStyle:{padding:20}},[
        h('div',{style:{textAlign:'center',marginBottom:20}},[
          h('div',{style:{fontSize:40,marginBottom:8}},'🔗'),
          h('div',{style:{fontSize:18,fontWeight:700}},'分享聊天室'),
          h('div',{style:{fontSize:13,color:'#999',marginTop:4}},'生成链接分享给好友，扫码或点击链接即可加入群聊')
        ]),
        h('div',{style:{background:'#f8f8f8',borderRadius:10,padding:16,marginBottom:16}},[
          h('div',{style:{fontSize:14,fontWeight:600,marginBottom:12}},'📝 创建分享链接'),
          h('div',{style:{display:'flex',gap:10}},[
            h(Input,{value:sharePassword,onChange:function(e){setSharePassword(e.target.value);},placeholder:'密码（留空则无需密码）',prefix:'🔒',style:{flex:1}}),
            h(Select,{value:shareExpiry,onChange:setShareExpiry,style:{width:110},options:[{value:0,label:'永久有效'},{value:1,label:'1天后'},{value:3,label:'3天后'},{value:7,label:'7天后'},{value:30,label:'30天后'}]})
          ]),
          h('div',{style:{marginTop:12}},[
            h(Button,{type:'primary',loading:shareCreating,onClick:createShareLink,block:true},'🚀 生成分享链接')
          ]),
          shareLink?h('div',{style:{marginTop:12,padding:14,background:'#fff',borderRadius:8,border:'1px solid #e8e8e8'}},[
            h('div',{style:{display:'flex',alignItems:'center',gap:8,marginBottom:10}},[
              h('span',{style:{fontSize:13,color:'#07C160',fontWeight:500,flex:1,wordBreak:'break-all'}},shareLink),
              h(Button,{size:'small',onClick:function(){copyShareLink(shareLink);}},'📋 复制')
            ]),
            h('img',{src:'https://api.qrserver.com/v1/create-qr-code/?size=180x180&margin=8&data='+encodeURIComponent(window.location.origin+shareLink),
              style:{display:'block',margin:'0 auto',borderRadius:6,width:180,height:180},alt:'扫码加入',crossOrigin:'anonymous'}),
            h('div',{style:{textAlign:'center',fontSize:11,color:'#999',marginTop:4}},'📱 扫描二维码加入群聊')
          ]):null
        ]),
        shares.length>0?h('div',{style:{borderTop:'1px solid #eee',paddingTop:16}},[
          h('div',{style:{fontSize:14,fontWeight:600,marginBottom:10}},'📋 已有分享链接 ('+shares.length+')'),
          h('div',{style:{maxHeight:200,overflow:'auto'}},
            shares.map(function(s){
              return h('div',{key:s.token,style:{display:'flex',alignItems:'center',padding:'10px 12px',background:s.expired?'#fff2f0':'#fafafa',borderRadius:8,marginBottom:6,border:'1px solid '+(s.expired?'#ffccc7':'#e8e8e8')}},[
                h('div',{style:{flex:1,overflow:'hidden'}},[
                  h('div',{style:{fontSize:13,fontWeight:500}},s.room_name+(s.has_password?' 🔒':'')+(s.expired?' ⏰ 已过期':'')),
                  h('div',{style:{fontSize:11,color:'#999',whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}},new Date(s.created_at).toLocaleString()+(s.expires_at?' · 过期: '+new Date(s.expires_at).toLocaleDateString():' · 永久有效'))
                ]),
                h('div',{style:{display:'flex',gap:4,flexShrink:0}},[
                  h(Button,{size:'small',onClick:function(){copyShareLink(s.share_url);}},'📋'),
                  h(Button,{size:'small',style:{color:'#576B95'},onClick:function(){addSharedRoomToAddr(s.room_name,s.room_id);}},'📞'),
                  h(Button,{size:'small',danger:true,onClick:function(){revokeShare(s.token);}},'🗑️')
                ])
              ]);
            })
          )
        ]):null
      ]),
      // ── 通讯录弹窗 ──
      h(Modal,{title:null,open:showAddrBook,onCancel:function(){setShowAddrBook(false);},footer:null,width:560,bodyStyle:{padding:20}},[
        h('div',{style:{textAlign:'center',marginBottom:20}},[
          h('div',{style:{fontSize:40,marginBottom:8}},'📞'),
          h('div',{style:{fontSize:18,fontWeight:700}},'通讯录'),
          h('div',{style:{fontSize:13,color:'#999',marginTop:4}},'记录分享的聊天室、朋友和家人')
        ]),
        h('div',{style:{background:'#f8f8f8',borderRadius:10,padding:14,marginBottom:16}},[
          h('div',{style:{fontSize:14,fontWeight:600,marginBottom:10}},'➕ 添加联系人'),
          h('div',{style:{display:'flex',gap:8,marginBottom:8}},[
            h(Input,{value:addrName,onChange:function(e){setAddrName(e.target.value);},placeholder:'姓名 *',prefix:'👤',style:{flex:2}}),
            h(Select,{value:addrType,onChange:setAddrType,style:{width:100},
              options:[{value:'friend',label:'👥 朋友'},{value:'family',label:'🏠 家人'},{value:'room',label:'💬 聊天室'},{value:'other',label:'📌 其他'}]})
          ]),
          h('div',{style:{display:'flex',gap:8}},[
            h(Input,{value:addrPhone,onChange:function(e){setAddrPhone(e.target.value);},placeholder:'手机号码',prefix:'📱',style:{flex:1}}),
            h(Button,{type:'primary',style:{background:C.primary,flexShrink:0},onClick:addContact},'添加')
          ])
        ]),
        addrBook.length===0?h('div',{style:{textAlign:'center',padding:20,color:'#999'}},'暂无联系人'):
        h('div',{style:{maxHeight:300,overflow:'auto'}},
          addrBook.map(function(entry,idx){
            var isRoom=entry.type==='room';
            return h('div',{key:idx,style:{display:'flex',alignItems:'center',padding:'10px 12px',marginBottom:6,background:isRoom?'#e6f7ff':'#fafafa',borderRadius:8}},[
              h('div',{style:{width:36,height:36,borderRadius:'50%',background:isRoom?'#10AEFF':(entry.type==='family'?'#FF9500':'#07C160'),display:'flex',alignItems:'center',justifyContent:'center',fontSize:18,marginRight:10,flexShrink:0}},
                isRoom?'💬':(entry.type==='family'?'🏠':'👤')),
              h('div',{style:{flex:1,overflow:'hidden'}},[
                h('div',{style:{display:'flex',alignItems:'center',gap:6}},[
                  h('span',{style:{fontSize:14,fontWeight:600}},entry.name),
                  h(Tag,{color:isRoom?'blue':(entry.type==='family'?'orange':'green'),style:{fontSize:10,padding:'0 4px',lineHeight:'16px'}},isRoom?'聊天室':(entry.type==='family'?'家人':'朋友'))
                ]),
                entry.phone?h('div',{style:{fontSize:12,color:'#666',marginTop:2}},'📱 '+entry.phone):null,
                isRoom?h('div',{style:{fontSize:12,color:'#576B95',marginTop:2,cursor:'pointer'},onClick:function(){setShowAddrBook(false);copyShareLink(entry.link||'/api/plugins/p_plugin/web/'+entry.note);}},entry.link?'🔗 '+entry.link:'🔗 /api/plugins/p_plugin/web/'+entry.note):null,
                entry.addedAt?h('div',{style:{fontSize:10,color:'#999',marginTop:2}},new Date(entry.addedAt).toLocaleDateString()):null
              ]),
              h('div',{style:{display:'flex',gap:4,flexShrink:0}},[
                isRoom?h(Button,{size:'small',onClick:function(){setShowAddrBook(false);copyShareLink(entry.link||'/api/plugins/p_plugin/web/'+entry.note);}},'📋'):null,
                h(Button,{size:'small',danger:true,onClick:function(){delContact(idx);}},'🗑️')
              ])
            ]);
          })
        ),
        h('div',{style:{marginTop:12,padding:'10px 12px',background:'#fffbe6',borderRadius:8,fontSize:12,color:'#d4880b'}},'💡 在聊天室中点击「加入通讯录」按钮即可保存分享的房间链接')
      ]),
      // ── Add Panel Modal ──
      h(Modal,{title:'Add Panel',open:showAddPanel,onCancel:function(){setShowAddPanel(false);},footer:null,width:480,bodyStyle:{padding:24}},[
        h('div',{style:{marginBottom:16}},[
          h('div',{style:{fontSize:14,fontWeight:500,marginBottom:8}},'Panel Type'),
          h('div',{style:{display:'flex',gap:8,marginBottom:16}},[
            h(Button,{type:addPanelType==='webview'?'primary':'default',onClick:function(){setAddPanelType('webview');},size:'small'},'🌐 Web'),
            h(Button,{type:addPanelType==='custom'?'primary':'default',onClick:function(){setAddPanelType('custom');},size:'small'},'📝 Custom'),
            h(Button,{type:addPanelType==='chat'?'primary':'default',onClick:function(){setAddPanelType('chat');},size:'small'},'💬 Chat')
          ])
        ]),
        h('div',{style:{marginBottom:16}},[
          h('div',{style:{fontSize:14,fontWeight:500,marginBottom:8}},'Panel Name'),
          h(Input,{value:newPanelName,onChange:function(e){setNewPanelName(e.target.value);},
            placeholder:addPanelType==='webview'?'e.g. AI Site':'Panel Name',
            prefix:addPanelType==='webview'?'🌐':(addPanelType==='custom'?'📝':'💬')})
        ]),
        addPanelType==='webview'?h('div',{style:{marginBottom:16}},[
          h('div',{style:{fontSize:14,fontWeight:500,marginBottom:8}},'URL (required)'),
          h(Input,{value:newPanelUrl,onChange:function(e){setNewPanelUrl(e.target.value);},
            placeholder:'e.g. https://example.com',prefix:'🔗',
            onPressEnter:addPanel})
        ]):null,
        addPanelType==='custom'?h('div',{style:{marginBottom:16}},[
          h('div',{style:{fontSize:14,fontWeight:500,marginBottom:8}},'HTML Content'),
          h(Input.TextArea,{value:newPanelUrl,onChange:function(e){setNewPanelUrl(e.target.value);},
            placeholder:'Enter HTML content to display...',autoSize:{minRows:3,maxRows:8}})
        ]):null,
        addPanelType==='chat'?h('div',{style:{padding:20,background:'#f6ffed',borderRadius:8,marginBottom:16,fontSize:13,color:'#389e0d'}},
          '💬 Chat panel for group messages.'):null,
        h(Button,{type:'primary',block:true,style:{background:C.primary},onClick:addPanel},
          '🚀 Add Panel')
      ]),
      // ── Scene Selector Modal ──
      h(Modal,{title:'🎭 切换场景',open:showSceneSelector,onCancel:function(){setShowSceneSelector(false);},footer:null,width:520},[
        h('div',{style:{padding:'10px 0'}},[
          h('div',{style:{fontSize:13,color:'#666',marginBottom:16}},'选择场景主题来改变聊天室的氛围'),
          availableScenes.map(function(s){
            var isCurrent=currentScene&&currentScene.id===s.id;
            return h('div',{key:s.id,style:{padding:14,borderRadius:10,marginBottom:10,cursor:'pointer',border:'2px solid '+(isCurrent?'#7c3aed':'#e8e8e8'),background:isCurrent?'#f3e8ff':'#fafafa'},onClick:function(){changeScene(s.id);}},[
              h('div',{style:{display:'flex',alignItems:'center',gap:10}},[
                h('span',{style:{fontSize:28}},s.icon),
                h('div',{style:{flex:1}},[
                  h('div',{style:{fontSize:15,fontWeight:600}},s.name+(isCurrent?' (当前)':'')),
                  h('div',{style:{fontSize:12,color:'#666',marginTop:2}},s.description)
                ]),
                isCurrent?h(Tag,{color:'purple'},'当前'):null,
                !isCurrent?h(Button,{size:'small',type:'primary'},'切换'):null
              ])
            ]);
          })
        ])
      ]),
      // ── Inventory Modal ──
      h(Modal,{title:'🎒 我的背包',open:showInventory,onCancel:function(){setShowInventory(false);},footer:null,width:480},[
        h('div',{style:{padding:'10px 0'}},[
          // Clues section
          h('div',{style:{marginBottom:16}},[
            h('div',{style:{fontSize:14,fontWeight:600,marginBottom:8,borderBottom:'1px solid #eee',paddingBottom:6}},'🔍 线索 ('+inventory.clues.length+')'),
            inventory.clues.length===0?h('div',{style:{color:'#999',fontSize:13,padding:'10px 0'}},'暂无线索，与NPC对话获取'):null,
            inventory.clues.map(function(c,i){return h('div',{key:i,style:{padding:10,background:'#f6ffed',borderRadius:8,marginBottom:6}},[
              h('div',{style:{fontSize:13,fontWeight:500}},c.icon+' '+c.name),
              h('div',{style:{fontSize:11,color:'#666',marginTop:2}},c.description)
            ]);})
          ]),
          // Items section
          h('div',{style:{marginBottom:16}},[
            h('div',{style:{fontSize:14,fontWeight:600,marginBottom:8,borderBottom:'1px solid #eee',paddingBottom:6}},'📦 道具 ('+inventory.items.length+')'),
            inventory.items.length===0?h('div',{style:{color:'#999',fontSize:13,padding:'10px 0'}},'暂无道具'):null,
            inventory.items.map(function(item,i){return h('div',{key:i,style:{padding:10,background:'#e6f7ff',borderRadius:8,marginBottom:6}},[
              h('div',{style:{fontSize:13,fontWeight:500}},item.icon+' '+item.name),
              h('div',{style:{fontSize:11,color:'#666',marginTop:2}},item.description)
            ]);})
          ]),
          // Achievements section
          h('div',{style:{marginBottom:16}},[
            h('div',{style:{fontSize:14,fontWeight:600,marginBottom:8,borderBottom:'1px solid #eee',paddingBottom:6}},'🏆 成就 ('+inventory.achievements.length+')'),
            inventory.achievements.length===0?h('div',{style:{color:'#999',fontSize:13,padding:'10px 0'}},'暂无成就'):null,
            inventory.achievements.map(function(a,i){return h('div',{key:i,style:{padding:10,background:'#fffbe6',borderRadius:8,marginBottom:6}},[
              h('div',{style:{fontSize:13,fontWeight:500}},a.icon+' '+a.name),
              h('div',{style:{fontSize:11,color:'#666',marginTop:2}},a.description)
            ]);})
          ])
        ])
      ]),
      // ── Quests Modal ──
      h(Modal,{title:'📜 任务列表',open:showQuests,onCancel:function(){setShowQuests(false);},footer:null,width:480},[
        h('div',{style:{padding:'10px 0'}},[
          // Active quests
          h('div',{style:{marginBottom:16}},[
            h('div',{style:{fontSize:14,fontWeight:600,marginBottom:8,borderBottom:'1px solid #eee',paddingBottom:6}},'⏳ 进行中 ('+quests.active.length+')'),
            quests.active.length===0?h('div',{style:{color:'#999',fontSize:13,padding:'10px 0'}},'暂无进行中的任务'):null,
            quests.active.map(function(q,i){return h('div',{key:i,style:{padding:12,background:'#fff2e8',borderRadius:8,marginBottom:8}},[
              h('div',{style:{fontSize:14,fontWeight:600}},q.title),
              h('div',{style:{fontSize:12,color:'#666',marginTop:4}},q.description),
              h('div',{style:{fontSize:11,color:'#999',marginTop:6}},'进度: '+q.progress+'%')
            ]);})
          ]),
          // Completed quests
          h('div',{style:{marginBottom:16}},[
            h('div',{style:{fontSize:14,fontWeight:600,marginBottom:8,borderBottom:'1px solid #eee',paddingBottom:6}},'✅ 已完成 ('+quests.completed.length+')'),
            quests.completed.length===0?h('div',{style:{color:'#999',fontSize:13,padding:'10px 0'}},'暂无已完成的任务'):null,
            quests.completed.map(function(q,i){return h('div',{key:i,style:{padding:12,background:'#f6ffed',borderRadius:8,marginBottom:8}},[
              h('div',{style:{fontSize:14,fontWeight:500}},'✓ '+q.title),
              h('div',{style:{fontSize:11,color:'#999',marginTop:4}},'完成于: '+new Date(q.completed_at).toLocaleDateString())
            ]);})
          ])
        ])
      ])
    ]);
  }
  // ═══════════════════════════════════════════════════════════════
  // 双显示模式注册：应用栏目 + 侧边栏菜单（参考 dual-registration 技能）
  // ═══════════════════════════════════════════════════════════════
  
  var PLUGIN_ID = 'p_plugin';
  
  // ── 1. 应用栏目注册（新旧版共用）──
  if (typeof QwenPaw !== 'undefined' && QwenPaw.registerRoutes) {
    try {
      QwenPaw.registerRoutes(PLUGIN_ID, [{
        path: '/apps/' + PLUGIN_ID,
        component: PPage,
        label: 'P 群聊',
        icon: 'Q',
        priority: 20
      }]);
      console.log('[P] ✅ Registered via registerRoutes (App Gallery)');
    } catch(e) {
      console.error('[P] ❌ registerRoutes failed:', e);
    }
  } else {
    console.log('[P] ⚠️ QwenPaw.registerRoutes not available');
  }
  
  // ── 2. 新版侧边栏菜单 ──
  if (QP.menu && QP.menu.add) {
    try {
      QP.menu.add(PLUGIN_ID, [{
        id: PLUGIN_ID + '.menu',
        location: 'primary.agentScoped',
        label: 'P 群聊',
        icon: function() {
          return h('span', { style: { fontSize: 18 } }, 'Q');
        },
        route: PLUGIN_ID + '.home',
        order: 20
      }]);
      console.log('[P] ✅ Registered via menu.add (Sidebar Menu)');
    } catch(e) {
      console.error('[P] ❌ menu.add failed:', e);
    }
  } else {
    console.log('[P] ⚠️ QP.menu.add not available');
  }
  
  // ── 3. 新版侧边栏路由 ──
  if (QP.route && QP.route.add) {
    try {
      QP.route.add(PLUGIN_ID, [{
        id: PLUGIN_ID + '.home',
        path: '/plugin/' + PLUGIN_ID,
        component: PPage
      }]);
      console.log('[P] ✅ Registered via route.add (Sidebar Route)');
    } catch(e) {
      console.error('[P] ❌ route.add failed:', e);
    }
  } else {
    console.log('[P] ⚠️ QP.route.add not available');
  }
  
  console.log('[P] v5.5.1 (双显示模式：应用栏目 + 侧边栏 + 游戏可玩性强化) 初始化完成');
})();