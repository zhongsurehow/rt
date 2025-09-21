#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天机变游戏高级功能系统
Advanced Features System for TianJiBian Game
"""

import json
import os
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import pickle
import sqlite3

@dataclass
class GameSave:
    """游戏存档数据类"""
    save_id: str
    player_name: str
    game_state: Dict[str, Any]
    timestamp: float
    game_version: str
    save_name: str
    description: str
    playtime: float
    achievements: List[str]
    statistics: Dict[str, Any]

@dataclass
class PlayerStatistics:
    """玩家统计数据类"""
    player_name: str
    games_played: int
    games_won: int
    games_lost: int
    total_playtime: float
    favorite_strategy: str
    best_win_streak: int
    current_win_streak: int
    total_cards_played: int
    total_hexagrams_used: int
    achievements_unlocked: List[str]
    last_played: float
    skill_level: str
    experience_points: int

@dataclass
class Achievement:
    """成就数据类"""
    achievement_id: str
    name: str
    description: str
    icon: str
    unlock_condition: str
    reward_points: int
    rarity: str  # common, rare, epic, legendary
    unlocked: bool
    unlock_date: Optional[float]

class SaveGameManager:
    """游戏存档管理器"""
    
    def __init__(self, save_directory: str = "saves"):
        self.save_directory = save_directory
        self.max_saves = 50
        self._ensure_save_directory()
    
    def _ensure_save_directory(self):
        """确保存档目录存在"""
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def save_game(self, game_state: Dict[str, Any], player_name: str, 
                  save_name: str = None, description: str = "") -> str:
        """保存游戏"""
        timestamp = time.time()
        save_id = hashlib.md5(f"{player_name}_{timestamp}".encode()).hexdigest()[:12]
        
        if not save_name:
            save_name = f"存档_{datetime.fromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S')}"
        
        # 计算游戏时间
        playtime = game_state.get('playtime', 0)
        
        # 获取成就和统计数据
        achievements = game_state.get('achievements', [])
        statistics = game_state.get('statistics', {})
        
        game_save = GameSave(
            save_id=save_id,
            player_name=player_name,
            game_state=game_state,
            timestamp=timestamp,
            game_version="1.0.0",
            save_name=save_name,
            description=description,
            playtime=playtime,
            achievements=achievements,
            statistics=statistics
        )
        
        # 保存到文件
        save_file = os.path.join(self.save_directory, f"{save_id}.json")
        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(game_save), f, indent=2, ensure_ascii=False)
        
        # 清理旧存档
        self._cleanup_old_saves()
        
        print(f"💾 游戏已保存: {save_name} (ID: {save_id})")
        return save_id
    
    def create_save(self, game_state: Dict[str, Any], player_name: str, 
                   save_name: str = None, description: str = "") -> str:
        """创建新存档（save_game的别名方法）"""
        return self.save_game(game_state, player_name, save_name, description)
    
    def load_game(self, save_id: str) -> Optional[GameSave]:
        """加载游戏"""
        save_file = os.path.join(self.save_directory, f"{save_id}.json")
        
        if not os.path.exists(save_file):
            print(f"❌ 存档不存在: {save_id}")
            return None
        
        try:
            with open(save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            game_save = GameSave(**save_data)
            print(f"📂 游戏已加载: {game_save.save_name}")
            return game_save
        
        except Exception as e:
            print(f"❌ 加载存档失败: {e}")
            return None
    
    def list_saves(self, player_name: str = None) -> List[GameSave]:
        """列出存档"""
        saves = []
        
        for filename in os.listdir(self.save_directory):
            if filename.endswith('.json'):
                save_id = filename[:-5]  # 移除.json后缀
                game_save = self.load_game(save_id)
                
                if game_save and (not player_name or game_save.player_name == player_name):
                    saves.append(game_save)
        
        # 按时间排序
        saves.sort(key=lambda x: x.timestamp, reverse=True)
        return saves
    
    def delete_save(self, save_id: str) -> bool:
        """删除存档"""
        save_file = os.path.join(self.save_directory, f"{save_id}.json")
        
        if os.path.exists(save_file):
            os.remove(save_file)
            print(f"🗑️ 存档已删除: {save_id}")
            return True
        
        return False
    
    def _cleanup_old_saves(self):
        """清理旧存档"""
        saves = self.list_saves()
        
        if len(saves) > self.max_saves:
            # 删除最旧的存档
            for save in saves[self.max_saves:]:
                self.delete_save(save.save_id)

class StatisticsManager:
    """统计数据管理器"""
    
    def __init__(self, stats_file: str = "player_statistics.json"):
        self.stats_file = stats_file
        self.player_stats: Dict[str, PlayerStatistics] = {}
        self.load_statistics()
    
    def load_statistics(self):
        """加载统计数据"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    stats_data = json.load(f)
                
                for player_name, data in stats_data.items():
                    self.player_stats[player_name] = PlayerStatistics(**data)
            
            except Exception as e:
                print(f"❌ 加载统计数据失败: {e}")
    
    def save_statistics(self):
        """保存统计数据"""
        try:
            stats_data = {}
            for player_name, stats in self.player_stats.items():
                stats_data[player_name] = asdict(stats)
            
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            print(f"❌ 保存统计数据失败: {e}")
    
    def get_player_stats(self, player_name: str) -> PlayerStatistics:
        """获取玩家统计数据"""
        if player_name not in self.player_stats:
            self.player_stats[player_name] = PlayerStatistics(
                player_name=player_name,
                games_played=0,
                games_won=0,
                games_lost=0,
                total_playtime=0.0,
                favorite_strategy="",
                best_win_streak=0,
                current_win_streak=0,
                total_cards_played=0,
                total_hexagrams_used=0,
                achievements_unlocked=[],
                last_played=time.time(),
                skill_level="新手",
                experience_points=0
            )
        
        return self.player_stats[player_name]
    
    def update_game_result(self, player_name: str, won: bool, playtime: float,
                          cards_played: int = 0, hexagrams_used: int = 0):
        """更新游戏结果"""
        stats = self.get_player_stats(player_name)
        
        stats.games_played += 1
        stats.total_playtime += playtime
        stats.total_cards_played += cards_played
        stats.total_hexagrams_used += hexagrams_used
        stats.last_played = time.time()
        
        if won:
            stats.games_won += 1
            stats.current_win_streak += 1
            stats.best_win_streak = max(stats.best_win_streak, stats.current_win_streak)
            stats.experience_points += 100
        else:
            stats.games_lost += 1
            stats.current_win_streak = 0
            stats.experience_points += 25
        
        # 更新技能等级
        self._update_skill_level(stats)
        
        self.save_statistics()
    
    def _update_skill_level(self, stats: PlayerStatistics):
        """更新技能等级"""
        if stats.experience_points >= 10000:
            stats.skill_level = "宗师"
        elif stats.experience_points >= 5000:
            stats.skill_level = "专家"
        elif stats.experience_points >= 2000:
            stats.skill_level = "高手"
        elif stats.experience_points >= 500:
            stats.skill_level = "熟练"
        elif stats.experience_points >= 100:
            stats.skill_level = "入门"
        else:
            stats.skill_level = "新手"
    
    def get_leaderboard(self, category: str = "win_rate") -> List[Tuple[str, Any]]:
        """获取排行榜"""
        if not self.player_stats:
            return []
        
        if category == "win_rate":
            # 胜率排行榜
            leaderboard = []
            for name, stats in self.player_stats.items():
                if stats.games_played > 0:
                    win_rate = stats.games_won / stats.games_played
                    leaderboard.append((name, win_rate))
            
            leaderboard.sort(key=lambda x: x[1], reverse=True)
        
        elif category == "experience":
            # 经验排行榜
            leaderboard = [(name, stats.experience_points) 
                          for name, stats in self.player_stats.items()]
            leaderboard.sort(key=lambda x: x[1], reverse=True)
        
        elif category == "playtime":
            # 游戏时间排行榜
            leaderboard = [(name, stats.total_playtime) 
                          for name, stats in self.player_stats.items()]
            leaderboard.sort(key=lambda x: x[1], reverse=True)
        
        elif category == "win_streak":
            # 连胜排行榜
            leaderboard = [(name, stats.best_win_streak) 
                          for name, stats in self.player_stats.items()]
            leaderboard.sort(key=lambda x: x[1], reverse=True)
        
        else:
            return []
        
        return leaderboard[:10]  # 返回前10名

