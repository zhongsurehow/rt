"""
事件总线系统 - 解耦各大系统间的直接调用关系
通过事件广播和订阅机制实现松耦合的系统通信
"""

from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import threading
import time
import uuid
from collections import defaultdict
import weakref

class EventPriority(Enum):
    """事件优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Event:
    """事件数据结构"""
    type: str
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = ""
    timestamp: float = field(default_factory=time.time)
    priority: EventPriority = EventPriority.NORMAL
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    propagation_stopped: bool = False
    
    def stop_propagation(self):
        """停止事件传播"""
        self.propagation_stopped = True

@dataclass
class EventListener:
    """事件监听器"""
    callback: Callable[[Event], None]
    priority: EventPriority = EventPriority.NORMAL
    once: bool = False  # 是否只执行一次
    filter_func: Optional[Callable[[Event], bool]] = None  # 事件过滤函数
    listener_id: str = field(default_factory=lambda: str(uuid.uuid4()))

class EventBus:
    """事件总线"""
    
    def __init__(self):
        """初始化事件总线"""
        self._listeners: Dict[str, List[EventListener]] = defaultdict(list)
        self._global_listeners: List[EventListener] = []
        self._event_history: List[Event] = []
        self._max_history_size = 1000
        self._lock = threading.RLock()
        self._middleware: List[Callable[[Event], bool]] = []
        
        # 统计信息
        self._stats = {
            "events_emitted": 0,
            "events_processed": 0,
            "listeners_count": 0
        }
    
    def emit(self, event_type: str, data: Dict[str, Any] = None, 
             source: str = "", priority: EventPriority = EventPriority.NORMAL) -> Event:
        """发射事件"""
        if data is None:
            data = {}
        
        event = Event(
            type=event_type,
            data=data,
            source=source,
            priority=priority
        )
        
        return self.emit_event(event)
    
    def emit_event(self, event: Event) -> Event:
        """发射事件对象"""
        with self._lock:
            self._stats["events_emitted"] += 1
            
            # 记录事件历史
            self._add_to_history(event)
            
            # 执行中间件
            for middleware in self._middleware:
                if not middleware(event):
                    return event  # 中间件阻止了事件传播
            
            # 获取所有相关监听器
            listeners = self._get_listeners_for_event(event)
            
            # 按优先级排序
            listeners.sort(key=lambda l: l.priority.value, reverse=True)
            
            # 执行监听器
            for listener in listeners:
                if event.propagation_stopped:
                    break
                
                try:
                    # 检查过滤条件
                    if listener.filter_func and not listener.filter_func(event):
                        continue
                    
                    # 执行回调
                    listener.callback(event)
                    self._stats["events_processed"] += 1
                    
                    # 如果是一次性监听器，移除它
                    if listener.once:
                        self._remove_listener(listener)
                        
                except Exception as e:
                    # 发射错误事件
                    error_event = Event(
                        type="system.listener_error",
                        data={
                            "original_event": event,
                            "listener_id": listener.listener_id,
                            "error": str(e)
                        },
                        source="event_bus",
                        priority=EventPriority.HIGH
                    )
                    # 避免递归错误
                    if event.type != "system.listener_error":
                        self.emit_event(error_event)
            
            return event
    
    def on(self, event_type: str, callback: Callable[[Event], None], 
           priority: EventPriority = EventPriority.NORMAL,
           once: bool = False,
           filter_func: Optional[Callable[[Event], bool]] = None) -> str:
        """订阅事件"""
        listener = EventListener(
            callback=callback,
            priority=priority,
            once=once,
            filter_func=filter_func
        )
        
        with self._lock:
            self._listeners[event_type].append(listener)
            self._stats["listeners_count"] += 1
        
        return listener.listener_id
    
    def once(self, event_type: str, callback: Callable[[Event], None],
             priority: EventPriority = EventPriority.NORMAL) -> str:
        """订阅一次性事件"""
        return self.on(event_type, callback, priority, once=True)
    
    def on_any(self, callback: Callable[[Event], None],
               priority: EventPriority = EventPriority.NORMAL,
               filter_func: Optional[Callable[[Event], bool]] = None) -> str:
        """订阅所有事件"""
        listener = EventListener(
            callback=callback,
            priority=priority,
            filter_func=filter_func
        )
        
        with self._lock:
            self._global_listeners.append(listener)
            self._stats["listeners_count"] += 1
        
        return listener.listener_id
    
    def off(self, event_type: str, listener_id: str = None, 
            callback: Callable[[Event], None] = None) -> bool:
        """取消订阅"""
        with self._lock:
            if event_type in self._listeners:
                listeners = self._listeners[event_type]
                
                # 根据不同条件移除监听器
                if listener_id:
                    listeners[:] = [l for l in listeners if l.listener_id != listener_id]
                elif callback:
                    listeners[:] = [l for l in listeners if l.callback != callback]
                else:
                    # 移除所有该事件类型的监听器
                    listeners.clear()
                
                self._stats["listeners_count"] = sum(len(listeners) for listeners in self._listeners.values())
                self._stats["listeners_count"] += len(self._global_listeners)
                
                return True
        
        return False
    
    def off_all(self, event_type: str = None):
        """移除所有监听器"""
        with self._lock:
            if event_type:
                if event_type in self._listeners:
                    self._listeners[event_type].clear()
            else:
                self._listeners.clear()
                self._global_listeners.clear()
            
            self._stats["listeners_count"] = sum(len(listeners) for listeners in self._listeners.values())
            self._stats["listeners_count"] += len(self._global_listeners)
    
    def add_middleware(self, middleware: Callable[[Event], bool]):
        """添加中间件"""
        self._middleware.append(middleware)
    
    def remove_middleware(self, middleware: Callable[[Event], bool]):
        """移除中间件"""
        if middleware in self._middleware:
            self._middleware.remove(middleware)
    
    def _get_listeners_for_event(self, event: Event) -> List[EventListener]:
        """获取事件的所有监听器"""
        listeners = []
        
        # 特定事件类型的监听器
        if event.type in self._listeners:
            listeners.extend(self._listeners[event.type])
        
        # 全局监听器
        listeners.extend(self._global_listeners)
        
        return listeners
    
    def _remove_listener(self, listener: EventListener):
        """移除监听器"""
        # 从特定事件类型中移除
        for event_type, listeners in self._listeners.items():
            if listener in listeners:
                listeners.remove(listener)
                self._stats["listeners_count"] -= 1
                return
        
        # 从全局监听器中移除
        if listener in self._global_listeners:
            self._global_listeners.remove(listener)
            self._stats["listeners_count"] -= 1
    
    def _add_to_history(self, event: Event):
        """添加到事件历史"""
        self._event_history.append(event)
        
        # 限制历史记录大小
        if len(self._event_history) > self._max_history_size:
            self._event_history = self._event_history[-self._max_history_size:]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            return {
                **self._stats,
                "event_types": list(self._listeners.keys()),
                "history_size": len(self._event_history)
            }
    
    def get_history(self, event_type: str = None, limit: int = 100) -> List[Event]:
        """获取事件历史"""
        with self._lock:
            if event_type:
                filtered_events = [e for e in self._event_history if e.type == event_type]
                return filtered_events[-limit:]
            else:
                return self._event_history[-limit:]
    
    def clear_history(self):
        """清空事件历史"""
        with self._lock:
            self._event_history.clear()

# 全局事件总线实例
_global_event_bus = None

def get_event_bus() -> EventBus:
    """获取全局事件总线实例"""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus

def emit(event_type: str, data: Dict[str, Any] = None, 
         source: str = "", priority: EventPriority = EventPriority.NORMAL) -> Event:
    """全局事件发射函数"""
    return get_event_bus().emit(event_type, data, source, priority)

def on(event_type: str, callback: Callable[[Event], None], 
       priority: EventPriority = EventPriority.NORMAL) -> str:
    """全局事件订阅函数"""
    return get_event_bus().on(event_type, callback, priority)

def once(event_type: str, callback: Callable[[Event], None],
         priority: EventPriority = EventPriority.NORMAL) -> str:
    """全局一次性事件订阅函数"""
    return get_event_bus().once(event_type, callback, priority)

def off(event_type: str, listener_id: str = None) -> bool:
    """全局事件取消订阅函数"""
    return get_event_bus().off(event_type, listener_id)

# 预定义的游戏事件类型
class GameEvents:
    """游戏事件类型常量"""
    
    # 游戏流程事件
    GAME_START = "game.start"
    GAME_END = "game.end"
    GAME_PAUSE = "game.pause"
    GAME_RESUME = "game.resume"
    
    # 回合事件
    TURN_START = "turn.start"
    TURN_END = "turn.end"
    PHASE_CHANGE = "phase.change"
    
    # 玩家事件
    PLAYER_JOIN = "player.join"
    PLAYER_LEAVE = "player.leave"
    PLAYER_ACTION = "player.action"
    PLAYER_DAMAGE = "player.damage"
    PLAYER_HEAL = "player.heal"
    PLAYER_DEATH = "player.death"
    
    # 卡牌事件
    CARD_DRAW = "card.draw"
    CARD_PLAY = "card.play"
    CARD_DISCARD = "card.discard"
    CARD_EFFECT = "card.effect"
    
    # 战斗事件
    BATTLE_START = "battle.start"
    BATTLE_END = "battle.end"
    ATTACK = "battle.attack"
    DEFEND = "battle.defend"
    
    # UI事件
    UI_UPDATE = "ui.update"
    UI_NOTIFICATION = "ui.notification"
    UI_ANIMATION = "ui.animation"
    
    # 系统事件
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"
    SYSTEM_INFO = "system.info"
    SYSTEM_INITIALIZED = "system.initialized"
    
    # 游戏状态事件
    GAME_STATE_CHANGED = "game.state.changed"
    ACTION_RECORDED = "action.recorded"
    EFFECT_EXECUTED = "effect.executed"
    VICTORY_ACHIEVED = "victory.achieved"
    AI_ACTION_DECIDED = "ai.action.decided"
    CARD_PLAYED = "card.played"
    TURN_STARTED = "turn.started"
    
    # 成就事件
    ACHIEVEMENT_UNLOCK = "achievement.unlock"
    ACHIEVEMENT_PROGRESS = "achievement.progress"
    
    # 音效事件
    SOUND_PLAY = "sound.play"
    SOUND_STOP = "sound.stop"
    MUSIC_CHANGE = "music.change"

# 事件数据结构辅助类
class EventData:
    """事件数据构建辅助类"""
    
    @staticmethod
    def player_action(player_id: str, action: str, details: Dict = None) -> Dict:
        """构建玩家行动事件数据"""
        return {
            "player_id": player_id,
            "action": action,
            "details": details or {},
            "timestamp": time.time()
        }
    
    @staticmethod
    def card_play(player_id: str, card_id: str, target: str = None) -> Dict:
        """构建卡牌使用事件数据"""
        return {
            "player_id": player_id,
            "card_id": card_id,
            "target": target,
            "timestamp": time.time()
        }
    
    @staticmethod
    def damage_dealt(source: str, target: str, amount: int, damage_type: str = "direct") -> Dict:
        """构建伤害事件数据"""
        return {
            "source": source,
            "target": target,
            "amount": amount,
            "damage_type": damage_type,
            "timestamp": time.time()
        }
    
    @staticmethod
    def ui_notification(message: str, notification_type: str = "info", duration: float = 3.0) -> Dict:
        """构建UI通知事件数据"""
        return {
            "message": message,
            "type": notification_type,
            "duration": duration,
            "timestamp": time.time()
        }
    
    @staticmethod
    def achievement_unlock(achievement_id: str, player_id: str, description: str = "") -> Dict:
        """构建成就解锁事件数据"""
        return {
            "achievement_id": achievement_id,
            "player_id": player_id,
            "description": description,
            "timestamp": time.time()
        }

# 事件过滤器辅助函数
class EventFilters:
    """事件过滤器辅助类"""
    
    @staticmethod
    def by_source(source: str) -> Callable[[Event], bool]:
        """按事件源过滤"""
        return lambda event: event.source == source
    
    @staticmethod
    def by_priority(min_priority: EventPriority) -> Callable[[Event], bool]:
        """按最小优先级过滤"""
        return lambda event: event.priority.value >= min_priority.value
    
    @staticmethod
    def by_player(player_id: str) -> Callable[[Event], bool]:
        """按玩家ID过滤"""
        return lambda event: event.data.get("player_id") == player_id
    
    @staticmethod
    def by_data_key(key: str, value: Any) -> Callable[[Event], bool]:
        """按数据键值过滤"""
        return lambda event: event.data.get(key) == value