#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI智能程度和游戏平衡性测试
AI Intelligence and Game Balance Test
"""

import sys
import time
import random
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

# 导入游戏模块
from game_state import GameState, Player, Avatar, AvatarName
from game_data import GAME_DECK
from multiplayer_manager import create_multiplayer_game
from core_engine import CoreGameEngine, ActionType
from bot_player import get_bot_choice
from enhanced_game_mechanics import enhanced_mechanics

class AIBalanceTest:
    """AI智能程度和游戏平衡性测试"""
    
    def __init__(self):
        self.test_results = []
        self.game_statistics = defaultdict(int)
        self.ai_performance = defaultdict(list)
        self.start_time = datetime.now()
        
    def log_test(self, test_name: str, result: str, details: str = ""):
        """记录测试结果"""
        log_entry = {
            "时间": datetime.now().strftime("%H:%M:%S"),
            "测试": test_name,
            "结果": result,
            "详情": details
        }
        self.test_results.append(log_entry)
        print(f"🧪 {test_name}: {result}")
        if details:
            print(f"   详情: {details}")
    
    def test_ai_decision_quality(self, iterations: int = 10):
        """测试AI决策质量"""
        print(f"\n🤖 测试AI决策质量 ({iterations}次迭代)...")
        
        decision_scores = []
        
        for i in range(iterations):
            try:
                # 创建不同的游戏情况
                valid_actions = self._create_test_scenarios()[i % 5]
                
                # 记录AI选择
                ai_choice = get_bot_choice(valid_actions)
                chosen_action = valid_actions[ai_choice]
                
                # 评估决策质量
                score = self._evaluate_decision_quality(chosen_action, valid_actions)
                decision_scores.append(score)
                
                self.ai_performance["决策质量"].append(score)
                
            except Exception as e:
                self.log_test(f"AI决策测试{i+1}", "失败", f"错误: {e}")
                continue
        
        if decision_scores:
            avg_score = sum(decision_scores) / len(decision_scores)
            self.log_test("AI决策质量", "完成", f"平均分: {avg_score:.2f}/10")
            return avg_score
        else:
            self.log_test("AI决策质量", "失败", "无有效决策数据")
            return 0
    
    def _create_test_scenarios(self) -> List[Dict]:
        """创建测试场景"""
        scenarios = [
            # 场景1: 优势局面
            {
                1: {"action": "play_card", "description": "出强力卡牌", "priority": 9},
                2: {"action": "meditate", "description": "冥想", "priority": 3},
                3: {"action": "pass", "description": "跳过", "priority": 1}
            },
            # 场景2: 劣势局面
            {
                1: {"action": "study", "description": "研习", "priority": 7},
                2: {"action": "divine", "description": "占卜", "priority": 6},
                3: {"action": "pass", "description": "跳过", "priority": 2}
            },
            # 场景3: 平衡局面
            {
                1: {"action": "play_card", "description": "出牌", "priority": 5},
                2: {"action": "move", "description": "移动", "priority": 5},
                3: {"action": "meditate", "description": "冥想", "priority": 4}
            },
            # 场景4: 资源紧张
            {
                1: {"action": "meditate", "description": "冥想恢复", "priority": 8},
                2: {"action": "study", "description": "研习", "priority": 4},
                3: {"action": "pass", "description": "跳过", "priority": 3}
            },
            # 场景5: 终局阶段
            {
                1: {"action": "play_card", "description": "决胜出牌", "priority": 10},
                2: {"action": "divine", "description": "占卜", "priority": 2},
                3: {"action": "pass", "description": "跳过", "priority": 1}
            }
        ]
        return scenarios
    
    def _evaluate_decision_quality(self, chosen_action: Dict, all_actions: Dict) -> float:
        """评估决策质量"""
        # 基于优先级评估决策质量
        chosen_priority = chosen_action.get("priority", 5)
        max_priority = max(action.get("priority", 5) for action in all_actions.values())
        
        # 计算相对质量分数 (1-10分)
        if max_priority == 0:
            return 5.0
        
        quality_ratio = chosen_priority / max_priority
        return min(10.0, quality_ratio * 10)
    
    def test_game_balance(self, games: int = 20):
        """测试游戏平衡性"""
        print(f"\n⚖️ 测试游戏平衡性 ({games}场游戏)...")
        
        win_stats = defaultdict(int)
        game_lengths = []
        
        for game_num in range(games):
            try:
                # 创建游戏
                players, manager = create_multiplayer_game(2, ["人类玩家", "AI玩家"])
                game_state = GameState(players=players)
                engine = CoreGameEngine(game_state)
                
                # 模拟游戏
                winner, turns = self._simulate_balanced_game(game_state, engine)
                
                if winner:
                    win_stats[winner.name] += 1
                    game_lengths.append(turns)
                    
                    self.log_test(f"游戏{game_num+1}", "完成", f"胜者: {winner.name}, 回合数: {turns}")
                
            except Exception as e:
                self.log_test(f"游戏{game_num+1}", "失败", f"错误: {e}")
                continue
        
        # 分析平衡性
        self._analyze_balance(win_stats, game_lengths)
        
        return win_stats, game_lengths
    
    def _simulate_balanced_game(self, game_state: GameState, engine: CoreGameEngine, max_turns: int = 50):
        """模拟平衡游戏"""
        turns = 0
        
        # 发牌
        deck = GAME_DECK.copy()
        random.shuffle(deck)
        
        for player in game_state.players:
            for _ in range(5):
                if deck:
                    player.hand.append(deck.pop())
        
        # 游戏循环
        while turns < max_turns:
            current_player = game_state.get_current_player()
            
            # 模拟玩家行动
            if "AI" in current_player.name:
                # AI玩家决策
                valid_actions = self._get_valid_actions(current_player, game_state)
                if valid_actions:
                    choice = get_bot_choice(valid_actions)
                    self._execute_action(current_player, valid_actions[choice], game_state)
            else:
                # 人类玩家模拟（随机决策）
                self._simulate_human_action(current_player, game_state)
            
            # 检查胜利条件
            winner = self._check_simple_victory(game_state)
            if winner:
                return winner, turns
            
            # 下一回合
            game_state.current_player_index = (game_state.current_player_index + 1) % len(game_state.players)
            turns += 1
        
        # 超时判定
        return self._determine_winner_by_score(game_state), turns
    
    def _get_valid_actions(self, player: Player, game_state: GameState) -> Dict:
        """获取有效行动"""
        actions = {}
        action_id = 1
        
        # 出牌
        if player.hand and player.qi >= 1:
            actions[action_id] = {"action": "play_card", "description": "出牌"}
            action_id += 1
        
        # 冥想
        if player.qi < 10:
            actions[action_id] = {"action": "meditate", "description": "冥想"}
            action_id += 1
        
        # 研习
        if player.qi >= 2:
            actions[action_id] = {"action": "study", "description": "研习"}
            action_id += 1
        
        # 跳过
        actions[action_id] = {"action": "pass", "description": "跳过"}
        
        return actions
    
    def _execute_action(self, player: Player, action: Dict, game_state: GameState):
        """执行行动"""
        action_type = action["action"]
        
        if action_type == "play_card" and player.hand:
            # 出牌
            card = player.hand.pop(0)
            player.qi = max(0, player.qi - 1)
            player.dao_xing += 1
            
        elif action_type == "meditate":
            # 冥想
            player.qi = min(10, player.qi + 2)
            
        elif action_type == "study":
            # 研习
            player.qi = max(0, player.qi - 2)
            player.dao_xing += 2
    
    def _simulate_human_action(self, player: Player, game_state: GameState):
        """模拟人类玩家行动"""
        valid_actions = self._get_valid_actions(player, game_state)
        if valid_actions:
            choice = random.choice(list(valid_actions.keys()))
            self._execute_action(player, valid_actions[choice], game_state)
    
    def _check_simple_victory(self, game_state: GameState) -> Optional[Player]:
        """简单胜利条件检查"""
        for player in game_state.players:
            if player.dao_xing >= 20:  # 道行达到20获胜
                return player
        return None
    
    def _determine_winner_by_score(self, game_state: GameState) -> Optional[Player]:
        """根据分数确定胜者"""
        if not game_state.players:
            return None
        
        return max(game_state.players, key=lambda p: p.dao_xing + p.qi)
    
    def _analyze_balance(self, win_stats: Dict, game_lengths: List[int]):
        """分析游戏平衡性"""
        total_games = sum(win_stats.values())
        
        if total_games == 0:
            self.log_test("平衡性分析", "失败", "无有效游戏数据")
            return
        
        # 胜率分析
        for player, wins in win_stats.items():
            win_rate = (wins / total_games) * 100
            self.log_test(f"{player}胜率", "统计", f"{win_rate:.1f}% ({wins}/{total_games})")
        
        # 游戏长度分析
        if game_lengths:
            avg_length = sum(game_lengths) / len(game_lengths)
            min_length = min(game_lengths)
            max_length = max(game_lengths)
            
            self.log_test("游戏长度", "统计", f"平均{avg_length:.1f}回合 (范围: {min_length}-{max_length})")
        
        # 平衡性评估
        ai_wins = win_stats.get("AI玩家", 0)
        human_wins = win_stats.get("人类玩家", 0)
        
        if total_games > 0:
            ai_win_rate = (ai_wins / total_games) * 100
            balance_score = 100 - abs(50 - ai_win_rate) * 2  # 越接近50%越平衡
            
            if balance_score >= 80:
                balance_level = "优秀"
            elif balance_score >= 60:
                balance_level = "良好"
            else:
                balance_level = "需改进"
            
            self.log_test("平衡性评估", balance_level, f"平衡分数: {balance_score:.1f}/100")
    
    def test_ai_adaptability(self):
        """测试AI适应性"""
        print("\n🔄 测试AI适应性...")
        
        adaptability_scores = []
        
        # 测试不同难度场景
        scenarios = [
            ("简单场景", {"complexity": 1, "pressure": 1}),
            ("中等场景", {"complexity": 5, "pressure": 3}),
            ("困难场景", {"complexity": 8, "pressure": 7}),
            ("极限场景", {"complexity": 10, "pressure": 10})
        ]
        
        for scenario_name, params in scenarios:
            try:
                score = self._test_scenario_adaptability(scenario_name, params)
                adaptability_scores.append(score)
                self.log_test(f"适应性-{scenario_name}", "完成", f"得分: {score:.1f}/10")
                
            except Exception as e:
                self.log_test(f"适应性-{scenario_name}", "失败", f"错误: {e}")
        
        if adaptability_scores:
            avg_adaptability = sum(adaptability_scores) / len(adaptability_scores)
            self.log_test("AI适应性", "评估", f"综合得分: {avg_adaptability:.1f}/10")
            return avg_adaptability
        
        return 0
    
    def _test_scenario_adaptability(self, scenario_name: str, params: Dict) -> float:
        """测试场景适应性"""
        complexity = params["complexity"]
        pressure = params["pressure"]
        
        # 创建复杂度相应的行动选项
        num_actions = min(2 + complexity, 8)
        valid_actions = {}
        
        for i in range(num_actions):
            priority = random.randint(1, 10)
            # 在高压力情况下，降低某些选项的优先级
            if pressure > 5 and random.random() < 0.3:
                priority = max(1, priority - pressure)
            
            valid_actions[i + 1] = {
                "action": f"action_{i+1}",
                "description": f"行动{i+1}",
                "priority": priority
            }
        
        # 测试AI在此场景下的表现
        correct_decisions = 0
        total_decisions = 10
        
        for _ in range(total_decisions):
            ai_choice = get_bot_choice(valid_actions)
            chosen_action = valid_actions[ai_choice]
            
            # 评估决策是否合理
            if self._is_reasonable_decision(chosen_action, valid_actions, complexity, pressure):
                correct_decisions += 1
        
        return (correct_decisions / total_decisions) * 10
    
    def _is_reasonable_decision(self, chosen_action: Dict, all_actions: Dict, complexity: int, pressure: int) -> bool:
        """判断决策是否合理"""
        chosen_priority = chosen_action.get("priority", 5)
        max_priority = max(action.get("priority", 5) for action in all_actions.values())
        
        # 在高复杂度和高压力下，要求更高的决策质量
        threshold = 0.7 if complexity > 7 or pressure > 7 else 0.5
        
        return (chosen_priority / max_priority) >= threshold if max_priority > 0 else True
    
    def generate_ai_balance_report(self):
        """生成AI和平衡性测试报告"""
        print("\n📊 生成AI和平衡性测试报告...")
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        # 统计测试结果
        total_tests = len(self.test_results)
        successful_tests = len([test for test in self.test_results if test["结果"] not in ["失败", "错误"]])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # 计算AI性能指标
        ai_metrics = {}
        for metric, scores in self.ai_performance.items():
            if scores:
                ai_metrics[metric] = {
                    "平均分": sum(scores) / len(scores),
                    "最高分": max(scores),
                    "最低分": min(scores),
                    "样本数": len(scores)
                }
        
        report = {
            "测试时间": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "测试时长": f"{duration:.2f}秒",
            "总测试数": total_tests,
            "成功测试数": successful_tests,
            "成功率": f"{success_rate:.1f}%",
            "AI性能指标": ai_metrics,
            "详细测试日志": self.test_results,
            "综合评估": {
                "AI智能程度": "优秀" if success_rate >= 90 else "良好" if success_rate >= 70 else "需改进",
                "游戏平衡性": "已测试" if successful_tests >= 10 else "数据不足",
                "系统稳定性": "稳定" if success_rate >= 85 else "一般"
            }
        }
        
        # 保存报告
        with open("ai_balance_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📋 AI和平衡性测试报告已保存: ai_balance_test_report.json")
        print(f"⭐ 总体评分: {success_rate:.1f}%")
        
        return report
    
    def run_full_ai_balance_test(self):
        """运行完整的AI和平衡性测试"""
        print("=" * 60)
        print("🤖 天机变游戏 - AI智能程度和游戏平衡性测试")
        print("=" * 60)
        
        # 1. AI决策质量测试
        self.test_ai_decision_quality(20)
        
        # 2. 游戏平衡性测试
        self.test_game_balance(15)
        
        # 3. AI适应性测试
        self.test_ai_adaptability()
        
        # 4. 生成报告
        report = self.generate_ai_balance_report()
        
        print("\n" + "=" * 60)
        print("🎉 AI智能程度和游戏平衡性测试完成!")
        print("=" * 60)
        
        return report

def main():
    """主函数"""
    tester = AIBalanceTest()
    return tester.run_full_ai_balance_test()

if __name__ == "__main__":
    main()