class AchievementSystem:
    """成就系统"""
    
    def __init__(self, achievements_file: str = "achievements.json"):
        self.achievements_file = achievements_file
        self.achievements: Dict[str, Achievement] = {}
        self.player_achievements: Dict[str, List[str]] = {}
        self._initialize_achievements()
        self.load_player_achievements()
    
    def _initialize_achievements(self):
        """初始化成就"""
        default_achievements = [
            {
                "achievement_id": "first_win",
                "name": "初战告捷",
                "description": "赢得第一场游戏",
                "icon": "🏆",
                "unlock_condition": "win_first_game",
                "reward_points": 100,
                "rarity": "common",
                "unlocked": False,
                "unlock_date": None
            },
            {
                "achievement_id": "win_streak_5",
                "name": "连胜高手",
                "description": "连续赢得5场游戏",
                "icon": "🔥",
                "unlock_condition": "win_streak_5",
                "reward_points": 250,
                "rarity": "rare",
                "unlocked": False,
                "unlock_date": None
            },
            {
                "achievement_id": "master_strategist",
                "name": "策略大师",
                "description": "使用所有36种策略",
                "icon": "🧠",
                "unlock_condition": "use_all_strategies",
                "reward_points": 500,
                "rarity": "epic",
                "unlocked": False,
                "unlock_date": None
            },
            {
                "achievement_id": "hexagram_master",
                "name": "卦象宗师",
                "description": "使用所有64卦",
                "icon": "☯️",
                "unlock_condition": "use_all_hexagrams",
                "reward_points": 1000,
                "rarity": "legendary",
                "unlocked": False,
                "unlock_date": None
            },
            {
                "achievement_id": "speed_demon",
                "name": "闪电战士",
                "description": "在5分钟内完成一场游戏",
                "icon": "⚡",
                "unlock_condition": "fast_game",
                "reward_points": 200,
                "rarity": "rare",
                "unlocked": False,
                "unlock_date": None
            }
        ]
        
        for ach_data in default_achievements:
            achievement = Achievement(**ach_data)
            self.achievements[achievement.achievement_id] = achievement
    
    def load_player_achievements(self):
        """加载玩家成就"""
        if os.path.exists(self.achievements_file):
            try:
                with open(self.achievements_file, 'r', encoding='utf-8') as f:
                    self.player_achievements = json.load(f)
            except Exception as e:
                print(f"❌ 加载成就数据失败: {e}")
    
    def save_player_achievements(self):
        """保存玩家成就"""
        try:
            with open(self.achievements_file, 'w', encoding='utf-8') as f:
                json.dump(self.player_achievements, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存成就数据失败: {e}")
    
    def check_achievements(self, player_name: str, game_data: Dict[str, Any]) -> List[Achievement]:
        """检查并解锁成就"""
        if player_name not in self.player_achievements:
            self.player_achievements[player_name] = []
        
        unlocked_achievements = []
        player_unlocked = self.player_achievements[player_name]
        
        for ach_id, achievement in self.achievements.items():
            if ach_id in player_unlocked:
                continue  # 已解锁
            
            if self._check_unlock_condition(achievement.unlock_condition, game_data):
                # 解锁成就
                player_unlocked.append(ach_id)
                achievement.unlocked = True
                achievement.unlock_date = time.time()
                unlocked_achievements.append(achievement)
                
                print(f"🎉 成就解锁: {achievement.icon} {achievement.name}")
                print(f"   {achievement.description}")
                print(f"   奖励: {achievement.reward_points} 经验点")
        
        if unlocked_achievements:
            self.save_player_achievements()
        
        return unlocked_achievements
    
    def _check_unlock_condition(self, condition: str, game_data: Dict[str, Any]) -> bool:
        """检查解锁条件"""
        if condition == "win_first_game":
            return game_data.get('games_won', 0) >= 1
        
        elif condition == "win_streak_5":
            return game_data.get('current_win_streak', 0) >= 5
        
        elif condition == "use_all_strategies":
            used_strategies = game_data.get('used_strategies', set())
            return len(used_strategies) >= 36
        
        elif condition == "use_all_hexagrams":
            used_hexagrams = game_data.get('used_hexagrams', set())
            return len(used_hexagrams) >= 64
        
        elif condition == "fast_game":
            last_game_time = game_data.get('last_game_duration', float('inf'))
            return last_game_time <= 300  # 5分钟
        
        return False
    
    def get_player_achievements(self, player_name: str) -> List[Achievement]:
        """获取玩家成就"""
        if player_name not in self.player_achievements:
            return []
        
        unlocked_ids = self.player_achievements[player_name]
        return [self.achievements[ach_id] for ach_id in unlocked_ids 
                if ach_id in self.achievements]

class AdvancedFeaturesManager:
    """高级功能管理器"""
    
    def __init__(self):
        self.save_manager = SaveGameManager()
        self.stats_manager = StatisticsManager()
        self.achievement_system = AchievementSystem()
        
    def create_comprehensive_demo(self):
        """创建综合演示"""
        print("\n" + "="*60)
        print("🎮 天机变游戏高级功能演示")
        print("="*60)
        
        # 模拟游戏数据
        player_name = "测试玩家"
        
        # 模拟游戏状态
        game_state = {
            'current_player': player_name,
            'turn': 15,
            'season': '春',
            'players': {
                player_name: {
                    'cards': ['乾', '坤', '震'],
                    'score': 85,
                    'strategies_used': ['兵不厌诈', '声东击西', '借刀杀人']
                }
            },
            'playtime': 420.5,  # 7分钟
            'achievements': ['first_win'],
            'statistics': {
                'cards_played': 12,
                'hexagrams_used': 8,
                'strategies_used': 3
            }
        }
        
        # 1. 保存游戏演示
        print("\n📁 游戏存档功能演示:")
        save_id = self.save_manager.save_game(
            game_state, 
            player_name, 
            "测试存档", 
            "这是一个测试存档"
        )
        
        # 2. 加载游戏演示
        print("\n📂 游戏加载功能演示:")
        loaded_save = self.save_manager.load_game(save_id)
        if loaded_save:
            print(f"   存档名称: {loaded_save.save_name}")
            print(f"   游戏时间: {loaded_save.playtime:.1f}秒")
            print(f"   保存时间: {datetime.fromtimestamp(loaded_save.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 3. 统计数据演示
        print("\n📊 统计数据功能演示:")
        self.stats_manager.update_game_result(
            player_name, 
            won=True, 
            playtime=420.5,
            cards_played=12,
            hexagrams_used=8
        )
        
        stats = self.stats_manager.get_player_stats(player_name)
        print(f"   玩家: {stats.player_name}")
        print(f"   游戏场次: {stats.games_played}")
        print(f"   胜利次数: {stats.games_won}")
        print(f"   胜率: {stats.games_won/max(1, stats.games_played):.1%}")
        print(f"   技能等级: {stats.skill_level}")
        print(f"   经验点数: {stats.experience_points}")
        
        # 4. 成就系统演示
        print("\n🏆 成就系统功能演示:")
        game_data = {
            'games_won': stats.games_won,
            'current_win_streak': stats.current_win_streak,
            'last_game_duration': 420.5
        }
        
        unlocked = self.achievement_system.check_achievements(player_name, game_data)
        
        player_achievements = self.achievement_system.get_player_achievements(player_name)
        print(f"   已解锁成就: {len(player_achievements)}")
        for ach in player_achievements:
            print(f"   {ach.icon} {ach.name} - {ach.description}")
        
        # 5. 排行榜演示
        print("\n🏅 排行榜功能演示:")
        
        # 添加一些模拟数据
        for i, name in enumerate(["高手甲", "高手乙", "高手丙"]):
            self.stats_manager.update_game_result(name, i % 2 == 0, 300 + i * 50)
        
        leaderboards = {
            "胜率排行榜": self.stats_manager.get_leaderboard("win_rate"),
            "经验排行榜": self.stats_manager.get_leaderboard("experience"),
            "游戏时间排行榜": self.stats_manager.get_leaderboard("playtime")
        }
        
        for board_name, board_data in leaderboards.items():
            print(f"\n   {board_name}:")
            for i, (name, value) in enumerate(board_data[:5], 1):
                if "胜率" in board_name:
                    print(f"     {i}. {name}: {value:.1%}")
                elif "时间" in board_name:
                    print(f"     {i}. {name}: {value:.1f}秒")
                else:
                    print(f"     {i}. {name}: {value}")
        
        # 6. 存档列表演示
        print("\n💾 存档管理功能演示:")
        saves = self.save_manager.list_saves()
        print(f"   总存档数: {len(saves)}")
        for save in saves[:3]:  # 显示前3个存档
            print(f"   📁 {save.save_name}")
            print(f"      ID: {save.save_id}")
            print(f"      玩家: {save.player_name}")
            print(f"      时间: {datetime.fromtimestamp(save.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n" + "="*60)
        print("✅ 高级功能演示完成!")
        print("="*60)

if __name__ == "__main__":
    print("🚀 天机变游戏高级功能系统")
    
    # 创建管理器实例
    advanced_features = AdvancedFeaturesManager()
    
    # 运行综合演示
    advanced_features.create_comprehensive_demo()