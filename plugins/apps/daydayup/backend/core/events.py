"""
事件管理器
基于 Deep Tutor 的事件系统
"""

import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional
from collections import defaultdict

logger = logging.getLogger("daydayup")


class EventManager:
    """
    事件管理器
    管理插件内的事件订阅和发布
    """
    
    def __init__(self):
        # 事件监听器
        self._listeners: Dict[str, List[Callable]] = defaultdict(list)
        # 异步事件队列
        self._event_queue: asyncio.Queue = asyncio.Queue()
        # 事件处理器任务
        self._processor_task: Optional[asyncio.Task] = None
        # 运行状态
        self._running = False
        
        logger.info("[Events] Event manager initialized")
    
    def on(self, event: str, handler: Callable):
        """
        订阅事件
        
        Args:
            event: 事件名称
            handler: 事件处理器
        """
        self._listeners[event].append(handler)
        logger.debug(f"[Events] Handler registered for '{event}'")
    
    def off(self, event: str, handler: Callable = None):
        """
        取消订阅
        
        Args:
            event: 事件名称
            handler: 要移除的处理器，为 None 则移除所有
        """
        if handler is None:
            self._listeners[event].clear()
        else:
            self._listeners[event] = [
                h for h in self._listeners[event] if h != handler
            ]
        logger.debug(f"[Events] Handlers removed for '{event}'")
    
    async def emit(self, event: str, data: Any = None):
        """
        触发事件
        
        Args:
            event: 事件名称
            data: 事件数据
        """
        await self._event_queue.put((event, data))
        logger.debug(f"[Events] Event '{event}' queued")
    
    async def emit_sync(self, event: str, data: Any = None):
        """
        同步触发事件（立即执行）
        
        Args:
            event: 事件名称
            data: 事件数据
        """
        await self._process_event(event, data)
    
    async def _process_event(self, event: str, data: Any):
        """处理单个事件"""
        handlers = self._listeners.get(event, [])
        
        if not handlers:
            return
        
        logger.debug(f"[Events] Processing '{event}' with {len(handlers)} handlers")
        
        tasks = []
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    task = asyncio.create_task(handler(data))
                    tasks.append(task)
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"[Events] Handler error for '{event}': {e}")
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _event_processor(self):
        """事件处理器主循环"""
        self._running = True
        logger.info("[Events] Event processor started")
        
        while self._running:
            try:
                event, data = await self._event_queue.get()
                await self._process_event(event, data)
                self._event_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[Events] Processor error: {e}")
        
        logger.info("[Events] Event processor stopped")
    
    def start(self):
        """启动事件处理器"""
        if self._processor_task is None or self._processor_task.done():
            self._processor_task = asyncio.create_task(self._event_processor())
    
    def stop(self):
        """停止事件处理器"""
        self._running = False
        if self._processor_task:
            self._processor_task.cancel()
    
    def get_listeners(self, event: str = None) -> Dict[str, List[Callable]]:
        """获取监听器列表"""
        if event:
            return {event: self._listeners.get(event, [])}
        return dict(self._listeners)
    
    def clear(self):
        """清除所有监听器"""
        self._listeners.clear()
        logger.info("[Events] All listeners cleared")
