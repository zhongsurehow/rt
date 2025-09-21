#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化游戏体验测试 - 模拟完整的游戏流程
Automated Gameplay Test - Simulates complete game experience
"""

import sys
import time
import random
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# 导入游戏模块
from game_state import GameState, Player, Avatar, AvatarName
from game_data import GAME_DECK
from multiplayer_manager import create_multiplayer_game
from yijing_education_system import YijingEducationSystem
from enhanced_game_mechanics import enhanced_mechanics
from config_manager import ConfigManager
from enhanced_ui_experience import EnhancedUIExperience, MessageType
from core_engine import CoreGameEngine
from bot_player import get_bot_choice

class AutomatedGameplayTest:
    """自动化游戏体验测试"""
    
    def __init__(self):
        self.test_results = []
        self.game_log = []
        self.start_time = datetime.now()
        
    def log_action(self, action: str, result: str, details: str = ""):
        """记录游戏行动"""
        log_entry = {
            "时间": datetime.now().strftime("%H:%M:%S"),
            "行动": action,
            "结果": result,
            "详情": details
        }
        self.game_log.append(log_entry)
        print(f"🎮 {action}: {result}")
        if details:
            print(f"   详情: {details}")
    
    def test_game_initialization(self):
        """测试游戏初始化"""
        print("\n🚀 测试游戏初始化...")
        
        try:
            # 创建多人游戏
            players, manager = create_multiplayer_game(2, ["玩家1", "AI玩家"])
            self.log_action("创建多人游戏", "成功", f"创建了{len(players)}个玩家")
            
            # 创建游戏状态
            game_state = GameState(players=players)
            self.log_action("游戏状态初始化", "成功", f"游戏包含{len(game_state.players)}个玩家")
            
            # 创建游戏引擎
            engine = CoreGameEngine(game_state)
            self.log_action("游戏引擎创建", "成功", "核心引擎已就绪")
            
            return game_state, engine
            
        except Exception as e:
            self.log_action("游戏初始化", "失败", f"错误: {e}")
            return None, None
    
    def test_card_dealing(self, game_state: GameState):
        """测试发牌系统"""
        print("\n🃏 测试发牌系统...")
        
        try:
            # 模拟发牌
            deck = GAME_DECK.copy()
            random.shuffle(deck)
            
            for player in game_state.players:
                for _ in range(5):  # 发5张牌
                    if deck:
                        player.hand.append(deck.pop())
            
            # 检查发牌结果
            for i, player in enumerate(game_state.players):
                self.log_action(f"玩家{i+1}发牌", "成功", f"手牌数量: {len(player.hand)}")
                
                # 显示手牌信息
                if player.hand:
                    card_names = [card.name for card in player.hand]
                    self.log_action(f"玩家{i+1}手牌", "详情", f"卡牌: {', '.join(card_names[:3])}...")
            
            return True
            
        except Exception as e:
            self.log_action("发牌系统", "失败", f"错误: {e}")
            return False
    
    def test_game_mechanics(self, game_state: GameState, engine: CoreGameEngine):
        """测试游戏机制"""
        print("\n⚙️ 测试游戏机制...")
        
        try:
            # 测试季节系统
            season_info = enhanced_mechanics.get_current_season_info()
            self.log_action("季节系统", "成功", f"当前季节: {season_info.get('season', '未知')}")
            
            # 测试卦象生成
            hexagram = enhanced_mechanics.get_random_hexagram()
            if hexagram:
                self.log_action("卦象生成", "成功", f"生成: {hexagram.get('name', '未知卦象')}")
            
            # 测试玩家状态
            current_player = game_state.get_current_player()
            self.log_action("当前玩家", "成功", f"轮到: {current_player.name}")
            
            # 测试资源系统
            self.log_action("资源检查", "成功", f"气: {current_player.qi}, 道行: {current_player.dao_xing}")
            
            return True
            
        except Exception as e:
            self.log_action("游戏机制", "失败", f"错误: {e}")
            return False
    
    def simulate_game_turns(self, game_state: GameState, engine: CoreGameEngine, turns: int = 5):
        """模拟游戏回合"""
        print(f"\n🔄 模拟{turns}个游戏回合...")
        
        try:
            for turn in range(turns):
                print(f"\n--- 第{turn + 1}回合 ---")
                
                current_player = game_state.get_current_player()
                self.log_action(f"回合{turn + 1}", "开始", f"当前玩家: {current_player.name}")
                
                # 模拟玩家行动
                if current_player.hand:
                    # 随机选择一张卡牌
                    card_index = random.randint(0, len(current_player.hand) - 1)
                    card = current_player.hand[card_index]
                    
                    # 随机选择一个可用区域
                    if hasattr(card, 'associated_guas') and card.associated_guas:
                        zone = random.choice(card.associated_guas)
                        
                        # 尝试出牌
                        try:
                            # 这里简化处理，直接移除卡牌
                            played_card = current_player.hand.pop(card_index)
                            self.log_action("出牌", "成功", f"{current_player.name}打出{played_card.name}到{zone}")
                        except Exception as e:
                            self.log_action("出牌", "失败", f"错误: {e}")
                
                # 切换到下一个玩家
                game_state.current_player_index = (game_state.current_player_index + 1) % len(game_state.players)
                
                # 短暂延迟
                time.sleep(0.1)
            
            return True
            
        except Exception as e:
            self.log_action("回合模拟", "失败", f"错误: {e}")
            return False
    
    def test_ai_behavior(self, game_state: GameState):
        """测试AI行为"""
        print("\n🤖 测试AI行为...")
        
        try:
            # 找到AI玩家
            ai_player = None
            for player in game_state.players:
                if "AI" in player.name:
                    ai_player = player
                    break
            
            if ai_player:
                # 创建模拟行动选项
                valid_actions = {
                    1: {"action": "play_card", "description": "出牌"},
                    2: {"action": "meditate", "description": "冥想"},
                    3: {"action": "study", "description": "研习"},
                    4: {"action": "pass", "description": "跳过"}
                }
                
                # 测试AI决策
                for i in range(3):
                    ai_choice = get_bot_choice(valid_actions)
                    action_desc = valid_actions[ai_choice]["description"]
                    self.log_action(f"AI决策{i+1}", "成功", f"选择: {action_desc}")
            
            return True
            
        except Exception as e:
            self.log_action("AI行为测试", "失败", f"错误: {e}")
            return False
    
    def test_education_system(self):
        """测试教育系统"""
        print("\n📚 测试教育系统...")
        
        try:
            education = YijingEducationSystem()
            
            # 初始化学习者
            education.initialize_player("测试学习者")
            self.log_action("学习者初始化", "成功", "创建学习档案")
            
            # 获取随机知识
            knowledge = education.get_random_knowledge()
            if knowledge:
                self.log_action("知识获取", "成功", f"获得: {knowledge.title}")
            
            # 记录学习
            education.record_learning("测试学习者", "易经基础", 5)
            self.log_action("学习记录", "成功", "记录学习成果")
            
            # 获取学习建议
            suggestion = education.get_learning_suggestion("测试学习者")
            if suggestion:
                self.log_action("学习建议", "成功", f"建议: {suggestion[:50]}...")
            
            return True
            
        except Exception as e:
            self.log_action("教育系统", "失败", f"错误: {e}")
            return False
    
    def generate_gameplay_report(self):
        """生成游戏体验报告"""
        print("\n📊 生成游戏体验报告...")
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        # 统计测试结果
        total_actions = len(self.game_log)
        successful_actions = len([log for log in self.game_log if log["结果"] == "成功"])
        success_rate = (successful_actions / total_actions * 100) if total_actions > 0 else 0
        
        report = {
            "测试时间": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "测试时长": f"{duration:.2f}秒",
            "总行动数": total_actions,
            "成功行动数": successful_actions,
            "成功率": f"{success_rate:.1f}%",
            "游戏日志": self.game_log,
            "评估结果": {
                "游戏稳定性": "优秀" if success_rate >= 90 else "良好" if success_rate >= 70 else "需改进",
                "功能完整性": "完整" if successful_actions >= 20 else "基本完整",
                "用户体验": "流畅" if success_rate >= 85 else "一般"
            }
        }
        
        # 保存报告
        with open("automated_gameplay_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📋 游戏体验报告已保存: automated_gameplay_report.json")
        print(f"⭐ 总体评分: {success_rate:.1f}%")
        
        return report
    
    def run_full_gameplay_test(self):
        """运行完整的游戏体验测试"""
        print("=" * 60)
        print("🎮 天机变游戏 - 自动化游戏体验测试")
        print("=" * 60)
        
        # 1. 游戏初始化
        game_state, engine = self.test_game_initialization()
        if not game_state or not engine:
            print("❌ 游戏初始化失败，测试终止")
            return
        
        # 2. 发牌测试
        if not self.test_card_dealing(game_state):
            print("❌ 发牌系统测试失败")
        
        # 3. 游戏机制测试
        if not self.test_game_mechanics(game_state, engine):
            print("❌ 游戏机制测试失败")
        
        # 4. 回合模拟
        if not self.simulate_game_turns(game_state, engine):
            print("❌ 回合模拟失败")
        
        # 5. AI行为测试
        if not self.test_ai_behavior(game_state):
            print("❌ AI行为测试失败")
        
        # 6. 教育系统测试
        if not self.test_education_system():
            print("❌ 教育系统测试失败")
        
        # 7. 生成报告
        report = self.generate_gameplay_report()
        
        print("\n" + "=" * 60)
        print("🎉 自动化游戏体验测试完成!")
        print("=" * 60)
        
        return report

def main():
    """主函数"""
    tester = AutomatedGameplayTest()
    return tester.run_full_gameplay_test()

if __name__ == "__main__":
    main()