from enum import Enum, auto
from typing import Optional, List, Dict
import logging

from card_base import GuaCard
from yijing_mechanics import YinYangBalance, WuXing

# 导入优雅编程模式
from elegant_patterns import (
    PlayerState, GamePhase, ActionType,
    log_action, performance_monitor, validate_game_state
)

# --- Core Enums ---
# Defining these here avoids circular dependencies.
class AvatarName(Enum):
    EMPEROR = "帝王"
    HERMIT = "隐士"

class BonusType(Enum):
    EXTRA_AP = auto()
    EXTRA_QI = auto()
    DRAW_CARD = auto()
    HAND_LIMIT = auto()
    EXTRA_INFLUENCE = auto()
    FREE_STUDY = auto()
    QI_DISCOUNT = auto()
    DAO_XING_ON_TASK = auto()

class Zone(Enum):
    """Enumeration for the board zones."""
    DI = "地"
    REN = "人"
    TIAN = "天"
    TAIJI = "太极"

from dataclasses import dataclass, field

@dataclass
class Modifiers:
    """A data class to hold all temporary modifications for a player's turn."""
    qi_discount: int = 0
    extra_ap: int = 0
    extra_influence: int = 0
    extra_dao_xing_on_task: int = 0
    cards_to_draw_on_study: int = 2
    has_free_study: bool = False
    hand_limit_bonus: int = 0
    empower_cost_increase: int = 0
    extra_qi_gain: int = 0

# --- Core Data Classes ---
class Avatar:
    """Represents a player's Avatar with unique abilities."""
    def __init__(self, name: AvatarName, description: str, ability_description: str):
        self.name = name
        self.description = description
        self.ability_description = ability_description

class Player:
    """Represents a player in the game."""
    def __init__(self, name: str, avatar: Avatar):
        self.name = name
        self.avatar = avatar
        self.dao_xing: int = 0
        self.cheng_yi: int = 0
        self.qi: int = 0
        self.hand: list[GuaCard] = []
        self.position: Zone = Zone.DI
        self.influence_markers: int = 15
        self.current_task_card: Optional[GuaCard] = None
        self.placed_influence_this_turn: bool = False
        self.destiny_chart: list = [] # List of Tian Shi cards
        
        # 易经哲学属性
        self.yin_yang_balance: YinYangBalance = YinYangBalance()
        self.wuxing_affinities: Dict[WuXing, int] = {
            WuXing.JIN: 0, WuXing.MU: 0, WuXing.SHUI: 0, 
            WuXing.HUO: 0, WuXing.TU: 0
        }
        self.active_wisdom: List[str] = []  # 激活的智慧格言
        self.transformation_history: List[str] = []  # 变卦历史
        
        # 玩家状态
        self.state: PlayerState = PlayerState.ACTIVE
        
    @log_action(ActionType.RESOURCE_CHANGE)
    @performance_monitor(threshold_ms=20.0)
    def modify_qi(self, amount: int) -> None:
        """
        修改玩家的气值
        
        Args:
            amount: 变化量（正数增加，负数减少）
        """
        old_qi = self.qi
        self.qi = max(0, self.qi + amount)
        logging.info(f"玩家 {self.name} 气值变化: {old_qi} -> {self.qi} (变化: {amount})")
        
    @log_action(ActionType.RESOURCE_CHANGE)
    @performance_monitor(threshold_ms=20.0)
    def modify_dao_xing(self, amount: int) -> None:
        """
        修改玩家的道行值
        
        Args:
            amount: 变化量（正数增加，负数减少）
        """
        old_dao_xing = self.dao_xing
        self.dao_xing = max(0, self.dao_xing + amount)
        logging.info(f"玩家 {self.name} 道行变化: {old_dao_xing} -> {self.dao_xing} (变化: {amount})")
        
    @log_action(ActionType.RESOURCE_CHANGE)
    @performance_monitor(threshold_ms=20.0)
    def modify_cheng_yi(self, amount: int) -> None:
        """
        修改玩家的诚意值
        
        Args:
            amount: 变化量（正数增加，负数减少）
        """
        old_cheng_yi = self.cheng_yi
        self.cheng_yi = max(0, self.cheng_yi + amount)
        logging.info(f"玩家 {self.name} 诚意变化: {old_cheng_yi} -> {self.cheng_yi} (变化: {amount})")
        
    @performance_monitor(threshold_ms=30.0)
    def get_resource_summary(self) -> Dict[str, int]:
        """
        获取玩家资源摘要
        
        Returns:
            资源字典
        """
        return {
            "qi": self.qi,
            "dao_xing": self.dao_xing,
            "cheng_yi": self.cheng_yi,
            "hand_size": len(self.hand),
            "influence_markers": self.influence_markers
        }

