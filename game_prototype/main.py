#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天机变 - 易经主题策略游戏 (增强版)
支持1-8人游戏，融入易经教育功能
"""

import random
import sys
from typing import Dict, Any, Optional, List

# 核心游戏模块
from game_state import GameState, Player
from game_data import GAME_DECK, EMPEROR_AVATAR, HERMIT_AVATAR
from bot_player import get_bot_choice

# 新增模块
from multiplayer_manager import MultiplayerManager, create_multiplayer_game
from yijing_education_system import YijingEducationSystem, YijingKnowledge
from enhanced_game_mechanics import enhanced_mechanics, get_combo_effect, get_seasonal_multiplier
from enhanced_card_data import get_card_by_name, ENHANCED_CARDS
from config_manager import ConfigManager
from enhanced_ui_experience import EnhancedUIExperience, MessageType
from interactive_game_flow import InteractiveGameFlow
from game_utils import (
    format_game_header, format_player_info, format_season_info,
    get_user_choice, get_user_number, simulate_ai_thinking,
    generate_strategy_hint, format_achievement_notification,
    validate_card_play, format_game_summary, get_random_wisdom_quote
)

# 全局系统实例
config_manager = ConfigManager()
enhanced_ui = EnhancedUIExperience()
interactive_flow = InteractiveGameFlow()
education_system = YijingEducationSystem()
multiplayer_manager = None

def setup_game(num_players: int = 2, player_names: Optional[List[str]] = None) -> tuple[GameState, MultiplayerManager]:
    """初始化游戏状态（增强版）"""
    # 从配置获取玩家数量限制
    min_players = config_manager.get("game_settings.min_players", 1)
    max_players = config_manager.get("game_settings.max_players", 8)
    
    if not min_players <= num_players <= max_players:
        raise ValueError(f"游戏支持{min_players}-{max_players}人，请输入正确的人数")
    
    # 使用多人游戏管理器创建游戏
    players, manager = create_multiplayer_game(num_players, player_names)
    
    # 创建游戏状态
    game_state = GameState(players=players)
    
    # 根据人数调整卡组大小
    deck = GAME_DECK.copy()
    deck_multiplier = manager.get_deck_size_multiplier()
    if deck_multiplier > 1.0:
        # 多人游戏需要更多卡牌，复制部分卡牌
        additional_cards = int(len(deck) * (deck_multiplier - 1.0))
        deck.extend(random.choices(deck, k=additional_cards))
    
    random.shuffle(deck)
    
    # 从配置获取初始手牌数量
    initial_hand_size = config_manager.get("game_settings.initial_hand_size", manager.balance.initial_hand_size)
    for player in game_state.players:
        for _ in range(initial_hand_size):
            if deck:
                player.hand.append(deck.pop())
        
        # 初始化玩家的教育系统
        education_system.initialize_player(player.name)
    
    return game_state, manager

def display_game_state(game_state: GameState, current_player: Player = None, season_info: Dict[str, Any] = None):
    """显示游戏状态"""
    try:
        # 使用增强UI显示游戏界面
        if current_player is None:
            current_player = game_state.get_current_player()
        if season_info is None:
            season_info = enhanced_mechanics.get_current_season_info()
        
        enhanced_ui.display_game_screen(game_state=game_state, player=current_player, season_info=season_info, show_help=False)
        
    except Exception as e:
        print(f"显示游戏状态时出错: {e}")
        # 回退到基本显示
        print(format_game_header(game_state.turn))
        if current_player is None:
            current_player = game_state.get_current_player()
        print(f"🎯 当前玩家: {current_player.name}")
        for player in game_state.players:
            print(format_player_info(player, player == current_player))
        print("继续游戏...")

def show_action_menu(player: Player) -> str:
    """显示行动菜单并获取用户选择"""
    try:
        # 使用增强UI创建菜单
        menu_options = [
            {"key": "1", "text": "出牌", "description": "消耗1气，使用手牌"},
            {"key": "2", "text": "移动", "description": "消耗1气，改变位置"},
            {"key": "3", "text": "冥想", "description": "恢复2气，调息养神"},
            {"key": "4", "text": "研习", "description": "消耗2气，获得1道行"},
            {"key": "5", "text": "易经学习", "description": "学习易经智慧"},
            {"key": "6", "text": "查看学习进度", "description": "查看学习进度"},
            {"key": "7", "text": "查看状态", "description": "查看详细信息"},
            {"key": "8", "text": "结束回合", "description": "结束当前回合"},
            {"key": "0", "text": "退出游戏", "description": "退出游戏"}
        ]
        
        menu_display = enhanced_ui.create_enhanced_menu("选择您的行动", menu_options)
        print(menu_display)
        
        while True:
            choice = enhanced_ui.get_enhanced_input(
                "请输入选项", 
                "choice", 
                ["0", "1", "2", "3", "4", "5", "6", "7", "8"]
            )
            if choice in ['0', '1', '2', '3', '4', '5', '6', '7', '8']:
                return choice
            print(enhanced_ui.create_notification("无效选择，请输入0-8之间的数字", MessageType.WARNING))
            
    except KeyboardInterrupt:
        print("\n游戏被中断")
        return "0"
    except Exception as e:
        print(f"显示菜单时出错: {e}")
        return "0"

def handle_play_card(game_state: GameState, player: Player):
    """处理出牌行动（增强版）"""
    if not player.hand:
        print("❌ 手中没有卡牌!")
        return game_state
    
    # 显示当前季节信息
    season_info = enhanced_mechanics.get_current_season_info()
    print(f"\n🌸 当前季节：{season_info['season']} - {season_info['special_effect']}")
    
    print(f"\n{player.name} 的手牌:")
    for i, card_name in enumerate(player.hand):
        # 获取增强卡牌信息
        enhanced_card = get_card_by_name(card_name)
        if enhanced_card:
            # 检查季节性奖励
            qi_mult, dao_mult = get_seasonal_multiplier(card_name)
            season_bonus = "⭐" if qi_mult > 1.0 or dao_mult > 1.0 else ""
            
            print(f"{i+1}. {card_name} {season_bonus}(消耗: {enhanced_card.cost}气, 效果: +{enhanced_card.qi_effect}气 +{enhanced_card.dao_xing_effect}道行)")
        else:
            print(f"{i+1}. {card_name} (基础效果: 消耗1气, +1道行)")
    
    # 显示策略提示
    tips = enhanced_mechanics.get_strategic_advice(player.hand, {})
    if tips:
        print(f"\n💡 策略提示：")
        for tip in tips[:2]:  # 显示前两个提示
            print(f"  • {tip}")
    
    try:
        choice = int(input("\n选择要出的牌 (输入序号): ")) - 1
        if 0 <= choice < len(player.hand):
            card_name = player.hand[choice]
            enhanced_card = get_card_by_name(card_name)
            
            # 确定卡牌属性
            if enhanced_card:
                cost = enhanced_card.cost
                qi_effect = enhanced_card.qi_effect
                dao_effect = enhanced_card.dao_xing_effect
            else:
                cost = 1
                qi_effect = 0
                dao_effect = 1
            
            if player.qi >= cost:
                # 计算季节性奖励
                qi_mult, dao_mult = get_seasonal_multiplier(card_name)
                actual_qi_effect = int(qi_effect * qi_mult)
                actual_dao_effect = int(dao_effect * dao_mult)
                
                # 出牌
                player.qi -= cost
                player.qi += actual_qi_effect
                player.dao_xing += actual_dao_effect
                
                played_card = player.hand.pop(choice)
                
                # 记录出牌历史（用于连招检测）
                if not hasattr(player, 'recent_cards'):
                    player.recent_cards = []
                player.recent_cards.append(played_card)
                if len(player.recent_cards) > 5:  # 只保留最近5张牌
                    player.recent_cards.pop(0)
                
                print(f"✅ {player.name} 出牌: {played_card}")
                
                # 显示季节性奖励
                if qi_mult > 1.0 or dao_mult > 1.0:
                    print(f"🌟 季节奖励: 气效果 x{qi_mult:.1f}, 道行效果 x{dao_mult:.1f}")
                
                print(f"💫 效果: 气 {player.qi-actual_qi_effect}→{player.qi}, 道行 {player.dao_xing-actual_dao_effect}→{player.dao_xing}")
                
                # 检查连招
                if len(player.recent_cards) >= 2:
                    combo_effect = get_combo_effect(player.recent_cards[-2:])  # 检查最近两张牌
                    if combo_effect:
                        print(f"\n🎊 连招成功: {combo_effect.name}!")
                        print(f"📜 {combo_effect.description}")
                        
                        # 应用连招效果
                        player.qi += combo_effect.qi_bonus
                        player.dao_xing += combo_effect.dao_xing_bonus
                        
                        print(f"🎁 连招奖励: +{combo_effect.qi_bonus}气 +{combo_effect.dao_xing_bonus}道行")
                        
                        if combo_effect.special_effect:
                            print(f"✨ 特殊效果: {combo_effect.special_effect}")
                        
                        # 记录连招统计
                        if not hasattr(player, 'combos_performed'):
                            player.combos_performed = 0
                        player.combos_performed += 1
                        
                        # 获得智慧点数
                        progress = education_system.get_player_progress(player.name)
                        if progress:
                            education_system.add_wisdom_points(player.name, combo_effect.wisdom_points)
                            print(f"🧠 获得智慧点数: +{combo_effect.wisdom_points}")
                
                # 从卡牌学习易经知识
                if enhanced_card:
                    knowledge = YijingKnowledge(
                        gua_name=enhanced_card.chinese_name,
                        description=enhanced_card.judgment_meaning,
                        philosophy=enhanced_card.philosophy,
                        wisdom=enhanced_card.life_wisdom
                    )
                    education_system.learn_from_card(player.name, knowledge)
                    print(f"📚 从 {enhanced_card.chinese_name} 卦中学到了易经智慧")
                
            else:
                print(f"❌ 气不足! 需要 {cost} 气，当前只有 {player.qi} 气")
        else:
            print("❌ 无效选择!")
    except ValueError:
        print("❌ 请输入有效数字!")
    
    return game_state

def handle_move(game_state: GameState, player: Player):
    """处理移动行动"""
    zones = ["天", "地", "人"]
    print(f"\n当前位置: {player.zone}")
    print("可移动到: " + ", ".join(zones))
    
    new_zone = input("请选择目标位置 (或按回车取消): ").strip()
    
    if new_zone in zones and new_zone != player.zone:
        if player.qi >= 1:
            player.zone = new_zone
            player.qi -= 1
            print(f"✅ {player.name} 移动到 {new_zone}")
        else:
            print("❌ 气不足，无法移动!")
    else:
        print("❌ 无效的移动选择!")
    
    return game_state

def handle_meditate(game_state: GameState, player: Player):
    """处理冥想行动"""
    if player.qi < 5:
        player.qi += 2
        player.cheng_yi += 1
        print(f"✅ {player.name} 冥想，恢复2点气，获得1点诚意")
    else:
        print("❌ 气已充足，无需冥想!")
    
    return game_state

def handle_study(game_state: GameState, player: Player):
    """处理研习行动"""
    if player.qi >= 2:
        player.qi -= 2
        player.dao_xing += 2
        print(f"✅ {player.name} 研习，消耗2点气，获得2点道行")
        
        # 从研习中学习易经知识
        knowledge = education_system.get_random_wisdom()
        if knowledge:
            print(f"\n📚 易经启发：{knowledge.title}")
            print(f"💡 {knowledge.practical_wisdom}")
    else:
        print("❌ 气不足，无法研习!")
    
    return game_state

def handle_yijing_learning(player: Player):
    """处理易经学习"""
    print(f"\n=== {player.name} 的易经学习 ===")
    
    # 显示每日智慧
    daily_wisdom = education_system.get_daily_wisdom()
    print(f"📜 今日智慧：{daily_wisdom}")
    
    # 获取学习建议
    suggestion = education_system.get_learning_suggestion(player.name)
    print(f"\n📚 学习建议：{suggestion}")
    
    # 提供学习选项
    print("\n请选择学习内容：")
    print("1. 随机易经知识")
    print("2. 解释手牌含义")
    print("3. 易经小测验")
    print("4. 返回")
    
    choice = input("请选择 (1-4): ").strip()
    
    if choice == "1":
        knowledge = education_system.get_random_wisdom()
        print(f"\n【{knowledge.title}】")
        print(f"{knowledge.content}")
        print(f"\n💡 实用智慧：{knowledge.practical_wisdom}")
        
    elif choice == "2":
        if player.hand:
            print("\n请选择要解释的卡牌：")
            for i, card in enumerate(player.hand):
                print(f"{i+1}. {card}")
            
            try:
                card_choice = int(input("请选择卡牌编号: ")) - 1
                if 0 <= card_choice < len(player.hand):
                    card = player.hand[card_choice]
                    explanation = education_system.explain_card_meaning(card)
                    print(f"\n{explanation}")
                else:
                    print("无效的卡牌编号")
            except ValueError:
                print("请输入有效的数字")
        else:
            print("你没有手牌可以解释")
            
    elif choice == "3":
        quiz = education_system.create_learning_quiz(player.name)
        print(f"\n❓ {quiz['question']}")
        for i, option in enumerate(quiz['options']):
            print(f"{i+1}. {option}")
        
        try:
            answer = int(input("请选择答案 (1-4): ")) - 1
            if answer == quiz['correct']:
                print("✅ 回答正确！")
                # 奖励一点诚意
                player.cheng_yi += 1
                print(f"获得1点诚意奖励！当前诚意：{player.cheng_yi}")
            else:
                print("❌ 回答错误")
            print(f"\n📖 解释：{quiz['explanation']}")
        except ValueError:
            print("请输入有效的数字")

def handle_learning_progress(player: Player):
    """查看学习进度"""
    progress = education_system.get_player_progress(player.name)
    if progress:
        print(f"\n=== {player.name} 的学习进度 ===")
        print(f"🎓 当前等级：{progress.current_level.value}")
        print(f"🌟 智慧点数：{progress.wisdom_points}")
        print(f"📚 已掌握概念：{len(progress.mastered_concepts)}")
        
        if progress.mastered_concepts:
            print("已学习的内容：")
            for concept in progress.mastered_concepts[:5]:  # 显示前5个
                print(f"  • {concept}")
            if len(progress.mastered_concepts) > 5:
                print(f"  ... 还有 {len(progress.mastered_concepts) - 5} 个")
        
        # 显示学习建议
        suggestion = education_system.get_learning_suggestion(player.name)
        print(f"\n💡 建议：{suggestion}")
    else:
        print("还没有学习记录，开始你的易经之旅吧！")

def check_victory_conditions(game_state: GameState) -> Optional[Player]:
    """检查胜利条件"""
    for player in game_state.players:
        if player.dao_xing >= 10:
            return player
    return None

def run_player_turn(game_state: GameState, player: Player, is_ai: bool = False) -> GameState:
    """运行玩家回合"""
    if is_ai:
        # 简化的AI逻辑
        action = get_bot_choice(game_state, player)
        if action == "play_card" and player.hand and player.qi >= 1:
            card = random.choice(player.hand)
            player.hand.remove(card)
            player.qi -= 1
            player.dao_xing += 1
            print(f"🤖 {player.name} 出牌: {card}")
        elif action == "meditate" and player.qi < 5:
            player.qi += 2
            player.cheng_yi += 1
            print(f"🤖 {player.name} 冥想")
        else:
            print(f"🤖 {player.name} 结束回合")
        return game_state
    
    # 人类玩家回合
    while True:
        choice = show_action_menu(player)
        
        if choice == "0":
            print("👋 游戏结束!")
            sys.exit(0)
        elif choice == "1":
            game_state = handle_play_card(game_state, player)
        elif choice == "2":
            game_state = handle_move(game_state, player)
        elif choice == "3":
            game_state = handle_meditate(game_state, player)
        elif choice == "4":
            game_state = handle_study(game_state, player)
        elif choice == "5":
            handle_yijing_learning(player)
            continue
        elif choice == "6":
            handle_learning_progress(player)
            continue
        elif choice == "7":
            display_game_state(game_state)
            continue
        elif choice == "8":
            print(f"✅ {player.name} 结束回合")
            break
        else:
            print("❌ 无效选择，请重新输入!")
            continue
        
        # 检查胜利条件
        winner = check_victory_conditions(game_state)
        if winner:
            print(f"\n🎉 恭喜 {winner.name} 获得胜利!")
            print(f"最终道行: {winner.dao_xing}")
            return game_state
    
    return game_state

def main_game_loop(num_players: int = 2, ai_players: int = 1, player_names: Optional[List[str]] = None):
    """主游戏循环（增强版）"""
    print("🎮 天机变 - 易经策略游戏 (增强版)")
    print("=" * 50)
    
    # 初始化游戏
    game_state, manager = setup_game(num_players, player_names)
    
    # 显示游戏信息
    game_info = manager.get_game_info()
    print(f"\n🎯 游戏模式：{game_info['mode']}")
    print(f"👥 玩家数量：{game_info['players']}")
    print(f"🏆 胜利条件：率先达到 {game_info['victory_dao_xing']} 点道行")
    
    # 显示策略提示
    tips = manager.get_strategic_tips()
    print(f"\n💡 策略提示：")
    for tip in tips[:2]:  # 显示前两个提示
        print(f"  • {tip}")
    
    # 显示每日智慧
    daily_wisdom = education_system.get_daily_wisdom()
    print(f"\n📜 今日智慧：{daily_wisdom}")
    
    # 游戏主循环
    turn_count = 0
    max_turns = 100  # 多人游戏可能需要更多回合
    victory_dao_xing = manager.get_victory_condition()
    
    while turn_count < max_turns:
        turn_count += 1
        print(f"\n{'='*25} 第 {turn_count} 轮 {'='*25}")
        
        # 每5轮推进一个季节
        if turn_count % 5 == 1 and turn_count > 1:
            enhanced_mechanics.advance_season()
            season_info = enhanced_mechanics.get_current_season_info()
            print(f"\n🌸 季节变化！现在是{season_info['season']}季")
            print(f"🎋 {season_info['special_effect']}")
        
        display_game_state(game_state)
        
        current_player = game_state.get_current_player()
        is_ai = game_state.current_player_index >= (num_players - ai_players)
        
        game_state = run_player_turn(game_state, current_player, is_ai)
        
        # 检查成就
        player_stats = {
            'combos_performed': getattr(current_player, 'combos_performed', 0),
            'unique_cards_played': len(set(getattr(current_player, 'recent_cards', []))),
            'dao_xing': current_player.dao_xing,
            'wisdom_points': education_system.get_player_progress(current_player.name).wisdom_points if education_system.get_player_progress(current_player.name) else 0
        }
        
        achievements = enhanced_mechanics.check_achievements(player_stats)
        for achievement in achievements:
            if not hasattr(current_player, 'completed_achievements'):
                current_player.completed_achievements = set()
            
            if achievement.name not in current_player.completed_achievements:
                current_player.completed_achievements.add(achievement.name)
                print(f"\n🏆 {current_player.name} 获得成就: {achievement.name}")
                print(f"📜 {achievement.description}")
                
                # 应用成就奖励
                current_player.qi += achievement.reward_qi
                current_player.dao_xing += achievement.reward_dao_xing
                if achievement.reward_wisdom > 0:
                    education_system.add_wisdom_points(current_player.name, achievement.reward_wisdom)
                
                print(f"🎁 奖励: +{achievement.reward_qi}气 +{achievement.reward_dao_xing}道行 +{achievement.reward_wisdom}智慧")
        
        # 检查胜利条件（使用动态胜利条件）
        if current_player.dao_xing >= victory_dao_xing:
            print(f"\n🎉 游戏结束！{current_player.name} 获得胜利！")
            print(f"🏆 最终道行：{current_player.dao_xing}/{victory_dao_xing}")
            
            # 显示学习成果
            progress = education_system.get_player_progress(current_player.name)
            if progress:
                print(f"📚 易经学习等级：{progress.current_level.value}")
                print(f"🌟 智慧点数：{progress.wisdom_points}")
            
            # 显示成就统计
            if hasattr(current_player, 'completed_achievements'):
                print(f"🏆 获得成就数量：{len(current_player.completed_achievements)}")
            
            return
        
        # 下一个玩家
        game_state.advance_turn()
    
    print(f"\n⏰ 游戏达到最大回合数({max_turns})，平局！")
    
    # 显示所有玩家的最终状态
    print("\n📊 最终排名：")
    sorted_players = sorted(game_state.players, key=lambda p: p.dao_xing, reverse=True)
    for i, player in enumerate(sorted_players):
        progress = education_system.get_player_progress(player.name)
        wisdom_info = f" (智慧等级: {progress.current_level.value})" if progress else ""
        print(f"{i+1}. {player.name}: {player.dao_xing} 道行{wisdom_info}")

def main():
    """主函数"""
    try:
        # 使用交互式游戏流程
        enhanced_ui.clear_screen()
        
        # 显示欢迎界面
        print(enhanced_ui.create_title_banner("天机变", "易经策略游戏"))
        
        # 游戏设置
        while True:
            try:
                num_players = int(enhanced_ui.get_enhanced_input(
                    "请输入玩家总数 (1-8)", 
                    "number"
                ) or "2")
                if 1 <= num_players <= 8:
                    break
                print(enhanced_ui.create_notification("请输入1-8之间的数字!", MessageType.WARNING))
            except ValueError:
                print(enhanced_ui.create_notification("请输入有效数字!", MessageType.ERROR))
        
        ai_players = 0
        if num_players > 1:
            while True:
                try:
                    ai_players = int(enhanced_ui.get_enhanced_input(
                        f"请输入AI玩家数量 (0-{num_players})", 
                        "number"
                    ) or "1")
                    if 0 <= ai_players <= num_players:
                        break
                    print(enhanced_ui.create_notification(f"AI玩家数量应在0-{num_players}之间!", MessageType.WARNING))
                except ValueError:
                    print(enhanced_ui.create_notification("请输入有效数字!", MessageType.ERROR))
        
        # 获取玩家名称
        player_names = []
        human_players = num_players - ai_players
        
        if human_players > 0:
            print(enhanced_ui.create_notification(f"请为{human_players}位人类玩家设置名称", MessageType.INFO))
            for i in range(human_players):
                name = enhanced_ui.get_enhanced_input(f"玩家{i+1}的名称 (按回车使用默认名称)", "text").strip()
                if not name:
                    name = f"玩家{i+1}"
                player_names.append(name)
                # 为每个玩家初始化学习进度
                education_system.initialize_player_progress(name)
        
        # 添加AI玩家名称
        for i in range(ai_players):
            ai_name = f"AI-{['天机', '玄武', '青龙', '白虎', '朱雀', '麒麟', '凤凰', '神龟'][i % 8]}"
            player_names.append(ai_name)
            education_system.initialize_player_progress(ai_name)
        
        # 显示游戏开始信息
        print(enhanced_ui.create_notification("🎮 准备开始游戏...", MessageType.SUCCESS))
        print(enhanced_ui.create_notification(f"👥 参与玩家：{', '.join(player_names)}", MessageType.INFO))
        enhanced_ui.show_loading_animation("初始化游戏", 2.0)
        
        # 开始游戏
        main_game_loop(num_players, ai_players, player_names)
        
    except KeyboardInterrupt:
        print(enhanced_ui.create_notification("\n👋 感谢游玩天机变！愿易经智慧伴随您的人生之路！", MessageType.INFO))
    except Exception as e:
        print(enhanced_ui.create_notification(f"游戏出现错误: {e}", MessageType.ERROR))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
