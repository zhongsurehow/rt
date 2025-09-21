#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多人游戏管理器 - 支持1-8人的天机变游戏
包含座位安排、回合管理、平衡机制等
"""

from enum import Enum, auto
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import random

from game_state import Player, Avatar, AvatarName, Zone
from game_data import EMPEROR_AVATAR, HERMIT_AVATAR


class GameMode(Enum):
    """游戏模式"""
    SOLO_PRACTICE = "独修模式"      # 1人 - 与AI对战，学习易经
    DUAL_WISDOM = "双贤论道"       # 2人 - 经典对战
    TRINITY_HARMONY = "三才和谐"   # 3人 - 天地人三才
    FOUR_SYMBOLS = "四象争锋"      # 4人 - 四象对应
    FIVE_ELEMENTS = "五行轮转"     # 5人 - 五行相生相克
    SIX_LINES = "六爻演变"        # 6人 - 六爻变化
    SEVEN_STARS = "七星连珠"      # 7人 - 北斗七星
    EIGHT_TRIGRAMS = "八卦齐聚"   # 8人 - 八卦完整


@dataclass
class GameBalance:
    """游戏平衡配置"""
    initial_qi: int
    initial_cheng_yi: int
    initial_hand_size: int
    victory_dao_xing: int
    max_influence_markers: int
    deck_multiplier: float  # 卡牌数量倍数


class MultiplayerManager:
    """多人游戏管理器"""
    
    # 不同人数的游戏平衡配置
    BALANCE_CONFIG = {
        1: GameBalance(8, 4, 5, 8, 20, 1.0),   # 单人模式稍微容易
        2: GameBalance(6, 3, 4, 10, 15, 1.0),  # 经典配置
        3: GameBalance(7, 3, 4, 12, 18, 1.2),  # 三人稍微增加资源
        4: GameBalance(8, 4, 5, 15, 20, 1.5),  # 四人增加卡牌和资源
        5: GameBalance(9, 4, 5, 18, 22, 1.8),  # 五人进一步增加
        6: GameBalance(10, 5, 6, 20, 25, 2.0), # 六人大幅增加
        7: GameBalance(11, 5, 6, 22, 28, 2.2), # 七人继续增加
        8: GameBalance(12, 6, 7, 25, 30, 2.5), # 八人最大配置
    }
    
    # 可用的化身列表（可扩展）
    AVAILABLE_AVATARS = [
        EMPEROR_AVATAR,
        HERMIT_AVATAR,
        # 可以添加更多化身
    ]
    
    def __init__(self, num_players: int):
        if not 1 <= num_players <= 8:
            raise ValueError("游戏支持1-8人，请输入正确的人数")
        
        self.num_players = num_players
        self.game_mode = self._get_game_mode(num_players)
        self.balance = self.BALANCE_CONFIG[num_players]
        self.seating_order: List[int] = []
        self.turn_order: List[int] = []
        
    def _get_game_mode(self, num_players: int) -> GameMode:
        """根据人数获取游戏模式"""
        mode_map = {
            1: GameMode.SOLO_PRACTICE,
            2: GameMode.DUAL_WISDOM,
            3: GameMode.TRINITY_HARMONY,
            4: GameMode.FOUR_SYMBOLS,
            5: GameMode.FIVE_ELEMENTS,
            6: GameMode.SIX_LINES,
            7: GameMode.SEVEN_STARS,
            8: GameMode.EIGHT_TRIGRAMS,
        }
        return mode_map[num_players]
    
    def create_players(self, player_names: Optional[List[str]] = None) -> List[Player]:
        """创建玩家列表"""
        if player_names is None:
            player_names = [f"修行者{i+1}" for i in range(self.num_players)]
        
        if len(player_names) != self.num_players:
            raise ValueError(f"玩家名称数量({len(player_names)})与游戏人数({self.num_players})不匹配")
        
        players = []
        
        # 为每个玩家分配化身
        for i, name in enumerate(player_names):
            # 循环使用可用化身
            avatar = self.AVAILABLE_AVATARS[i % len(self.AVAILABLE_AVATARS)]
            player = Player(name=name, avatar=avatar)
            
            # 根据平衡配置设置初始资源
            player.qi = self.balance.initial_qi
            player.dao_xing = 0
            player.cheng_yi = self.balance.initial_cheng_yi
            player.influence_markers = self.balance.max_influence_markers
            
            players.append(player)
        
        return players
    
    def arrange_seating(self, players: List[Player], random_seating: bool = True) -> List[Player]:
        """安排座位顺序"""
        if random_seating:
            # 随机座位安排
            seated_players = players.copy()
            random.shuffle(seated_players)
        else:
            # 按输入顺序安排
            seated_players = players
        
        # 记录座位顺序
        self.seating_order = list(range(len(seated_players)))
        
        # 根据游戏模式调整初始位置
        self._set_initial_positions(seated_players)
        
        return seated_players
    
    def _set_initial_positions(self, players: List[Player]):
        """根据游戏模式设置玩家初始位置"""
        if self.num_players <= 2:
            # 1-2人：都从地位开始
            for player in players:
                player.position = Zone.DI
        elif self.num_players == 3:
            # 3人：天地人各一位
            positions = [Zone.TIAN, Zone.REN, Zone.DI]
            for i, player in enumerate(players):
                player.position = positions[i]
        elif self.num_players == 4:
            # 4人：两人地位，一人人位，一人天位
            positions = [Zone.DI, Zone.DI, Zone.REN, Zone.TIAN]
            random.shuffle(positions)
            for i, player in enumerate(players):
                player.position = positions[i]
        else:
            # 5-8人：大部分从地位开始，少数分散到其他位置
            positions = [Zone.DI] * (self.num_players - 2)
            positions.extend([Zone.REN, Zone.TIAN])
            random.shuffle(positions)
            for i, player in enumerate(players):
                player.position = positions[i]
    
    def determine_turn_order(self, players: List[Player]) -> List[Player]:
        """确定回合顺序"""
        # 基础回合顺序：按座位顺序
        turn_order = players.copy()
        
        # 根据游戏模式调整回合顺序
        if self.game_mode == GameMode.TRINITY_HARMONY:
            # 三才模式：天→人→地的顺序
            turn_order.sort(key=lambda p: {Zone.TIAN: 0, Zone.REN: 1, Zone.DI: 2}[p.position])
        elif self.game_mode in [GameMode.FIVE_ELEMENTS, GameMode.SIX_LINES, 
                               GameMode.SEVEN_STARS, GameMode.EIGHT_TRIGRAMS]:
            # 多人模式：随机首位玩家，然后顺时针
            first_player_idx = random.randint(0, len(players) - 1)
            turn_order = players[first_player_idx:] + players[:first_player_idx]
        
        self.turn_order = [players.index(p) for p in turn_order]
        return turn_order
    
    def get_victory_condition(self) -> int:
        """获取胜利条件（道行目标）"""
        return self.balance.victory_dao_xing
    
    def get_deck_size_multiplier(self) -> float:
        """获取卡组大小倍数"""
        return self.balance.deck_multiplier
    
    def get_game_info(self) -> Dict:
        """获取游戏信息摘要"""
        return {
            "mode": self.game_mode.value,
            "players": self.num_players,
            "victory_dao_xing": self.balance.victory_dao_xing,
            "initial_resources": {
                "qi": self.balance.initial_qi,
                "cheng_yi": self.balance.initial_cheng_yi,
                "hand_size": self.balance.initial_hand_size,
                "influence_markers": self.balance.max_influence_markers,
            },
            "deck_multiplier": self.balance.deck_multiplier,
        }
    
    def get_strategic_tips(self) -> List[str]:
        """根据游戏模式提供策略提示"""
        tips_map = {
            GameMode.SOLO_PRACTICE: [
                "专注学习易经知识，理解卦象含义",
                "观察AI的策略，学习高级技巧",
                "尝试不同的化身能力组合",
            ],
            GameMode.DUAL_WISDOM: [
                "经典对战模式，平衡攻守",
                "观察对手的资源状况",
                "合理使用化身特殊能力",
            ],
            GameMode.TRINITY_HARMONY: [
                "三才平衡：天地人相互制衡",
                "注意位置优势和劣势",
                "联盟与背叛的艺术",
            ],
            GameMode.FOUR_SYMBOLS: [
                "四象对应：青龙、白虎、朱雀、玄武",
                "资源竞争更加激烈",
                "时机把握至关重要",
            ],
            GameMode.FIVE_ELEMENTS: [
                "五行相生相克：金木水火土",
                "理解相生相克关系",
                "多人联盟策略重要",
            ],
            GameMode.SIX_LINES: [
                "六爻变化：变化莫测",
                "长期规划与短期应变",
                "信息战略的重要性",
            ],
            GameMode.SEVEN_STARS: [
                "北斗七星：指引方向",
                "领导者与跟随者角色",
                "团队协作与个人利益平衡",
            ],
            GameMode.EIGHT_TRIGRAMS: [
                "八卦齐聚：最复杂的游戏模式",
                "多重联盟与复杂博弈",
                "需要深度的策略思考",
            ],
        }
        return tips_map.get(self.game_mode, ["享受游戏，学习易经智慧！"])


def create_multiplayer_game(num_players: int, 
                          player_names: Optional[List[str]] = None,
                          random_seating: bool = True) -> Tuple[List[Player], MultiplayerManager]:
    """创建多人游戏的便捷函数"""
    manager = MultiplayerManager(num_players)
    players = manager.create_players(player_names)
    seated_players = manager.arrange_seating(players, random_seating)
    ordered_players = manager.determine_turn_order(seated_players)
    
    return ordered_players, manager