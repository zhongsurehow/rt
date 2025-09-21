"""
优雅编程模式模块
实现枚举、装饰器、生成器等优雅的Python编程模式
"""

from enum import Enum, auto
from typing import Generator, List, Dict, Any, Callable, Optional, Union
import functools
import time
import logging
from dataclasses import dataclass

# ==================== 枚举定义 ====================

class CardType(Enum):
    """卡牌类型枚举"""
    SPELL = "法术牌"
    CREATURE = "生物牌"
    ARTIFACT = "法器牌"
    STRATEGY = "策略牌"
    HEXAGRAM = "卦牌"
    YIJING = "易经牌"
    
    def __str__(self):
        return self.value

class PlayerState(Enum):
    """玩家状态枚举"""
    ACTIVE = "active"
    WAITING = "waiting"
    PLAYING = "playing"
    FINISHED = "finished"
    INACTIVE = "inactive"

class GamePhase(Enum):
    """游戏阶段枚举"""
    INITIALIZATION = "初始化"
    PREPARATION = "准备阶段"
    MAIN_PHASE = "主要阶段"
    COMBAT = "战斗阶段"
    END_PHASE = "结束阶段"
    GAME_OVER = "游戏结束"
    
    def __str__(self):
        return self.value

class ActionType(Enum):
    """行动类型枚举"""
    PLAY_CARD = "play_card"
    MOVE = "move"
    STUDY = "study"
    MEDITATE = "meditate"
    PASS = "pass"
    SPECIAL = "special"
    RESOURCE_CHANGE = "resource_change"
    STATE_UPDATE = "state_update"
    TURN_CHANGE = "turn_change"
    VALIDATION = "validation"

class ResourceType(Enum):
    """资源类型枚举"""
    QI = "气"
    DAO_XING = "道行"
    CHENG_YI = "诚意"
    ACTION_POINTS = "行动点"
    
    def __str__(self):
        return self.value

class MessageType(Enum):
    """消息类型枚举"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    HIGHLIGHT = "highlight"
    MYSTICAL = "mystical"
    RESOURCE = "resource"

class CardRarity(Enum):
    """卡牌稀有度枚举"""
    COMMON = "普通"
    UNCOMMON = "稀有"
    RARE = "珍贵"
    EPIC = "史诗"
    LEGENDARY = "传说"
    MYTHIC = "神话"
    
    def __str__(self):
        return self.value

class ZoneType(Enum):
    """区域类型枚举"""
    HEAVEN = "天"
    EARTH = "地"
    HUMAN = "人"
    VOID = "虚空"
    
    def __str__(self):
        return self.value

# ==================== 装饰器定义 ====================

def require_resource(resource_type: ResourceType, amount: int):
    """
    资源消耗检查装饰器
    
    Args:
        resource_type: 资源类型
        amount: 消耗数量
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(player, *args, **kwargs):
            # 获取玩家当前资源
            current_amount = getattr(player, resource_type.name.lower(), 0)
            
            if current_amount < amount:
                raise ValueError(f"{resource_type.value}不足！需要 {amount}, 当前只有 {current_amount}")
            
            # 资源足够，执行原始函数
            result = func(player, *args, **kwargs)
            
            # 扣除资源
            setattr(player, resource_type.name.lower(), current_amount - amount)
            
            return result
        return wrapper
    return decorator

def log_action(action_type: ActionType, log_level: int = logging.INFO):
    """
    行动日志记录装饰器
    
    Args:
        action_type: 行动类型
        log_level: 日志级别
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # 记录开始
            logging.log(log_level, f"开始执行 {action_type.value}")
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logging.log(log_level, f"{action_type.value} 执行成功，耗时 {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logging.error(f"{action_type.value} 执行失败，耗时 {execution_time:.3f}s，错误: {e}")
                raise
        return wrapper
    return decorator

def performance_monitor(threshold_ms: float = 100.0):
    """
    性能监控装饰器
    
    Args:
        threshold_ms: 性能警告阈值（毫秒）
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            execution_time = (time.perf_counter() - start_time) * 1000
            
            if execution_time > threshold_ms:
                logging.warning(f"函数 {func.__name__} 执行时间过长: {execution_time:.2f}ms")
            
            return result
        return wrapper
    return decorator

