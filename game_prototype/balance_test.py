"""
游戏平衡性测试脚本
自动化测试多人游戏的平衡性
"""

import random
import statistics
from typing import List, Dict, Any
from game_state import GameState, Player
from multiplayer_manager import MultiplayerManager
from config_manager import ConfigManager
from enhanced_game_mechanics import EnhancedGameMechanics
from yijing_education_system import YijingEducationSystem

class BalanceTestRunner:
    """平衡性测试运行器"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.education_system = YijingEducationSystem()
        self.enhanced_mechanics = EnhancedGameMechanics()
        self.test_results = []
    
    def run_test_game(self, num_players: int, max_turns: int = 30) -> Dict[str, Any]:
        """运行一局测试游戏"""
        # 创建测试玩家
        player_names = [f"测试玩家{i+1}" for i in range(num_players)]
        
        # 初始化游戏
        manager = MultiplayerManager(num_players)
        players = manager.create_players(player_names)
        
        # 创建简化的游戏状态
        from game_state import GameState
        game_state = GameState(players)
        game_state.current_player_index = 0
        game_state.turn_count = 0
        
        # 初始化教育系统
        for name in player_names:
            self.education_system.initialize_player(name)
        
        turn_count = 0
        winner = None
        
        # 模拟游戏进行
        while turn_count < max_turns and not winner:
            turn_count += 1
            
            # 每5轮推进季节
            if turn_count % 5 == 1 and turn_count > 1:
                self.enhanced_mechanics.advance_season()
            
            current_player = game_state.get_current_player()
            
            # 模拟AI决策（随机选择动作）
            self._simulate_player_turn(current_player, game_state)
            
            # 检查胜利条件
            victory_threshold = self.config.get("victory_conditions.base_dao_xing", 100)
            if num_players >= 6:
                victory_threshold = int(victory_threshold * 0.8)
            elif num_players >= 4:
                victory_threshold = int(victory_threshold * 0.9)
            
            if current_player.dao_xing >= victory_threshold:
                winner = current_player
                break
            
            game_state.advance_turn()
        
        # 收集测试结果
        result = {
            'num_players': num_players,
            'turns_played': turn_count,
            'winner': winner.name if winner else None,
            'final_scores': {p.name: p.dao_xing for p in game_state.players},
            'game_completed': winner is not None,
            'average_score': statistics.mean([p.dao_xing for p in game_state.players]),
            'score_variance': statistics.variance([p.dao_xing for p in game_state.players]) if len(game_state.players) > 1 else 0
        }
        
        return result
    
    def _simulate_player_turn(self, player: Player, game_state: GameState):
        """模拟玩家回合"""
        # 简单的AI逻辑：随机选择动作
        actions = ['play_card', 'meditate', 'study']
        
        if len(player.hand) == 0:
            # 没有手牌时只能冥想或学习
            actions = ['meditate', 'study']
        
        action = random.choice(actions)
        
        if action == 'play_card' and player.hand:
            # 随机出牌
            card = random.choice(player.hand)
            if player.qi >= 1:  # 基础出牌消耗
                player.hand.remove(card)
                player.qi = max(0, player.qi - 1)
                player.dao_xing += random.randint(1, 3)  # 随机道行增长
                # 尝试从卦牌学习知识
                try:
                    self.education_system.learn_from_card(player.name, card)
                except:
                    pass  # 忽略学习错误
        
        elif action == 'meditate':
            # 冥想恢复气
            if player.cheng_yi >= 1:
                player.cheng_yi -= 1
                player.qi = min(player.qi + 3, 25)  # 最大气值限制
        
        elif action == 'study':
            # 学习增加道行
            if player.qi >= 1:
                player.qi -= 1
                player.dao_xing += random.randint(1, 2)
    
    def run_balance_tests(self, tests_per_config: int = 10) -> Dict[str, Any]:
        """运行完整的平衡性测试"""
        print("🧪 开始游戏平衡性测试...")
        print("=" * 50)
        
        test_configs = [
            {'players': 2, 'description': '双人对战'},
            {'players': 4, 'description': '四人混战'},
            {'players': 6, 'description': '六人大战'},
            {'players': 8, 'description': '八人终极战'}
        ]
        
        all_results = {}
        
        for config in test_configs:
            num_players = config['players']
            description = config['description']
            
            print(f"\n🎮 测试配置: {description} ({num_players}人)")
            print("-" * 30)
            
            config_results = []
            
            for i in range(tests_per_config):
                print(f"  进行第{i+1}/{tests_per_config}局测试...", end=" ")
                
                result = self.run_test_game(num_players)
                config_results.append(result)
                
                status = "✅ 完成" if result['game_completed'] else "⏰ 超时"
                print(status)
            
            # 分析结果
            analysis = self._analyze_results(config_results)
            all_results[f"{num_players}人游戏"] = {
                'config': config,
                'results': config_results,
                'analysis': analysis
            }
            
            # 显示分析结果
            print(f"\n📊 {description}分析结果:")
            print(f"  完成率: {analysis['completion_rate']:.1%}")
            print(f"  平均回合数: {analysis['avg_turns']:.1f}")
            print(f"  平均分数: {analysis['avg_final_score']:.1f}")
            print(f"  分数方差: {analysis['score_variance']:.1f}")
            print(f"  胜利分布: {analysis['winner_distribution']}")
        
        return all_results
    
    def _analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析测试结果"""
        completed_games = [r for r in results if r['game_completed']]
        
        analysis = {
            'total_games': len(results),
            'completed_games': len(completed_games),
            'completion_rate': len(completed_games) / len(results) if results else 0,
            'avg_turns': statistics.mean([r['turns_played'] for r in results]),
            'avg_final_score': statistics.mean([r['average_score'] for r in results]),
            'score_variance': statistics.mean([r['score_variance'] for r in results]),
            'winner_distribution': {}
        }
        
        # 分析胜利者分布
        if completed_games:
            winners = [r['winner'] for r in completed_games]
            for winner in set(winners):
                analysis['winner_distribution'][winner] = winners.count(winner)
        
        return analysis
    
    def generate_balance_report(self, results: Dict[str, Any]) -> str:
        """生成平衡性报告"""
        report_lines = [
            "🎯 游戏平衡性测试报告",
            "=" * 50,
            ""
        ]
        
        for config_name, data in results.items():
            analysis = data['analysis']
            
            report_lines.extend([
                f"📋 {config_name}:",
                f"  • 游戏完成率: {analysis['completion_rate']:.1%}",
                f"  • 平均游戏时长: {analysis['avg_turns']:.1f}回合",
                f"  • 平均最终分数: {analysis['avg_final_score']:.1f}",
                f"  • 分数方差: {analysis['score_variance']:.1f}",
                ""
            ])
            
            if analysis['winner_distribution']:
                report_lines.append("  🏆 胜利者分布:")
                for winner, count in analysis['winner_distribution'].items():
                    percentage = count / analysis['completed_games'] * 100
                    report_lines.append(f"    - {winner}: {count}次 ({percentage:.1f}%)")
                report_lines.append("")
        
        # 添加建议
        report_lines.extend([
            "💡 平衡性建议:",
            "  • 如果某配置完成率过低(<70%)，考虑调整胜利条件",
            "  • 如果分数方差过大(>50)，考虑调整资源平衡",
            "  • 如果胜利分布不均匀，考虑调整起始位置优势",
            ""
        ])
        
        return "\n".join(report_lines)

def main():
    """主函数"""
    tester = BalanceTestRunner()
    
    # 运行测试
    results = tester.run_balance_tests(tests_per_config=5)  # 每个配置测试5局
    
    # 生成报告
    report = tester.generate_balance_report(results)
    print("\n" + report)
    
    # 保存报告到文件
    with open("balance_test_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("📄 详细报告已保存到 balance_test_report.txt")

if __name__ == "__main__":
    main()