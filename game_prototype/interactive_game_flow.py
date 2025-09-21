#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式游戏流程系统
提供更流畅、直观的游戏交互体验
"""

import time
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from game_state import GameState, Player
from enhanced_ui_experience import EnhancedUIExperience, MessageType
from enhanced_card_data import get_card_by_name
from yijing_education_system import YijingEducationSystem
from enhanced_game_mechanics import enhanced_mechanics, get_combo_effect, get_seasonal_multiplier
from config_manager import ConfigManager

class GamePhase(Enum):
    """游戏阶段"""
    SETUP = "setup"
    PLAYING = "playing"
    CARD_SELECTION = "card_selection"
    ACTION_EXECUTION = "action_execution"
    LEARNING = "learning"
    END_TURN = "end_turn"
    GAME_OVER = "game_over"

@dataclass
class ActionResult:
    """行动结果"""
    success: bool
    message: str
    effects: Dict[str, int]
    notifications: List[str]
    achievements: List[str]

class InteractiveGameFlow:
    """交互式游戏流程管理器"""
    
    def __init__(self):
        self.ui = EnhancedUIExperience()
        self.config_manager = ConfigManager()
        self.education_system = YijingEducationSystem()
        self.current_phase = GamePhase.SETUP
        self.tutorial_mode = False
        self.auto_save_enabled = True
        
    def start_game_session(self, game_state: GameState) -> None:
        """开始游戏会话"""
        self.ui.clear_screen()
        
        # 显示欢迎界面
        self._show_welcome_screen()
        
        # 检查是否需要教程
        if self._should_show_tutorial():
            self.tutorial_mode = True
            self._show_tutorial()
        
        # 开始主游戏循环
        self._main_game_loop(game_state)
    
    def _show_welcome_screen(self) -> None:
        """显示欢迎界面"""
        welcome_text = """
        🌟 欢迎来到天机变 - 易经策略游戏 🌟
        
        在这个游戏中，您将：
        • 🎯 通过策略出牌获得道行
        • 📚 学习易经六十四卦的智慧
        • 🌸 体验四季变化的游戏机制
        • 🏆 解锁各种成就和奖励
        
        愿易经的智慧指引您的游戏之路！
        """
        
        print(self.ui.create_title_banner("天机变", "易经策略游戏"))
        print(self.ui.colorize(welcome_text, self.ui.theme.text_color))
        
        # 显示加载动画
        self.ui.show_loading_animation("初始化游戏", 2.0)
    
    def _should_show_tutorial(self) -> bool:
        """检查是否应该显示教程"""
        # 检查配置或玩家历史
        show_tutorial = self.config_manager.get("game_settings.show_tutorial", True)
        
        if show_tutorial:
            choice = self.ui.get_enhanced_input(
                "是否需要查看游戏教程？(y/n)", 
                "choice", 
                ["y", "n", "yes", "no"]
            )
            return choice.lower() in ["y", "yes"]
        
        return False
    
    def _show_tutorial(self) -> None:
        """显示游戏教程"""
        tutorial_steps = [
            {
                "title": "游戏目标",
                "content": "通过出牌、移动、冥想等行动获得道行，率先达到胜利条件的玩家获胜。",
                "tips": ["道行是胜利的关键", "合理管理气的消耗"]
            },
            {
                "title": "基本行动",
                "content": "出牌消耗气获得道行，移动改变位置，冥想恢复气，研习提升道行。",
                "tips": ["每种行动都有其用途", "根据情况选择最佳行动"]
            },
            {
                "title": "易经学习",
                "content": "游戏融入了易经教学，您可以从卡牌中学习卦象含义和人生智慧。",
                "tips": ["学习易经可获得智慧点数", "智慧点数可用于解锁特殊能力"]
            },
            {
                "title": "季节系统",
                "content": "游戏有四季变化，不同季节某些卡牌会有额外效果。",
                "tips": ["注意季节变化", "利用季节奖励制定策略"]
            }
        ]
        
        for i, step in enumerate(tutorial_steps, 1):
            self.ui.clear_screen()
            print(self.ui.create_title_banner(f"教程 {i}/{len(tutorial_steps)}", step["title"]))
            print()
            
            print(self.ui.colorize(step["content"], self.ui.theme.text_color))
            print()
            
            print(self.ui.create_section_header("小贴士"))
            for tip in step["tips"]:
                print(self.ui.colorize(f"💡 {tip}", self.ui.theme.secondary_color))
            
            print()
            input(self.ui.colorize("按回车继续...", self.ui.theme.dim_color))
        
        print(self.ui.create_notification("教程完成！开始游戏吧！", MessageType.SUCCESS))
        time.sleep(1)
    
    def _main_game_loop(self, game_state: GameState) -> None:
        """主游戏循环"""
        self.current_phase = GamePhase.PLAYING
        
        while not self._check_game_end_conditions(game_state):
            current_player = game_state.get_current_player()
            
            # 显示游戏界面
            self._display_turn_interface(game_state, current_player)
            
            # 处理玩家回合
            if self._is_ai_player(current_player):
                self._handle_ai_turn(game_state, current_player)
            else:
                self._handle_human_turn(game_state, current_player)
            
            # 检查回合结束条件
            if self._should_end_turn(game_state, current_player):
                self._end_turn(game_state)
        
        self._handle_game_end(game_state)
    
    def _display_turn_interface(self, game_state: GameState, player: Player) -> None:
        """显示回合界面"""
        # 获取季节信息
        season_info = enhanced_mechanics.get_current_season_info()
        
        # 显示主界面
        self.ui.display_game_screen(game_state, player, season_info)
        
        # 显示当前玩家的详细信息
        print(self.ui.create_section_header(f"{player.name} 的回合"))
        print()
        
        # 显示手牌
        enhanced_cards = {card: get_card_by_name(card).__dict__ for card in player.hand if get_card_by_name(card)}
        print(self.ui.create_card_display(player.hand, enhanced_cards))
        print()
        
        # 显示策略提示
        if self.tutorial_mode or random.random() < 0.3:  # 30%概率显示提示
            tips = self._generate_contextual_tips(game_state, player)
            if tips:
                print(self.ui.create_section_header("策略提示"))
                for tip in tips[:2]:
                    print(self.ui.colorize(f"💡 {tip}", self.ui.theme.secondary_color))
                print()
    
    def _generate_contextual_tips(self, game_state: GameState, player: Player) -> List[str]:
        """生成上下文相关的提示"""
        tips = []
        
        # 资源状态提示
        if player.qi < 3:
            tips.append("气不足，考虑冥想恢复或使用低消耗卡牌")
        
        if player.dao_xing >= 8:
            tips.append("道行很高了，距离胜利不远！")
        
        # 手牌提示
        if len(player.hand) > 7:
            tips.append("手牌较多，可以积极出牌")
        elif len(player.hand) < 3:
            tips.append("手牌不足，注意保存资源")
        
        # 季节提示
        season_info = enhanced_mechanics.get_current_season_info()
        if season_info:
            season_cards = self._get_season_bonus_cards(player.hand, season_info["season"])
            if season_cards:
                tips.append(f"当前{season_info['season']}季，{season_cards[0]}等卡牌有额外效果")
        
        # 连招提示
        if hasattr(player, 'recent_cards') and len(player.recent_cards) >= 1:
            combo_suggestions = self._get_combo_suggestions(player.hand, player.recent_cards)
            if combo_suggestions:
                tips.append(f"可以尝试连招：{combo_suggestions[0]}")
        
        return tips
    
    def _get_season_bonus_cards(self, hand: List[str], season: str) -> List[str]:
        """获取有季节奖励的手牌"""
        bonus_cards = []
        for card in hand:
            qi_mult, dao_mult = get_seasonal_multiplier(card)
            if qi_mult > 1.0 or dao_mult > 1.0:
                bonus_cards.append(card)
        return bonus_cards
    
    def _get_combo_suggestions(self, hand: List[str], recent_cards: List[str]) -> List[str]:
        """获取连招建议"""
        suggestions = []
        if not recent_cards:
            return suggestions
        
        last_card = recent_cards[-1]
        for card in hand:
            combo = get_combo_effect([last_card, card])
            if combo:
                suggestions.append(f"{last_card} + {card} = {combo.name}")
        
        return suggestions
    
    def _handle_human_turn(self, game_state: GameState, player: Player) -> None:
        """处理人类玩家回合"""
        while True:
            # 创建行动菜单
            action_menu = self._create_action_menu(player)
            print(action_menu)
            
            # 获取玩家选择
            choice = self.ui.get_enhanced_input("请选择行动", "text")
            
            # 处理选择
            result = self._process_player_action(game_state, player, choice)
            
            if result.success:
                self._display_action_result(result)
                
                # 检查是否结束回合
                if choice in ["8", "end", "结束回合"]:
                    break
                
                # 检查胜利条件
                if self._check_victory_condition(player):
                    break
            else:
                print(self.ui.create_notification(result.message, MessageType.ERROR))
    
    def _create_action_menu(self, player: Player) -> str:
        """创建行动菜单"""
        options = [
            {
                "name": "出牌",
                "icon": "🃏",
                "description": "选择手牌出牌获得效果",
                "shortcut": "1"
            },
            {
                "name": "移动",
                "icon": "🚶",
                "description": "在天地人三界间移动",
                "shortcut": "2"
            },
            {
                "name": "冥想",
                "icon": "🧘",
                "description": "恢复气并获得诚意",
                "shortcut": "3"
            },
            {
                "name": "研习",
                "icon": "📖",
                "description": "消耗气来获得道行",
                "shortcut": "4"
            },
            {
                "name": "易经学习",
                "icon": "📚",
                "description": "学习易经知识获得智慧",
                "shortcut": "5"
            },
            {
                "name": "查看状态",
                "icon": "📊",
                "description": "查看详细游戏状态",
                "shortcut": "6"
            },
            {
                "name": "帮助",
                "icon": "❓",
                "description": "查看游戏帮助信息",
                "shortcut": "7"
            },
            {
                "name": "结束回合",
                "icon": "⏭️",
                "description": "结束当前回合",
                "shortcut": "8"
            }
        ]
        
        return self.ui.create_enhanced_menu("选择行动", options)
    
    def _process_player_action(self, game_state: GameState, player: Player, choice: str) -> ActionResult:
        """处理玩家行动"""
        choice = choice.strip().lower()
        
        if choice in ["1", "出牌", "play"]:
            return self._handle_play_card_action(game_state, player)
        elif choice in ["2", "移动", "move"]:
            return self._handle_move_action(game_state, player)
        elif choice in ["3", "冥想", "meditate"]:
            return self._handle_meditate_action(game_state, player)
        elif choice in ["4", "研习", "study"]:
            return self._handle_study_action(game_state, player)
        elif choice in ["5", "易经学习", "learn"]:
            return self._handle_learning_action(player)
        elif choice in ["6", "查看状态", "status"]:
            return self._handle_status_action(game_state, player)
        elif choice in ["7", "帮助", "help"]:
            return self._handle_help_action()
        elif choice in ["8", "结束回合", "end"]:
            return ActionResult(True, "回合结束", {}, [], [])
        else:
            return ActionResult(False, "无效的选择，请重新输入", {}, [], [])
    
    def _handle_play_card_action(self, game_state: GameState, player: Player) -> ActionResult:
        """处理出牌行动"""
        if not player.hand:
            return ActionResult(False, "手中没有卡牌！", {}, [], [])
        
        # 显示卡牌选择界面
        self.ui.clear_screen()
        print(self.ui.create_section_header("选择要出的卡牌"))
        
        # 显示详细卡牌信息
        for i, card_name in enumerate(player.hand, 1):
            enhanced_card = get_card_by_name(card_name)
            
            # 基本信息
            print(f"\n{i}. {self.ui.colorize(card_name, self.ui.theme.primary_color + self.ui.theme.bold)}")
            
            if enhanced_card:
                # 卡牌效果
                cost = enhanced_card.cost
                qi_effect = enhanced_card.qi_effect
                dao_effect = enhanced_card.dao_xing_effect
                
                print(f"   消耗: {cost}气")
                print(f"   效果: +{qi_effect}气 +{dao_effect}道行")
                
                # 季节奖励
                qi_mult, dao_mult = get_seasonal_multiplier(card_name)
                if qi_mult > 1.0 or dao_mult > 1.0:
                    bonus_text = f"   🌟 季节奖励: 气效果x{qi_mult:.1f}, 道行效果x{dao_mult:.1f}"
                    print(self.ui.colorize(bonus_text, self.ui.theme.secondary_color))
                
                # 卡牌含义
                if hasattr(enhanced_card, 'chinese_name'):
                    print(f"   📜 {enhanced_card.chinese_name}: {enhanced_card.judgment_meaning[:50]}...")
        
        print(f"\n0. 取消")
        
        # 获取选择
        choice = self.ui.get_enhanced_input("请选择卡牌编号", "text")
        
        try:
            if choice == "0":
                return ActionResult(False, "取消出牌", {}, [], [])
            
            card_index = int(choice) - 1
            if 0 <= card_index < len(player.hand):
                return self._execute_play_card(player, card_index)
            else:
                return ActionResult(False, "无效的卡牌编号", {}, [], [])
        except ValueError:
            return ActionResult(False, "请输入有效的数字", {}, [], [])
    
    def _execute_play_card(self, player: Player, card_index: int) -> ActionResult:
        """执行出牌"""
        card_name = player.hand[card_index]
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
        
        # 检查气是否足够
        if player.qi < cost:
            return ActionResult(False, f"气不足！需要{cost}气，当前只有{player.qi}气", {}, [], [])
        
        # 计算季节奖励
        qi_mult, dao_mult = get_seasonal_multiplier(card_name)
        actual_qi_effect = int(qi_effect * qi_mult)
        actual_dao_effect = int(dao_effect * dao_mult)
        
        # 执行出牌
        player.qi -= cost
        player.qi += actual_qi_effect
        player.dao_xing += actual_dao_effect
        
        played_card = player.hand.pop(card_index)
        
        # 记录出牌历史
        if not hasattr(player, 'recent_cards'):
            player.recent_cards = []
        player.recent_cards.append(played_card)
        if len(player.recent_cards) > 5:
            player.recent_cards.pop(0)
        
        # 创建结果
        effects = {
            "qi_change": actual_qi_effect - cost,
            "dao_xing_change": actual_dao_effect
        }
        
        notifications = [f"出牌: {played_card}"]
        
        # 季节奖励通知
        if qi_mult > 1.0 or dao_mult > 1.0:
            notifications.append(f"季节奖励: 气效果x{qi_mult:.1f}, 道行效果x{dao_mult:.1f}")
        
        # 检查连招
        achievements = []
        if len(player.recent_cards) >= 2:
            combo_effect = get_combo_effect(player.recent_cards[-2:])
            if combo_effect:
                player.qi += combo_effect.qi_bonus
                player.dao_xing += combo_effect.dao_xing_bonus
                
                notifications.append(f"连招成功: {combo_effect.name}!")
                notifications.append(f"连招奖励: +{combo_effect.qi_bonus}气 +{combo_effect.dao_xing_bonus}道行")
                
                if not hasattr(player, 'combos_performed'):
                    player.combos_performed = 0
                player.combos_performed += 1
                
                # 智慧点数奖励
                if combo_effect.wisdom_points > 0:
                    self.education_system.add_wisdom_points(player.name, combo_effect.wisdom_points)
                    notifications.append(f"获得智慧点数: +{combo_effect.wisdom_points}")
        
        # 易经学习
        if enhanced_card:
            from yijing_education_system import YijingKnowledge
            knowledge = YijingKnowledge(
                gua_name=enhanced_card.chinese_name,
                description=enhanced_card.judgment_meaning,
                philosophy=enhanced_card.philosophy,
                wisdom=enhanced_card.life_wisdom
            )
            self.education_system.learn_from_card(player.name, knowledge)
            notifications.append(f"从{enhanced_card.chinese_name}卦中学到了易经智慧")
        
        return ActionResult(True, f"成功出牌: {played_card}", effects, notifications, achievements)
    
    def _handle_move_action(self, game_state: GameState, player: Player) -> ActionResult:
        """处理移动行动"""
        zones = ["天", "地", "人"]
        current_zone = player.zone
        
        print(f"\n当前位置: {current_zone}")
        print("可移动到:")
        for i, zone in enumerate(zones, 1):
            if zone != current_zone:
                print(f"{i}. {zone}")
        print("0. 取消")
        
        choice = self.ui.get_enhanced_input("请选择目标位置", "text")
        
        try:
            if choice == "0":
                return ActionResult(False, "取消移动", {}, [], [])
            
            zone_index = int(choice) - 1
            if 0 <= zone_index < len(zones) and zones[zone_index] != current_zone:
                if player.qi >= 1:
                    player.zone = zones[zone_index]
                    player.qi -= 1
                    return ActionResult(True, f"移动到{zones[zone_index]}", {"qi_change": -1}, [], [])
                else:
                    return ActionResult(False, "气不足，无法移动！", {}, [], [])
            else:
                return ActionResult(False, "无效的移动选择", {}, [], [])
        except ValueError:
            return ActionResult(False, "请输入有效的数字", {}, [], [])
    
    def _handle_meditate_action(self, game_state: GameState, player: Player) -> ActionResult:
        """处理冥想行动"""
        if player.qi < 5:
            player.qi += 2
            player.cheng_yi += 1
            effects = {"qi_change": 2, "cheng_yi_change": 1}
            return ActionResult(True, "冥想成功", effects, ["恢复2点气，获得1点诚意"], [])
        else:
            return ActionResult(False, "气已充足，无需冥想！", {}, [], [])
    
    def _handle_study_action(self, game_state: GameState, player: Player) -> ActionResult:
        """处理研习行动"""
        if player.qi >= 2:
            player.qi -= 2
            player.dao_xing += 2
            effects = {"qi_change": -2, "dao_xing_change": 2}
            
            # 获得易经智慧
            notifications = ["消耗2点气，获得2点道行"]
            knowledge = self.education_system.get_random_wisdom()
            if knowledge:
                notifications.append(f"易经启发：{knowledge.practical_wisdom}")
            
            return ActionResult(True, "研习成功", effects, notifications, [])
        else:
            return ActionResult(False, "气不足，无法研习！", {}, [], [])
    
    def _handle_learning_action(self, player: Player) -> ActionResult:
        """处理易经学习行动"""
        self.ui.clear_screen()
        print(self.ui.create_section_header("易经学习"))
        
        # 显示每日智慧
        daily_wisdom = self.education_system.get_daily_wisdom()
        print(f"\n📜 今日智慧：{daily_wisdom}")
        
        # 学习选项
        learning_options = [
            {"name": "随机易经知识", "icon": "🎲", "description": "学习随机的易经智慧"},
            {"name": "解释手牌含义", "icon": "🃏", "description": "了解手牌的易经含义"},
            {"name": "易经小测验", "icon": "❓", "description": "通过测验获得奖励"},
            {"name": "返回", "icon": "↩️", "description": "返回主菜单"}
        ]
        
        menu = self.ui.create_enhanced_menu("学习选项", learning_options)
        print(menu)
        
        choice = self.ui.get_enhanced_input("请选择学习内容", "text")
        
        if choice in ["1", "随机"]:
            knowledge = self.education_system.get_random_wisdom()
            print(f"\n【{knowledge.title}】")
            print(f"{knowledge.content}")
            print(f"\n💡 实用智慧：{knowledge.practical_wisdom}")
            input("\n按回车继续...")
            
        elif choice in ["2", "手牌"]:
            if player.hand:
                self._explain_hand_cards(player)
            else:
                print("你没有手牌可以解释")
                
        elif choice in ["3", "测验"]:
            self._conduct_quiz(player)
            
        elif choice in ["4", "返回"]:
            pass
        
        return ActionResult(True, "学习完成", {}, [], [])
    
    def _explain_hand_cards(self, player: Player) -> None:
        """解释手牌含义"""
        print("\n请选择要解释的卡牌：")
        for i, card in enumerate(player.hand, 1):
            print(f"{i}. {card}")
        
        choice = self.ui.get_enhanced_input("请选择卡牌编号", "text")
        
        try:
            card_index = int(choice) - 1
            if 0 <= card_index < len(player.hand):
                card = player.hand[card_index]
                explanation = self.education_system.explain_card_meaning(card)
                print(f"\n{explanation}")
                input("\n按回车继续...")
            else:
                print("无效的卡牌编号")
        except ValueError:
            print("请输入有效的数字")
    
    def _conduct_quiz(self, player: Player) -> None:
        """进行易经测验"""
        quiz = self.education_system.create_learning_quiz(player.name)
        print(f"\n❓ {quiz['question']}")
        
        for i, option in enumerate(quiz['options'], 1):
            print(f"{i}. {option}")
        
        choice = self.ui.get_enhanced_input("请选择答案", "text")
        
        try:
            answer = int(choice) - 1
            if answer == quiz['correct']:
                print(self.ui.create_notification("回答正确！", MessageType.SUCCESS))
                player.cheng_yi += 1
                print(f"获得1点诚意奖励！当前诚意：{player.cheng_yi}")
            else:
                print(self.ui.create_notification("回答错误", MessageType.ERROR))
            
            print(f"\n📖 解释：{quiz['explanation']}")
            input("\n按回车继续...")
        except ValueError:
            print("请输入有效的数字")
    
    def _handle_status_action(self, game_state: GameState, player: Player) -> ActionResult:
        """处理查看状态行动"""
        self.ui.clear_screen()
        
        # 显示详细状态
        season_info = enhanced_mechanics.get_current_season_info()
        self.ui.display_game_screen(game_state, player, season_info, show_help=True)
        
        # 显示学习进度
        progress = self.education_system.get_player_progress(player.name)
        if progress:
            print(self.ui.create_section_header("学习进度"))
            print(f"🎓 当前等级：{progress.current_level.value}")
            print(f"🌟 智慧点数：{progress.wisdom_points}")
            print(f"📚 已掌握概念：{len(progress.mastered_concepts)}")
        
        input("\n按回车继续...")
        return ActionResult(True, "状态查看完成", {}, [], [])
    
    def _handle_help_action(self) -> ActionResult:
        """处理帮助行动"""
        self.ui.clear_screen()
        print(self.ui.create_help_panel("main"))
        print()
        print(self.ui.create_help_panel("cards"))
        input("\n按回车继续...")
        return ActionResult(True, "帮助查看完成", {}, [], [])
    
    def _display_action_result(self, result: ActionResult) -> None:
        """显示行动结果"""
        if result.success:
            print(self.ui.create_notification(result.message, MessageType.SUCCESS))
        
        # 显示效果
        if result.effects:
            effect_parts = []
            for effect, value in result.effects.items():
                if value != 0:
                    sign = "+" if value > 0 else ""
                    effect_parts.append(f"{sign}{value} {effect.replace('_change', '')}")
            
            if effect_parts:
                print(self.ui.colorize(f"效果: {', '.join(effect_parts)}", self.ui.theme.secondary_color))
        
        # 显示通知
        for notification in result.notifications:
            print(self.ui.colorize(f"📢 {notification}", self.ui.theme.text_color))
        
        # 显示成就
        for achievement in result.achievements:
            print(self.ui.create_notification(f"🏆 获得成就: {achievement}", MessageType.ACHIEVEMENT))
        
        if result.notifications or result.achievements:
            time.sleep(1.5)  # 让玩家有时间阅读
    
    def _handle_ai_turn(self, game_state: GameState, player: Player) -> None:
        """处理AI回合"""
        print(self.ui.create_notification(f"🤖 {player.name} 正在思考...", MessageType.INFO))
        self.ui.show_loading_animation("AI思考中", 1.5)
        
        # 简化的AI逻辑
        if player.hand and player.qi >= 1:
            # AI优先出牌
            card_index = random.randint(0, len(player.hand) - 1)
            result = self._execute_play_card(player, card_index)
            print(self.ui.create_notification(f"🤖 {player.name} {result.message}", MessageType.INFO))
        elif player.qi < 3:
            # 气不足时冥想
            result = self._handle_meditate_action(game_state, player)
            print(self.ui.create_notification(f"🤖 {player.name} {result.message}", MessageType.INFO))
        else:
            print(self.ui.create_notification(f"🤖 {player.name} 结束回合", MessageType.INFO))
        
        time.sleep(1)
    
    def _is_ai_player(self, player: Player) -> bool:
        """检查是否为AI玩家"""
        return player.name.startswith("AI-")
    
    def _should_end_turn(self, game_state: GameState, player: Player) -> bool:
        """检查是否应该结束回合"""
        # 检查胜利条件
        return self._check_victory_condition(player)
    
    def _check_victory_condition(self, player: Player) -> bool:
        """检查胜利条件"""
        victory_threshold = self.config_manager.get("victory_conditions.base_dao_xing", 10)
        return player.dao_xing >= victory_threshold
    
    def _end_turn(self, game_state: GameState) -> None:
        """结束回合"""
        self.current_phase = GamePhase.END_TURN
        
        # 推进到下一个玩家
        game_state.advance_turn()
        
        # 每5轮推进季节
        if game_state.turn % 5 == 1 and game_state.turn > 1:
            enhanced_mechanics.advance_season()
            season_info = enhanced_mechanics.get_current_season_info()
            print(self.ui.create_notification(
                f"🌸 季节变化！现在是{season_info['season']}季", 
                MessageType.INFO
            ))
            time.sleep(1)
        
        self.current_phase = GamePhase.PLAYING
    
    def _check_game_end_conditions(self, game_state: GameState) -> bool:
        """检查游戏结束条件"""
        # 检查胜利条件
        for player in game_state.players:
            if self._check_victory_condition(player):
                return True
        
        # 检查最大回合数
        max_turns = self.config_manager.get("game_settings.max_turns", 100)
        return game_state.turn >= max_turns
    
    def _handle_game_end(self, game_state: GameState) -> None:
        """处理游戏结束"""
        self.current_phase = GamePhase.GAME_OVER
        self.ui.clear_screen()
        
        # 找到获胜者
        winner = None
        for player in game_state.players:
            if self._check_victory_condition(player):
                winner = player
                break
        
        if winner:
            # 显示胜利界面
            victory_banner = self.ui.create_title_banner("游戏结束", f"🎉 {winner.name} 获得胜利！")
            print(victory_banner)
            
            # 显示胜利者信息
            print(self.ui.create_section_header("胜利者"))
            print(self.ui.create_player_dashboard(winner, True))
            
            # 显示学习成果
            progress = self.education_system.get_player_progress(winner.name)
            if progress:
                print(f"\n📚 易经学习等级：{progress.current_level.value}")
                print(f"🌟 智慧点数：{progress.wisdom_points}")
        else:
            # 平局
            print(self.ui.create_title_banner("游戏结束", "⏰ 达到最大回合数，平局！"))
        
        # 显示最终排名
        print(self.ui.create_section_header("最终排名"))
        sorted_players = sorted(game_state.players, key=lambda p: p.dao_xing, reverse=True)
        
        for i, player in enumerate(sorted_players, 1):
            progress = self.education_system.get_player_progress(player.name)
            wisdom_info = f" (智慧等级: {progress.current_level.value})" if progress else ""
            ranking_line = f"{i}. {player.name}: {player.dao_xing} 道行{wisdom_info}"
            print(self.ui.colorize(ranking_line, self.ui.theme.text_color))
        
        print(self.ui.create_notification("感谢游玩天机变！愿易经智慧伴随您的人生之路！", MessageType.SUCCESS))

# 全局游戏流程实例
interactive_flow = InteractiveGameFlow()