"""
AI决策优化模块
使用生成器模式实现惰性求值，优化AI决策和可能行动的计算
"""

from typing import Iterator, Dict, Any, List, Tuple, Optional
import random
import logging
from dataclasses import dataclass
from game_state import GameState, Player, Zone
from elegant_patterns import (
    ActionType, ResourceType, PlayerState, GamePhase,
    performance_monitor, log_action, ActionResult
)

@dataclass
class DecisionContext:
    """决策上下文"""
    player: Player
    game_state: GameState
    available_resources: Dict[ResourceType, int]
    strategic_goals: List[str]
    risk_tolerance: float = 0.5
    
@dataclass
class ActionCandidate:
    """行动候选"""
    action_type: ActionType
    priority: float
    expected_outcome: float
    resource_cost: Dict[ResourceType, int]
    description: str
    args: Dict[str, Any]

class AIDecisionOptimizer:
    """AI决策优化器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    @performance_monitor(threshold_ms=200.0)
    def generate_strategic_moves(self, context: DecisionContext) -> Iterator[ActionCandidate]:
        """
        生成战略行动候选
        
        Args:
            context: 决策上下文
            
        Yields:
            行动候选
        """
        # 惰性生成各种类型的行动
        yield from self._generate_resource_actions(context)
        yield from self._generate_card_actions(context)
        yield from self._generate_movement_actions(context)
        yield from self._generate_special_actions(context)
        
    def _generate_resource_actions(self, context: DecisionContext) -> Iterator[ActionCandidate]:
        """生成资源相关行动"""
        player = context.player
        
        # 冥想行动
        if player.qi < 5:  # 气不足时优先冥想
            yield ActionCandidate(
                action_type=ActionType.MEDITATE,
                priority=0.8,
                expected_outcome=0.7,
                resource_cost={},
                description="冥想获得气",
                args={}
            )
            
        # 学习行动
        if player.cheng_yi < 3 and player.qi >= 1:
            yield ActionCandidate(
                action_type=ActionType.STUDY,
                priority=0.6,
                expected_outcome=0.6,
                resource_cost={ResourceType.QI: 1},
                description="学习获得诚意",
                args={}
            )
            
    def _generate_card_actions(self, context: DecisionContext) -> Iterator[ActionCandidate]:
        """生成卡牌相关行动"""
        player = context.player
        
        # 为每张手牌生成打出行动
        for i, card in enumerate(player.hand):
            for zone in card.associated_guas:
                # 计算在该区域打出的优先级
                priority = self._calculate_card_play_priority(card, zone, context)
                
                yield ActionCandidate(
                    action_type=ActionType.PLAY_CARD,
                    priority=priority,
                    expected_outcome=priority * 0.8,
                    resource_cost={ResourceType.QI: 1},
                    description=f"打出 {card.name} 到 {zone}",
                    args={"card_index": i, "zone": zone}
                )
                
    def _generate_movement_actions(self, context: DecisionContext) -> Iterator[ActionCandidate]:
        """生成移动行动"""
        player = context.player
        current_zone = player.position
        
        # 生成到其他区域的移动
        for zone in Zone:
            if zone != current_zone:
                priority = self._calculate_movement_priority(zone, context)
                
                yield ActionCandidate(
                    action_type=ActionType.MOVE,
                    priority=priority,
                    expected_outcome=priority * 0.5,
                    resource_cost={ResourceType.AP: 1, ResourceType.QI: 1},
                    description=f"移动到 {zone.value}",
                    args={"target_zone": zone}
                )
                
    def _generate_special_actions(self, context: DecisionContext) -> Iterator[ActionCandidate]:
        """生成特殊行动"""
        player = context.player
        
        # 变卦行动
        if player.cheng_yi >= 3:
            yield ActionCandidate(
                action_type=ActionType.SPECIAL,
                priority=0.4,
                expected_outcome=0.6,
                resource_cost={ResourceType.AP: 1},
                description="变卦转换",
                args={"action": "biangua"}
            )
            
        # 占卜行动
        if player.qi >= 3:
            yield ActionCandidate(
                action_type=ActionType.SPECIAL,
                priority=0.3,
                expected_outcome=0.5,
                resource_cost={ResourceType.QI: 3},
                description="占卜运势",
                args={"action": "divine_fortune"}
            )
            
    @performance_monitor(threshold_ms=100.0)
    def generate_ai_strategies(self, context: DecisionContext, max_depth: int = 3) -> Iterator[List[ActionCandidate]]:
        """
        生成AI策略序列
        
        Args:
            context: 决策上下文
            max_depth: 最大策略深度
            
        Yields:
            策略序列（行动候选列表）
        """
        # 生成单步策略
        for action in self.generate_strategic_moves(context):
            yield [action]
            
        # 生成多步策略（如果深度允许）
        if max_depth > 1:
            yield from self._generate_multi_step_strategies(context, max_depth)
            
    def _generate_multi_step_strategies(self, context: DecisionContext, max_depth: int) -> Iterator[List[ActionCandidate]]:
        """生成多步策略"""
        # 获取高优先级的第一步行动
        first_actions = list(self.generate_strategic_moves(context))
        high_priority_actions = [a for a in first_actions if a.priority > 0.6]
        
        for first_action in high_priority_actions[:5]:  # 限制分支数量
            # 模拟执行第一步后的状态
            simulated_context = self._simulate_action_result(context, first_action)
            
            # 生成后续行动
            for second_action in self.generate_strategic_moves(simulated_context):
                if second_action.priority > 0.4:  # 只考虑中等以上优先级
                    strategy = [first_action, second_action]
                    yield strategy
                    
                    # 如果还有深度，继续生成
                    if max_depth > 2:
                        third_context = self._simulate_action_result(simulated_context, second_action)
                        for third_action in self.generate_strategic_moves(third_context):
                            if third_action.priority > 0.3:
                                yield [first_action, second_action, third_action]
                                
    @performance_monitor(threshold_ms=50.0)
    def evaluate_strategy_sequence(self, strategy: List[ActionCandidate], context: DecisionContext) -> float:
        """
        评估策略序列的总体价值
        
        Args:
            strategy: 策略序列
            context: 决策上下文
            
        Returns:
            策略价值评分
        """
        if not strategy:
            return 0.0
            
        total_value = 0.0
        current_context = context
        decay_factor = 0.9  # 后续行动的价值衰减
        
        for i, action in enumerate(strategy):
            # 检查资源是否足够
            if not self._can_afford_action(action, current_context):
                return total_value * 0.5  # 无法执行的策略价值减半
                
            # 计算行动价值
            action_value = action.expected_outcome * (decay_factor ** i)
            total_value += action_value
            
            # 更新上下文（简化模拟）
            current_context = self._simulate_action_result(current_context, action)
            
        return total_value
        
    def _calculate_card_play_priority(self, card, zone: str, context: DecisionContext) -> float:
        """计算卡牌打出的优先级"""
        base_priority = 0.5
        
        # 根据区域控制情况调整优先级
        zone_data = context.game_state.board.gua_zones.get(zone, {})
        markers = zone_data.get("markers", {})
        
        # 如果该区域没有我方标记，优先级提高
        player_markers = markers.get(context.player.name, 0)
        if player_markers == 0:
            base_priority += 0.3
            
        # 如果对手在该区域有优势，优先级提高
        max_opponent_markers = max([markers.get(name, 0) for name in markers if name != context.player.name] + [0])
        if max_opponent_markers > player_markers:
            base_priority += 0.2
            
        return min(1.0, base_priority)
        
    def _calculate_movement_priority(self, target_zone: Zone, context: DecisionContext) -> float:
        """计算移动的优先级"""
        base_priority = 0.3
        
        # 根据目标区域的特性调整优先级
        if target_zone == Zone.TIAN:  # 天域适合冥想
            if context.player.qi < 5:
                base_priority += 0.4
        elif target_zone == Zone.REN:  # 人域适合学习
            if context.player.cheng_yi < 3:
                base_priority += 0.3
        elif target_zone == Zone.DI:  # 地域平衡
            base_priority += 0.1
            
        return min(1.0, base_priority)
        
    def _can_afford_action(self, action: ActionCandidate, context: DecisionContext) -> bool:
        """检查是否有足够资源执行行动"""
        for resource_type, cost in action.resource_cost.items():
            available = context.available_resources.get(resource_type, 0)
            if available < cost:
                return False
        return True
        
    def _simulate_action_result(self, context: DecisionContext, action: ActionCandidate) -> DecisionContext:
        """模拟行动结果，返回新的上下文"""
        # 简化的模拟，实际实现可能更复杂
        new_resources = context.available_resources.copy()
        
        # 扣除资源成本
        for resource_type, cost in action.resource_cost.items():
            new_resources[resource_type] = max(0, new_resources.get(resource_type, 0) - cost)
            
        # 根据行动类型添加收益
        if action.action_type == ActionType.MEDITATE:
            new_resources[ResourceType.QI] = new_resources.get(ResourceType.QI, 0) + 2
        elif action.action_type == ActionType.STUDY:
            # 学习增加诚意（这里简化处理）
            pass
            
        return DecisionContext(
            player=context.player,
            game_state=context.game_state,
            available_resources=new_resources,
            strategic_goals=context.strategic_goals,
            risk_tolerance=context.risk_tolerance
        )

# 导出接口
__all__ = [
    'AIDecisionOptimizer',
    'DecisionContext', 
    'ActionCandidate'
]