class GameBoard:
    """Represents the state of the game board."""
    def __init__(self, num_players: int):
        if num_players == 2: limit = 5
        elif num_players == 3: limit = 6
        else: limit = 7
        self.base_limit = limit
        self.gua_zones = {
            "乾": {"markers": {}, "controller": None}, "坤": {"markers": {}, "controller": None},
            "震": {"markers": {}, "controller": None}, "巽": {"markers": {}, "controller": None},
            "坎": {"markers": {}, "controller": None}, "离": {"markers": {}, "controller": None},
            "艮": {"markers": {}, "controller": None}, "兑": {"markers": {}, "controller": None},
        }
        self.player_positions = {}

class GameState:
    """Represents the entire state of the game."""
    def __init__(self, players: list[Player]):
        self.board = GameBoard(num_players=len(players))
        self.players = players
        self.current_player_index = 0
        self.turn = 1
        self.current_tian_shi = None # The active Tian Shi card for the round
        for player in self.players:
            self.board.player_positions[player.name] = player.position

    @performance_monitor(threshold_ms=10.0)
    def get_current_player(self) -> Player:
        """获取当前玩家"""
        return self.players[self.current_player_index]
        
    @log_action(ActionType.TURN_CHANGE)
    @performance_monitor(threshold_ms=30.0)
    def advance_turn(self) -> None:
        """
        推进到下一个回合
        """
        old_player = self.get_current_player().name
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        
        # 如果回到第一个玩家，增加回合数
        if self.current_player_index == 0:
            self.turn += 1
            
        new_player = self.get_current_player().name
        logging.info(f"回合推进: {old_player} -> {new_player} (第 {self.turn} 回合)")
        
    @performance_monitor(threshold_ms=50.0)
    def validate_state(self) -> List[str]:
        """
        验证游戏状态的有效性
        
        Returns:
            错误信息列表
        """
        errors = []
        
        # 验证玩家数量
        if len(self.players) < 2:
            errors.append("玩家数量不足")
            
        # 验证当前玩家索引
        if not (0 <= self.current_player_index < len(self.players)):
            errors.append("当前玩家索引无效")
            
        # 验证玩家资源
        for player in self.players:
            if player.qi < 0:
                errors.append(f"玩家 {player.name} 气值为负数")
            if player.dao_xing < 0:
                errors.append(f"玩家 {player.name} 道行为负数")
            if player.cheng_yi < 0:
                errors.append(f"玩家 {player.name} 诚意为负数")
                
        return errors

    def __str__(self):
        """Creates a detailed, user-friendly string representation of the game state."""
        player = self.get_current_player()
        output = f"--- Turn {self.turn}: {player.name}'s Turn ({player.avatar.name.value}) ---\n"

        # Player Status
        output += "--- Player Status ---\n"
        for p in self.players:
            output += (
                f"  {p.name:<10} | Pos: {p.position.value:<2} | "
                f"气: {p.qi:<3} | 道行: {p.dao_xing:<3} | 诚意: {p.cheng_yi:<3} | "
                f"Hand: {len(p.hand)}\n"
            )

        # Board State
        output += "--- Board State ---\n"
        gua_zones = self.board.gua_zones
        for zone_name, data in gua_zones.items():
            line = f"  【{zone_name}】: "
            if data['controller']:
                line += f"Controlled by {data['controller'].name}"
            else:
                markers_str = ", ".join(f"{name}: {count}" for name, count in data['markers'].items())
                line += f"Influence -> {markers_str if markers_str else 'Empty'}"
            output += line + "\n"

        return output