def validate_game_state(required_phase: Optional[GamePhase] = None):
    """
    游戏状态验证装饰器
    
    Args:
        required_phase: 要求的游戏阶段
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(game_state, *args, **kwargs):
            if required_phase and hasattr(game_state, 'phase'):
                if game_state.phase != required_phase:
                    raise ValueError(f"当前阶段 {game_state.phase.value} 不允许此操作，需要 {required_phase.value}")
            
            return func(game_state, *args, **kwargs)
        return wrapper
    return decorator

def retry_on_failure(max_attempts: int = 3, delay: float = 0.1):
    """
    失败重试装饰器
    
    Args:
        max_attempts: 最大重试次数
        delay: 重试间隔（秒）
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                        logging.warning(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {e}")
            
            logging.error(f"函数 {func.__name__} 在 {max_attempts} 次尝试后仍然失败")
            raise last_exception
        return wrapper
    return decorator

# ==================== 生成器函数 ====================

def generate_possible_moves(player, game_state) -> Generator[Dict[str, Any], None, None]:
    """
    生成所有可能的行动（惰性求值）
    
    Args:
        player: 玩家对象
        game_state: 游戏状态
        
    Yields:
        Dict: 行动描述字典
    """
    try:
        # 检查所有手牌
        if hasattr(player, 'hand') and player.hand:
            for i, card in enumerate(player.hand):
                if hasattr(card, 'can_play') and card.can_play(game_state):
                    yield {
                        'type': ActionType.PLAY_CARD,
                        'description': f"打出 {getattr(card, 'name', '卡牌')} 🎴",
                        'card_index': i,
                        'cost': getattr(card, 'qi_cost', 1)
                    }
                elif hasattr(card, 'associated_guas'):
                    for zone in getattr(card, 'associated_guas', []):
                        yield {
                            'type': ActionType.PLAY_CARD,
                            'description': f"打出 {getattr(card, 'name', '卡牌')} 到 {zone} 🎴",
                            'card_index': i,
                            'target_zone': zone,
                            'cost': getattr(card, 'qi_cost', 1)
                        }
        
        # 检查冥想行动
        if getattr(player, 'qi', 0) < 10:  # 气不满时可以冥想
            yield {
                'type': ActionType.MEDITATE,
                'description': "冥想获得气 🧘",
                'cost': 0
            }
        
        # 检查学习行动
        if getattr(player, 'dao_xing', 0) < 20:  # 道行不满时可以学习
            yield {
                'type': ActionType.STUDY,
                'description': "学习获得道行 📚",
                'cost': 1
            }
        
        # 检查移动行动
        if hasattr(game_state, 'board') and hasattr(player, 'position'):
            for zone_name in getattr(game_state.board, 'gua_zones', []):
                if zone_name != getattr(player.position, 'value', player.position):
                    yield {
                        'type': ActionType.MOVE,
                        'description': f"移动到 {zone_name} 🚶",
                        'target_zone': zone_name,
                        'cost': 1
                    }
        
        # 特殊行动
        if getattr(player, 'cheng_yi', 0) >= 3:
            yield {
                'type': ActionType.PASS,  # 使用PASS作为特殊行动类型
                'description': "变卦转换 🔄",
                'action': 'biangua_prompt',
                'cost': 1
            }
            
        if getattr(player, 'qi', 0) >= 3:
            yield {
                'type': ActionType.PASS,  # 使用PASS作为特殊行动类型
                'description': "占卜运势 🔮",
                'action': 'divine_fortune',
                'cost': 1
            }
        
        # 总是可以跳过
        yield {
            'type': ActionType.PASS,
            'description': "跳过回合 ⏭️",
            'cost': 0
        }
        
    except Exception as e:
        # 如果出现错误，至少返回基础行动
        yield {
            'type': ActionType.PASS,
            'description': "跳过回合 ⏭️",
            'cost': 0
        }

def generate_ai_strategies(game_state, depth: int = 3) -> Generator[Dict[str, Any], None, None]:
    """
    生成AI策略（惰性求值）
    
    Args:
        game_state: 游戏状态
        depth: 策略深度
        
    Yields:
        策略字典
    """
    try:
        player = game_state.get_current_player()
        
        # 分析当前局势
        qi_ratio = getattr(player, 'qi', 0) / 10.0  # 假设最大气为10
        dao_xing_ratio = getattr(player, 'dao_xing', 0) / 20.0  # 假设最大道行为20
        hand_size = len(getattr(player, 'hand', []))
        
        # 资源导向策略
        if qi_ratio < 0.3:  # 气不足
            yield {
                "name": "resource_recovery",
                "priority": 0.9,
                "description": "资源恢复策略 - 优先冥想获得气",
                "focus": "meditation",
                "actions": ["meditate", "meditate", "study"]
            }
            
        # 扩张策略
        if hand_size > 3 and qi_ratio > 0.5:
            yield {
                "name": "expansion",
                "priority": 0.8,
                "description": "扩张策略 - 积极打出卡牌控制区域",
                "focus": "territory_control",
                "actions": ["play_card", "move", "play_card"]
            }
            
        # 平衡发展策略
        yield {
            "name": "balanced_development",
            "priority": 0.7,
            "description": "平衡发展策略 - 资源与行动并重",
            "focus": "balanced",
            "actions": ["study", "meditate", "play_card"]
        }
        
        # 防守策略
        if dao_xing_ratio < 0.4:
            yield {
                "name": "defensive",
                "priority": 0.6,
                "description": "防守策略 - 优先提升道行",
                "focus": "defense",
                "actions": ["study", "study", "meditate"]
            }
            
        # 激进策略
        if qi_ratio > 0.7 and hand_size > 2:
            yield {
                "name": "aggressive",
                "priority": 0.8,
                "description": "激进策略 - 快速扩张控制",
                "focus": "aggression",
                "actions": ["play_card", "play_card", "move"]
            }
            
        # 特殊策略（基于深度）
        if depth > 1:
            # 长期策略
            yield {
                "name": "long_term_cultivation",
                "priority": 0.5,
                "description": "长期修炼策略 - 注重道行积累",
                "focus": "cultivation",
                "actions": ["study"] * depth
            }
            
            # 控制策略
            if hand_size > 1:
                yield {
                    "name": "zone_control",
                    "priority": 0.7,
                    "description": "区域控制策略 - 集中控制关键区域",
                    "focus": "control",
                    "actions": ["move", "play_card"] * (depth // 2)
                }
                
        # 应急策略
        if qi_ratio < 0.2 and dao_xing_ratio < 0.2:
            yield {
                "name": "emergency_recovery",
                "priority": 1.0,
                "description": "应急恢复策略 - 全力恢复资源",
                "focus": "emergency",
                "actions": ["meditate", "meditate", "meditate"]
            }
            
    except Exception as e:
        # 默认策略
        yield {
            "name": "default",
            "priority": 0.5,
            "description": "默认策略 - 基础行动",
            "focus": "default",
            "actions": ["meditate", "study", "pass"]
        }

def generate_card_combinations(cards: List, min_combo_size: int = 2) -> Generator[List, None, None]:
    """
    生成卡牌组合（惰性求值）
    
    Args:
        cards: 卡牌列表
        min_combo_size: 最小组合大小
        
    Yields:
        卡牌组合列表
    """
    try:
        if not cards or len(cards) < min_combo_size:
            return
            
        from itertools import combinations
        
        # 生成不同大小的组合
        for combo_size in range(min_combo_size, len(cards) + 1):
            for combo in combinations(cards, combo_size):
                combo_list = list(combo)
                
                # 检查组合的有效性
                if _is_valid_card_combination(combo_list):
                    yield combo_list
                    
                # 限制组合数量以避免性能问题
                if combo_size > 5:  # 最多5张卡的组合
                    break
                    
    except Exception as e:
        # 如果出错，至少返回单张卡牌
        for card in cards[:min_combo_size]:
            yield [card]

def generate_game_events(game_state) -> Generator[Dict[str, Any], None, None]:
    """
    生成游戏事件（事件驱动）
    
    Args:
        game_state: 游戏状态
        
    Yields:
        游戏事件字典
    """
    try:
        current_player = game_state.get_current_player()
        
        # 回合开始事件
        yield {
            "type": "turn_start",
            "player": current_player.name,
            "turn": getattr(game_state, 'turn', 1),
            "timestamp": "current"
        }
        
        # 资源检查事件
        qi = getattr(current_player, 'qi', 0)
        dao_xing = getattr(current_player, 'dao_xing', 0)
        cheng_yi = getattr(current_player, 'cheng_yi', 0)
        
        if qi <= 2:
            yield {
                "type": "low_resource_warning",
                "resource": "qi",
                "current_value": qi,
                "player": current_player.name,
                "severity": "high" if qi == 0 else "medium"
            }
            
        if dao_xing >= 15:
            yield {
                "type": "high_cultivation_achieved",
                "resource": "dao_xing",
                "current_value": dao_xing,
                "player": current_player.name,
                "milestone": True
            }
            
        # 手牌事件
        hand_size = len(getattr(current_player, 'hand', []))
        if hand_size == 0:
            yield {
                "type": "empty_hand",
                "player": current_player.name,
                "suggestion": "consider_study_action"
            }
        elif hand_size > 7:
            yield {
                "type": "hand_overflow",
                "player": current_player.name,
                "hand_size": hand_size,
                "suggestion": "play_cards"
            }
            
        # 位置相关事件
        position = getattr(current_player, 'position', None)
        if position:
            yield {
                "type": "position_update",
                "player": current_player.name,
                "position": position,
                "zone_effects": _get_zone_effects(position)
            }
            
        # 成就检查事件
        achievements = getattr(current_player, 'achievements', [])
        if len(achievements) > 0:
            yield {
                "type": "achievement_status",
                "player": current_player.name,
                "achievement_count": len(achievements),
                "latest_achievement": achievements[-1] if achievements else None
            }
            
        # 游戏阶段事件
        if hasattr(game_state, 'phase'):
            yield {
                "type": "game_phase",
                "current_phase": game_state.phase,
                "description": _get_phase_description(game_state.phase)
            }
            
        # 特殊条件事件
        if qi > 8 and dao_xing > 10:
            yield {
                "type": "powerful_state",
                "player": current_player.name,
                "qi": qi,
                "dao_xing": dao_xing,
                "special_actions_available": True
            }
            
        # 回合结束预警事件
        yield {
            "type": "turn_end_approaching",
            "player": current_player.name,
            "actions_remaining": "check_action_count",
            "recommendations": _get_turn_end_recommendations(current_player)
        }
        
    except Exception as e:
        # 默认事件
        yield {
            "type": "error_event",
            "message": "事件生成出错",
            "fallback": True
        }

# ==================== 辅助函数 ====================

def _calculate_action_cost(action_type: ActionType, player) -> int:
    """计算行动成本"""
    base_costs = {
        ActionType.PLAY_CARD: 1,
        ActionType.MOVE: 1,
        ActionType.STUDY: 1,
        ActionType.MEDITATE: 0,
        ActionType.PASS: 0
    }
    return base_costs.get(action_type, 1)

def _get_action_description(action_type: ActionType, context: Dict[str, Any]) -> str:
    """获取行动描述"""
    descriptions = {
        ActionType.PLAY_CARD: f"打出卡牌: {context.get('card_name', '未知卡牌')}",
        ActionType.MOVE: f"移动到: {context.get('target_position', '未知位置')}",
        ActionType.STUDY: "学习 - 消耗气获得诚意",
        ActionType.MEDITATE: "冥想 - 获得气",
        ActionType.PASS: "跳过回合"
    }
    return descriptions.get(action_type, "未知行动")

def _evaluate_move(move: Dict[str, Any], game_state) -> float:
    """评估行动价值"""
    base_value = 1.0
    
    if move['type'] == ActionType.PLAY_CARD:
        base_value += 2.0  # 打牌通常比较有价值
    elif move['type'] == ActionType.MEDITATE:
        base_value += 1.5  # 冥想获得资源
    elif move['type'] == ActionType.STUDY:
        base_value += 1.8  # 学习获得道行
    
    # 考虑成本
    cost = move.get('cost', 0)
    if cost > 0:
        base_value -= cost * 0.1
    
    return base_value

def _simulate_move(game_state, move: Dict[str, Any]):
    """模拟执行行动后的游戏状态"""
    # 这里应该返回一个新的游戏状态副本
    # 为了简化，暂时返回None
    return None

def _is_valid_card_combination(cards: List) -> bool:
    """检查卡牌组合是否有效"""
    if not cards:
        return False
    
    # 基本有效性检查
    if len(cards) > 5:  # 最多5张卡的组合
        return False
        
    # 检查卡牌类型兼容性
    card_types = set()
    for card in cards:
        card_type = getattr(card, 'type', None) or getattr(card, 'card_type', 'unknown')
        card_types.add(card_type)
    
    # 某些类型不能组合
    incompatible_combinations = {
        frozenset(['attack', 'defense']),  # 攻击和防御卡不能组合
        frozenset(['instant', 'permanent'])  # 瞬发和永久卡不能组合
    }
    
    for incompatible in incompatible_combinations:
        if incompatible.issubset(card_types):
            return False
            
    return True

def _get_zone_effects(position) -> Dict[str, Any]:
    """获取区域效果"""
    zone_effects = {
        'center': {'qi_bonus': 1, 'description': '中心区域 - 气+1'},
        'north': {'dao_xing_bonus': 1, 'description': '北方区域 - 道行+1'},
        'south': {'cheng_yi_bonus': 1, 'description': '南方区域 - 诚意+1'},
        'east': {'card_draw_bonus': 1, 'description': '东方区域 - 抽卡+1'},
        'west': {'meditation_bonus': 1, 'description': '西方区域 - 冥想效果+1'}
    }
    return zone_effects.get(str(position).lower(), {'description': '普通区域'})

def _get_phase_description(phase) -> str:
    """获取游戏阶段描述"""
    phase_descriptions = {
        'setup': '游戏准备阶段',
        'early_game': '游戏初期阶段',
        'mid_game': '游戏中期阶段',
        'late_game': '游戏后期阶段',
        'endgame': '游戏结束阶段'
    }
    return phase_descriptions.get(str(phase).lower(), '未知阶段')

def _get_turn_end_recommendations(player) -> List[str]:
    """获取回合结束建议"""
    recommendations = []
    
    qi = getattr(player, 'qi', 0)
    dao_xing = getattr(player, 'dao_xing', 0)
    hand_size = len(getattr(player, 'hand', []))
    
    if qi < 3:
        recommendations.append("考虑冥想以恢复气")
    if dao_xing < 5:
        recommendations.append("考虑学习以提升道行")
    if hand_size > 5:
        recommendations.append("考虑打出一些卡牌")
    if hand_size == 0:
        recommendations.append("考虑学习以获得新卡牌")
        
    if not recommendations:
        recommendations.append("当前状态良好，可以执行任何行动")
        
    return recommendations

def _is_valid_combo(combo: List) -> bool:
    """检查卡牌组合是否有效"""
    # 简单的组合验证逻辑
    if len(combo) < 2:
        return False
    
    # 检查是否有协同效应
    card_types = [getattr(card, 'type', None) for card in combo]
    if len(set(card_types)) == 1:  # 同类型卡牌
        return True
    
    return False

# ==================== 数据类定义 ====================

@dataclass
class ActionResult:
    """行动结果数据类"""
    success: bool
    message: str
    resource_changes: Dict[ResourceType, int]
    state_changes: List[PlayerState]
    
@dataclass
class GameEvent:
    """游戏事件数据类"""
    event_type: str
    timestamp: float
    player: Optional[str]
    description: str
    data: Dict[str, Any]

# ==================== 导出接口 ====================

__all__ = [
    # 枚举
    'CardType', 'PlayerState', 'GamePhase', 'ActionType', 
    'ResourceType', 'MessageType', 'CardRarity', 'ZoneType',
    
    # 装饰器
    'require_resource', 'log_action', 'performance_monitor',
    'validate_game_state', 'retry_on_failure',
    
    # 生成器
    'generate_possible_moves', 'generate_ai_strategies',
    'generate_card_combinations', 'generate_game_events',
    
    # 数据类
    'ActionResult', 'GameEvent'
]