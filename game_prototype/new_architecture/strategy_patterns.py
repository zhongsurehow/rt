"""
策略模式框架 - 重构胜利条件、AI行为等复杂算法
将复杂的if/else逻辑封装为独立的策略对象，提高代码的可维护性和扩展性
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random
import json

# 游戏状态和玩家数据结构
@dataclass
class PlayerState:
    """玩家状态"""
    player_id: str
    health: int = 100
    energy: int = 100
    dao: int = 0
    yang: int = 0
    yin: int = 0
    wisdom: int = 0
    luck: int = 0
    cards_in_hand: List[str] = None
    active_buffs: List[Dict] = None
    active_debuffs: List[Dict] = None
    
    def __post_init__(self):
        if self.cards_in_hand is None:
            self.cards_in_hand = []
        if self.active_buffs is None:
            self.active_buffs = []
        if self.active_debuffs is None:
            self.active_debuffs = []

@dataclass
class GameState:
    """游戏状态"""
    players: Dict[str, PlayerState]
    turn_number: int = 1
    current_player: str = ""
    game_phase: str = "playing"
    special_conditions: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.special_conditions is None:
            self.special_conditions = {}

class Difficulty(Enum):
    """AI难度等级"""
    EASY = 1
    NORMAL = 2
    HARD = 3
    EXPERT = 4

# ==================== 胜利条件策略 ====================

class VictoryStrategy(ABC):
    """胜利条件策略基类"""
    
    @abstractmethod
    def check_victory(self, game_state: GameState, player_id: str) -> bool:
        """检查是否满足胜利条件"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """获取胜利条件描述"""
        pass
    
    @abstractmethod
    def get_progress(self, game_state: GameState, player_id: str) -> float:
        """获取胜利进度 (0.0 - 1.0)"""
        pass

class TraditionalVictory(VictoryStrategy):
    """传统胜利条件：道值达到100"""
    
    def __init__(self, target_dao: int = 100):
        self.target_dao = target_dao
    
    def check_victory(self, game_state: GameState, player_id: str) -> bool:
        player = game_state.players.get(player_id)
        return player and player.dao >= self.target_dao
    
    def get_description(self) -> str:
        return f"道值达到{self.target_dao}点"
    
    def get_progress(self, game_state: GameState, player_id: str) -> float:
        player = game_state.players.get(player_id)
        if not player:
            return 0.0
        return min(1.0, player.dao / self.target_dao)

class YinYangMastery(VictoryStrategy):
    """阴阳大师胜利：阴阳平衡保持5回合"""
    
    def __init__(self, balance_turns: int = 5, balance_threshold: int = 5):
        self.balance_turns = balance_turns
        self.balance_threshold = balance_threshold
    
    def check_victory(self, game_state: GameState, player_id: str) -> bool:
        # 检查特殊条件中的阴阳平衡回合数
        balance_count = game_state.special_conditions.get(f"{player_id}_balance_turns", 0)
        return balance_count >= self.balance_turns
    
    def get_description(self) -> str:
        return f"阴阳平衡保持{self.balance_turns}回合"
    
    def get_progress(self, game_state: GameState, player_id: str) -> float:
        balance_count = game_state.special_conditions.get(f"{player_id}_balance_turns", 0)
        return min(1.0, balance_count / self.balance_turns)

class ElementalSupremacy(VictoryStrategy):
    """元素至上胜利：某一元素达到极高值"""
    
    def __init__(self, element: str = "yang", target_value: int = 80):
        self.element = element
        self.target_value = target_value
    
    def check_victory(self, game_state: GameState, player_id: str) -> bool:
        player = game_state.players.get(player_id)
        if not player:
            return False
        
        element_value = getattr(player, self.element, 0)
        return element_value >= self.target_value
    
    def get_description(self) -> str:
        return f"{self.element}元素达到{self.target_value}点"
    
    def get_progress(self, game_state: GameState, player_id: str) -> float:
        player = game_state.players.get(player_id)
        if not player:
            return 0.0
        
        element_value = getattr(player, self.element, 0)
        return min(1.0, element_value / self.target_value)

class WisdomEnlightenment(VictoryStrategy):
    """智慧开悟胜利：智慧值达到100且使用特定卡牌组合"""
    
    def __init__(self, wisdom_threshold: int = 100, required_cards: List[str] = None):
        self.wisdom_threshold = wisdom_threshold
        self.required_cards = required_cards or ["qian_card", "kun_card", "li_card"]
    
    def check_victory(self, game_state: GameState, player_id: str) -> bool:
        player = game_state.players.get(player_id)
        if not player or player.wisdom < self.wisdom_threshold:
            return False
        
        # 检查是否使用过所需的卡牌组合
        used_cards = game_state.special_conditions.get(f"{player_id}_used_cards", set())
        return all(card in used_cards for card in self.required_cards)
    
    def get_description(self) -> str:
        return f"智慧达到{self.wisdom_threshold}点并使用特定卡牌组合"
    
    def get_progress(self, game_state: GameState, player_id: str) -> float:
        player = game_state.players.get(player_id)
        if not player:
            return 0.0
        
        wisdom_progress = min(1.0, player.wisdom / self.wisdom_threshold)
        
        used_cards = game_state.special_conditions.get(f"{player_id}_used_cards", set())
        card_progress = len([card for card in self.required_cards if card in used_cards]) / len(self.required_cards)
        
        return (wisdom_progress + card_progress) / 2

class SurvivalVictory(VictoryStrategy):
    """生存胜利：在指定回合数内存活"""
    
    def __init__(self, survival_turns: int = 20):
        self.survival_turns = survival_turns
    
    def check_victory(self, game_state: GameState, player_id: str) -> bool:
        player = game_state.players.get(player_id)
        return (player and player.health > 0 and 
                game_state.turn_number >= self.survival_turns)
    
    def get_description(self) -> str:
        return f"存活{self.survival_turns}回合"
    
    def get_progress(self, game_state: GameState, player_id: str) -> float:
        return min(1.0, game_state.turn_number / self.survival_turns)

# ==================== AI行为策略 ====================

class AIStrategy(ABC):
    """AI策略基类"""
    
    @abstractmethod
    def choose_action(self, game_state: GameState, ai_player_id: str) -> Dict[str, Any]:
        """选择行动"""
        pass
    
    @abstractmethod
    def evaluate_game_state(self, game_state: GameState, ai_player_id: str) -> float:
        """评估游戏状态 (-1.0 到 1.0，负数表示不利，正数表示有利)"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """获取策略名称"""
        pass

class AggressiveAI(AIStrategy):
    """激进AI策略：优先攻击和快速获胜"""
    
    def __init__(self, difficulty: Difficulty = Difficulty.NORMAL):
        self.difficulty = difficulty
        self.aggression_factor = {
            Difficulty.EASY: 0.6,
            Difficulty.NORMAL: 0.8,
            Difficulty.HARD: 0.9,
            Difficulty.EXPERT: 1.0
        }[difficulty]
    
    def choose_action(self, game_state: GameState, ai_player_id: str) -> Dict[str, Any]:
        ai_player = game_state.players[ai_player_id]
        available_cards = ai_player.cards_in_hand
        
        if not available_cards:
            return {"action": "pass", "reason": "no_cards"}
        
        # 优先选择攻击性卡牌
        attack_cards = [card for card in available_cards if "attack" in card.lower() or "damage" in card.lower()]
        
        if attack_cards and random.random() < self.aggression_factor:
            chosen_card = random.choice(attack_cards)
            target = self._choose_target(game_state, ai_player_id)
            return {
                "action": "play_card",
                "card": chosen_card,
                "target": target,
                "reason": "aggressive_play"
            }
        
        # 否则选择最有价值的卡牌
        best_card = self._evaluate_cards(available_cards, game_state, ai_player_id)
        return {
            "action": "play_card",
            "card": best_card,
            "target": self._choose_target(game_state, ai_player_id),
            "reason": "best_value"
        }
    
    def evaluate_game_state(self, game_state: GameState, ai_player_id: str) -> float:
        ai_player = game_state.players[ai_player_id]
        opponents = [p for pid, p in game_state.players.items() if pid != ai_player_id]
        
        if not opponents:
            return 1.0
        
        # 评估相对优势
        ai_power = ai_player.dao + ai_player.yang + ai_player.health * 0.5
        avg_opponent_power = sum(p.dao + p.yang + p.health * 0.5 for p in opponents) / len(opponents)
        
        advantage = (ai_power - avg_opponent_power) / max(avg_opponent_power, 1)
        return max(-1.0, min(1.0, advantage))
    
    def get_strategy_name(self) -> str:
        return f"激进AI ({self.difficulty.name})"
    
    def _choose_target(self, game_state: GameState, ai_player_id: str) -> str:
        """选择目标"""
        opponents = [pid for pid in game_state.players.keys() if pid != ai_player_id]
        if not opponents:
            return ai_player_id
        
        # 选择生命值最低的对手
        target = min(opponents, key=lambda pid: game_state.players[pid].health)
        return target
    
    def _evaluate_cards(self, cards: List[str], game_state: GameState, ai_player_id: str) -> str:
        """评估卡牌价值"""
        if not cards:
            return ""
        
        # 简化评估：随机选择
        return random.choice(cards)

class DefensiveAI(AIStrategy):
    """防御AI策略：优先防御和稳健发展"""
    
    def __init__(self, difficulty: Difficulty = Difficulty.NORMAL):
        self.difficulty = difficulty
        self.caution_factor = {
            Difficulty.EASY: 0.8,
            Difficulty.NORMAL: 0.7,
            Difficulty.HARD: 0.6,
            Difficulty.EXPERT: 0.5
        }[difficulty]
    
    def choose_action(self, game_state: GameState, ai_player_id: str) -> Dict[str, Any]:
        ai_player = game_state.players[ai_player_id]
        available_cards = ai_player.cards_in_hand
        
        if not available_cards:
            return {"action": "pass", "reason": "no_cards"}
        
        # 如果生命值低，优先治疗
        if ai_player.health < 50:
            heal_cards = [card for card in available_cards if "heal" in card.lower() or "restore" in card.lower()]
            if heal_cards:
                return {
                    "action": "play_card",
                    "card": random.choice(heal_cards),
                    "target": ai_player_id,
                    "reason": "defensive_heal"
                }
        
        # 优先防御性卡牌
        defense_cards = [card for card in available_cards if "shield" in card.lower() or "protect" in card.lower()]
        
        if defense_cards and random.random() < self.caution_factor:
            return {
                "action": "play_card",
                "card": random.choice(defense_cards),
                "target": ai_player_id,
                "reason": "defensive_play"
            }
        
        # 选择最安全的卡牌
        safe_card = self._choose_safe_card(available_cards, game_state, ai_player_id)
        return {
            "action": "play_card",
            "card": safe_card,
            "target": ai_player_id,
            "reason": "safe_play"
        }
    
    def evaluate_game_state(self, game_state: GameState, ai_player_id: str) -> float:
        ai_player = game_state.players[ai_player_id]
        
        # 重视生存能力
        health_factor = ai_player.health / 100.0
        stability_factor = (ai_player.yin + ai_player.wisdom) / 200.0
        
        return (health_factor + stability_factor) / 2 - 0.5
    
    def get_strategy_name(self) -> str:
        return f"防御AI ({self.difficulty.name})"
    
    def _choose_safe_card(self, cards: List[str], game_state: GameState, ai_player_id: str) -> str:
        """选择最安全的卡牌"""
        if not cards:
            return ""
        
        # 简化实现：避免攻击性卡牌
        safe_cards = [card for card in cards if "attack" not in card.lower() and "damage" not in card.lower()]
        return random.choice(safe_cards if safe_cards else cards)

class BalancedAI(AIStrategy):
    """平衡AI策略：根据情况调整策略"""
    
    def __init__(self, difficulty: Difficulty = Difficulty.NORMAL):
        self.difficulty = difficulty
        self.adaptability = {
            Difficulty.EASY: 0.3,
            Difficulty.NORMAL: 0.5,
            Difficulty.HARD: 0.7,
            Difficulty.EXPERT: 0.9
        }[difficulty]
    
    def choose_action(self, game_state: GameState, ai_player_id: str) -> Dict[str, Any]:
        ai_player = game_state.players[ai_player_id]
        available_cards = ai_player.cards_in_hand
        
        if not available_cards:
            return {"action": "pass", "reason": "no_cards"}
        
        # 根据当前状态选择策略
        game_evaluation = self.evaluate_game_state(game_state, ai_player_id)
        
        if game_evaluation < -0.3:  # 劣势，采用防御策略
            return self._defensive_action(available_cards, game_state, ai_player_id)
        elif game_evaluation > 0.3:  # 优势，采用攻击策略
            return self._aggressive_action(available_cards, game_state, ai_player_id)
        else:  # 平衡，采用发展策略
            return self._development_action(available_cards, game_state, ai_player_id)
    
    def evaluate_game_state(self, game_state: GameState, ai_player_id: str) -> float:
        ai_player = game_state.players[ai_player_id]
        opponents = [p for pid, p in game_state.players.items() if pid != ai_player_id]
        
        if not opponents:
            return 1.0
        
        # 综合评估
        health_ratio = ai_player.health / max(sum(p.health for p in opponents) / len(opponents), 1)
        dao_ratio = ai_player.dao / max(sum(p.dao for p in opponents) / len(opponents), 1)
        resource_ratio = (ai_player.yang + ai_player.yin) / max(sum(p.yang + p.yin for p in opponents) / len(opponents), 1)
        
        overall_ratio = (health_ratio + dao_ratio + resource_ratio) / 3
        return max(-1.0, min(1.0, (overall_ratio - 1.0) * 2))
    
    def get_strategy_name(self) -> str:
        return f"平衡AI ({self.difficulty.name})"
    
    def _defensive_action(self, cards: List[str], game_state: GameState, ai_player_id: str) -> Dict[str, Any]:
        """防御性行动"""
        defense_cards = [card for card in cards if any(keyword in card.lower() for keyword in ["heal", "shield", "protect", "restore"])]
        
        if defense_cards:
            return {
                "action": "play_card",
                "card": random.choice(defense_cards),
                "target": ai_player_id,
                "reason": "defensive_strategy"
            }
        
        return {
            "action": "play_card",
            "card": random.choice(cards),
            "target": ai_player_id,
            "reason": "fallback_defensive"
        }
    
    def _aggressive_action(self, cards: List[str], game_state: GameState, ai_player_id: str) -> Dict[str, Any]:
        """攻击性行动"""
        attack_cards = [card for card in cards if any(keyword in card.lower() for keyword in ["attack", "damage", "strike"])]
        
        if attack_cards:
            opponents = [pid for pid in game_state.players.keys() if pid != ai_player_id]
            target = random.choice(opponents) if opponents else ai_player_id
            
            return {
                "action": "play_card",
                "card": random.choice(attack_cards),
                "target": target,
                "reason": "aggressive_strategy"
            }
        
        return {
            "action": "play_card",
            "card": random.choice(cards),
            "target": ai_player_id,
            "reason": "fallback_aggressive"
        }
    
    def _development_action(self, cards: List[str], game_state: GameState, ai_player_id: str) -> Dict[str, Any]:
        """发展性行动"""
        development_cards = [card for card in cards if any(keyword in card.lower() for keyword in ["draw", "wisdom", "dao", "energy"])]
        
        if development_cards:
            return {
                "action": "play_card",
                "card": random.choice(development_cards),
                "target": ai_player_id,
                "reason": "development_strategy"
            }
        
        return {
            "action": "play_card",
            "card": random.choice(cards),
            "target": ai_player_id,
            "reason": "fallback_development"
        }

# ==================== 策略管理器 ====================

class StrategyManager:
    """策略管理器"""
    
    def __init__(self):
        self.victory_strategies: Dict[str, VictoryStrategy] = {}
        self.ai_strategies: Dict[str, AIStrategy] = {}
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """注册默认策略"""
        # 胜利条件策略
        self.register_victory_strategy("traditional", TraditionalVictory())
        self.register_victory_strategy("yin_yang_mastery", YinYangMastery())
        self.register_victory_strategy("elemental_yang", ElementalSupremacy("yang", 80))
        self.register_victory_strategy("elemental_yin", ElementalSupremacy("yin", 80))
        self.register_victory_strategy("wisdom_enlightenment", WisdomEnlightenment())
        self.register_victory_strategy("survival", SurvivalVictory())
        
        # AI策略
        for difficulty in Difficulty:
            self.register_ai_strategy(f"aggressive_{difficulty.name.lower()}", AggressiveAI(difficulty))
            self.register_ai_strategy(f"defensive_{difficulty.name.lower()}", DefensiveAI(difficulty))
            self.register_ai_strategy(f"balanced_{difficulty.name.lower()}", BalancedAI(difficulty))
    
    def register_victory_strategy(self, name: str, strategy: VictoryStrategy):
        """注册胜利条件策略"""
        self.victory_strategies[name] = strategy
    
    def register_ai_strategy(self, name: str, strategy: AIStrategy):
        """注册AI策略"""
        self.ai_strategies[name] = strategy
    
    def get_victory_strategy(self, name: str) -> Optional[VictoryStrategy]:
        """获取胜利条件策略"""
        return self.victory_strategies.get(name)
    
    def get_ai_strategy(self, name: str) -> Optional[AIStrategy]:
        """获取AI策略"""
        return self.ai_strategies.get(name)
    
    def list_victory_strategies(self) -> List[str]:
        """列出所有胜利条件策略"""
        return list(self.victory_strategies.keys())
    
    def list_ai_strategies(self) -> List[str]:
        """列出所有AI策略"""
        return list(self.ai_strategies.keys())
    
    def check_all_victory_conditions(self, game_state: GameState, player_id: str, 
                                   active_strategies: List[str] = None) -> Dict[str, bool]:
        """检查所有胜利条件"""
        if active_strategies is None:
            active_strategies = list(self.victory_strategies.keys())
        
        results = {}
        for strategy_name in active_strategies:
            if strategy_name in self.victory_strategies:
                strategy = self.victory_strategies[strategy_name]
                results[strategy_name] = strategy.check_victory(game_state, player_id)
        
        return results
    
    def get_victory_progress(self, game_state: GameState, player_id: str,
                           active_strategies: List[str] = None) -> Dict[str, float]:
        """获取所有胜利条件的进度"""
        if active_strategies is None:
            active_strategies = list(self.victory_strategies.keys())
        
        progress = {}
        for strategy_name in active_strategies:
            if strategy_name in self.victory_strategies:
                strategy = self.victory_strategies[strategy_name]
                progress[strategy_name] = strategy.get_progress(game_state, player_id)
        
        return progress

# 全局策略管理器实例
_global_strategy_manager = None

def get_strategy_manager() -> StrategyManager:
    """获取全局策略管理器实例"""
    global _global_strategy_manager
    if _global_strategy_manager is None:
        _global_strategy_manager = StrategyManager()
    return _global_strategy_manager