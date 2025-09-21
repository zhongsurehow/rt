#!/usr/bin/env python3
"""
自动化游戏测试脚本
模拟玩家操作，测试游戏的各项功能
"""

import sys
import time
import subprocess
import threading
from io import StringIO
import json

class GameTester:
    def __init__(self):
        self.test_results = []
        self.current_test = ""
        
    def log_test(self, test_name, result, details=""):
        """记录测试结果"""
        self.test_results.append({
            "test": test_name,
            "result": result,
            "details": details,
            "timestamp": time.time()
        })
        print(f"{'✅' if result else '❌'} {test_name}: {details}")
    
    def test_game_startup(self):
        """测试游戏启动"""
        self.current_test = "游戏启动测试"
        try:
            # 导入游戏模块测试
            from main import main
            from game_state import GameState
            from core_engine import CoreGameEngine
            
            self.log_test("模块导入", True, "所有核心模块导入成功")
            return True
        except Exception as e:
            self.log_test("模块导入", False, f"导入失败: {str(e)}")
            return False
    
    def test_game_initialization(self):
        """测试游戏初始化"""
        self.current_test = "游戏初始化测试"
        try:
            from game_state import GameState, Player, Avatar, AvatarName
            from core_engine import CoreGameEngine
            
            # 创建测试玩家
            avatar1 = Avatar(AvatarName.EMPEROR, "帝王", "统治能力")
            avatar2 = Avatar(AvatarName.HERMIT, "隐士", "智慧能力")
            player1 = Player("测试玩家1", avatar1)
            player2 = Player("AI玩家", avatar2)
            
            # 测试2人游戏初始化
            game_state = GameState(players=[player1, player2])
            
            # 给玩家发一些初始手牌进行测试
            from card_base import GuaCard, YaoCiTask
            # 创建简单的测试任务
            test_tasks = [
                YaoCiTask("初", "初九", "潜龙勿用", 1, 0),
                YaoCiTask("二", "九二", "见龙在田", 1, 0),
                YaoCiTask("三", "九三", "君子终日乾乾", 1, 1),
                YaoCiTask("四", "九四", "或跃在渊", 2, 0),
                YaoCiTask("五", "九五", "飞龙在天", 2, 1),
                YaoCiTask("上", "上九", "亢龙有悔", 1, 2)
            ]
            test_card1 = GuaCard("乾", ("乾", "乾"), test_tasks)
            test_card2 = GuaCard("坤", ("坤", "坤"), test_tasks)
            player1.hand.append(test_card1)
            player1.hand.append(test_card2)
            player2.hand.append(test_card1)
            
            self.log_test("游戏状态创建", True, "2人游戏状态创建成功")
            
            # 检查初始状态
            if len(game_state.players) == 2:
                self.log_test("玩家创建", True, f"成功创建{len(game_state.players)}个玩家")
            else:
                self.log_test("玩家创建", False, f"玩家数量错误: {len(game_state.players)}")
                
            # 检查初始资源
            player = game_state.players[0]
            if hasattr(player, 'qi') and hasattr(player, 'dao_xing'):
                self.log_test("玩家资源初始化", True, f"气: {player.qi}, 道行: {player.dao_xing}")
            else:
                self.log_test("玩家资源初始化", False, "玩家资源属性缺失")
                
            return True
        except Exception as e:
            self.log_test("游戏初始化", False, f"初始化失败: {str(e)}")
            return False
    
    def test_card_system(self):
        """测试卡牌系统"""
        self.current_test = "卡牌系统测试"
        try:
            from game_state import GameState, Player, Avatar, AvatarName
            from card_base import GuaCard, YaoCiTask
            
            # 创建测试玩家
            avatar1 = Avatar(AvatarName.EMPEROR, "帝王", "统治能力")
            avatar2 = Avatar(AvatarName.HERMIT, "隐士", "智慧能力")
            player1 = Player("测试玩家1", avatar1)
            player2 = Player("AI玩家", avatar2)
            
            game_state = GameState(players=[player1, player2])
            
            # 创建测试卡牌
            test_tasks = [
                YaoCiTask("初", "初九", "潜龙勿用", 1, 0),
                YaoCiTask("二", "九二", "见龙在田", 1, 0),
                YaoCiTask("三", "九三", "君子终日乾乾", 1, 1),
                YaoCiTask("四", "九四", "或跃在渊", 2, 0),
                YaoCiTask("五", "九五", "飞龙在天", 2, 1),
                YaoCiTask("上", "上九", "亢龙有悔", 1, 2)
            ]
            test_card = GuaCard("乾", ("乾", "乾"), test_tasks)
            
            # 给玩家添加测试卡牌
            player1.hand.append(test_card)
            player2.hand.append(test_card)
            
            player = game_state.players[0]
            
            # 测试手牌
            if hasattr(player, 'hand') and len(player.hand) > 0:
                self.log_test("初始手牌", True, f"玩家有{len(player.hand)}张手牌")
                
                # 测试第一张卡牌
                first_card = player.hand[0]
                if hasattr(first_card, 'name') and hasattr(first_card, 'associated_guas') and hasattr(first_card, 'tasks'):
                    self.log_test("卡牌属性", True, f"卡牌: {first_card.name}, 关联卦: {first_card.associated_guas}, 任务数: {len(first_card.tasks)}")
                else:
                    self.log_test("卡牌属性", False, "卡牌缺少必要属性")
            else:
                self.log_test("初始手牌", False, "玩家没有手牌")
            
            return True
        except Exception as e:
            self.log_test("卡牌系统", False, f"测试失败: {str(e)}")
            return False
    
    def test_action_system(self):
        """测试行动系统"""
        self.current_test = "行动系统测试"
        try:
            from game_state import GameState, Player, Avatar, AvatarName
            from actions import play_card, move, meditate, study
            
            # 创建测试玩家
            avatar1 = Avatar(AvatarName.EMPEROR, "帝王", "统治能力")
            avatar2 = Avatar(AvatarName.HERMIT, "隐士", "智慧能力")
            player1 = Player("测试玩家1", avatar1)
            player2 = Player("AI玩家", avatar2)
            
            game_state = GameState(players=[player1, player2])
            
            player = game_state.players[0]
            
            # 测试行动函数是否可调用
            self.log_test("行动函数导入", True, "成功导入行动函数")
            
            # 测试冥想行动
            try:
                from game_state import Modifiers
                mods = Modifiers()
                result = meditate(game_state, mods)
                if result is not None:
                    self.log_test("冥想行动", True, "冥想行动执行成功")
                else:
                    self.log_test("冥想行动", False, "冥想行动返回None")
            except Exception as e:
                self.log_test("冥想行动", False, f"冥想行动失败: {str(e)}")
            
            return True
        except Exception as e:
            self.log_test("行动系统", False, f"测试失败: {str(e)}")
            return False
    
    def test_ai_system(self):
        """测试AI系统"""
        self.current_test = "AI系统测试"
        try:
            from game_state import GameState, Player, Avatar, AvatarName
            from bot_player import get_bot_choice
            
            # 创建测试玩家
            avatar1 = Avatar(AvatarName.EMPEROR, "帝王", "统治能力")
            avatar2 = Avatar(AvatarName.HERMIT, "隐士", "智慧能力")
            player1 = Player("测试玩家1", avatar1)
            player2 = Player("AI玩家", avatar2)
            
            game_state = GameState(players=[player1, player2])
            
            self.log_test("AI函数导入", True, "成功导入AI决策函数")
            
            # 测试AI决策函数
            test_actions = {
                1: {"action": "meditate", "description": "冥想"},
                2: {"action": "study", "description": "学习"},
                3: {"action": "pass", "description": "跳过"}
            }
            
            choice = get_bot_choice(test_actions)
            if choice in test_actions:
                self.log_test("AI决策", True, f"AI选择了行动: {test_actions[choice]['action']}")
            else:
                self.log_test("AI决策", False, f"AI选择无效: {choice}")
            
            # 测试只有pass选项的情况
            pass_only_actions = {1: {"action": "pass", "description": "跳过"}}
            pass_choice = get_bot_choice(pass_only_actions)
            self.log_test("AI被迫跳过", pass_choice == 1, f"AI正确选择跳过: {pass_choice}")
            
            return True
        except Exception as e:
            self.log_test("AI系统", False, f"测试失败: {str(e)}")
            return False
    
    def test_victory_conditions(self):
        """测试胜利条件"""
        self.current_test = "胜利条件测试"
        try:
            from game_state import GameState, Player, Avatar, AvatarName
            from enhanced_victory import VictoryTracker, check_enhanced_victory_conditions
            
            # 创建测试玩家
            avatar1 = Avatar(AvatarName.EMPEROR, "帝王", "统治能力")
            avatar2 = Avatar(AvatarName.HERMIT, "隐士", "智慧能力")
            player1 = Player("测试玩家1", avatar1)
            player2 = Player("AI玩家", avatar2)
            
            game_state = GameState(players=[player1, player2])
            
            player = game_state.players[0]
            victory_tracker = VictoryTracker()
            
            self.log_test("胜利系统导入", True, "成功导入胜利条件系统")
            
            # 测试胜利追踪器
            victory_tracker.update_divination(True)
            victory_tracker.add_wisdom("天道酬勤")
            victory_tracker.add_transformation()
            
            self.log_test("胜利追踪器", True, f"占卜次数: {victory_tracker.divination_count}")
            
            # 测试胜利条件检查
            victories = check_enhanced_victory_conditions(player, victory_tracker)
            self.log_test("胜利条件检查", True, f"检查到{len(victories)}个胜利条件")
            
            # 测试基础胜利条件
            if hasattr(player, 'dao_xing'):
                self.log_test("道行胜利检查", True, f"当前道行: {player.dao_xing}")
            else:
                self.log_test("道行胜利检查", False, "玩家缺少道行属性")
            
            return True
        except Exception as e:
            self.log_test("胜利条件", False, f"测试失败: {str(e)}")
            return False
    
    def test_special_features(self):
        """测试特殊功能"""
        self.current_test = "特殊功能测试"
        try:
            # 测试教学系统
            try:
                from tutorial_system import TutorialSystem
                tutorial = TutorialSystem()
                self.log_test("教学系统", True, "教学系统加载成功")
            except:
                self.log_test("教学系统", False, "教学系统加载失败")
            
            # 测试成就系统
            try:
                from achievement_system import AchievementSystem
                achievements = AchievementSystem()
                self.log_test("成就系统", True, "成就系统加载成功")
            except:
                self.log_test("成就系统", False, "成就系统加载失败")
            
            # 测试智慧系统
            try:
                from wisdom_system import WisdomSystem
                wisdom = WisdomSystem()
                self.log_test("智慧系统", True, "智慧系统加载成功")
            except:
                self.log_test("智慧系统", False, "智慧系统加载失败")
            
            return True
        except Exception as e:
            self.log_test("特殊功能", False, f"测试失败: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始自动化游戏测试...")
        print("=" * 50)
        
        tests = [
            self.test_game_startup,
            self.test_game_initialization,
            self.test_card_system,
            self.test_action_system,
            self.test_ai_system,
            self.test_victory_conditions,
            self.test_special_features
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(self.current_test, False, f"测试异常: {str(e)}")
            print("-" * 30)
        
        # 生成测试报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        print("\n📊 测试报告")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['result'])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {passed_tests/total_tests*100:.1f}%")
        
        print("\n详细结果:")
        for result in self.test_results:
            status = "✅" if result['result'] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        # 保存报告到文件
        with open('test_report.json', 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存到 test_report.json")

if __name__ == "__main__":
    tester = GameTester()
    tester.run_all_tests()