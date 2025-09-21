#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强用户界面和交互体验系统
提供更直观、美观和用户友好的游戏界面
"""

import os
import sys
import time
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from game_state import Player, GameState
from config_manager import ConfigManager

class UIStyle(Enum):
    """界面风格"""
    MINIMAL = "简约"
    CLASSIC = "经典"
    MODERN = "现代"
    ELEGANT = "雅致"

class MessageType(Enum):
    """消息类型"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    ACHIEVEMENT = "achievement"
    WISDOM = "wisdom"

@dataclass
class UITheme:
    """UI主题配置"""
    primary_color: str = "\033[36m"      # 青色
    secondary_color: str = "\033[33m"    # 黄色
    success_color: str = "\033[32m"      # 绿色
    warning_color: str = "\033[93m"      # 亮黄色
    error_color: str = "\033[31m"        # 红色
    accent_color: str = "\033[35m"       # 紫色
    text_color: str = "\033[37m"         # 白色
    dim_color: str = "\033[90m"          # 暗色
    reset: str = "\033[0m"               # 重置
    bold: str = "\033[1m"                # 粗体

class EnhancedUIExperience:
    """增强用户界面体验类"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.theme = UITheme()
        self.style = UIStyle.ELEGANT
        self.use_colors = True
        self.use_animations = True
        self.screen_width = 80
        self.last_notification_time = 0
        self._load_ui_preferences()
    
    def _load_ui_preferences(self):
        """加载UI偏好设置"""
        try:
            ui_prefs = self.config_manager.get("ui_preferences", {})
            self.use_colors = ui_prefs.get("use_colors", True)
            self.use_animations = ui_prefs.get("use_animations", True)
            self.screen_width = ui_prefs.get("screen_width", 80)
            
            # 检测终端支持
            if os.name == 'nt':  # Windows
                try:
                    os.system('color')  # 启用颜色支持
                except:
                    self.use_colors = False
        except:
            pass  # 使用默认设置
    
    def colorize(self, text: str, color: str = "") -> str:
        """为文本添加颜色"""
        if not self.use_colors or not color:
            return text
        return f"{color}{text}{self.theme.reset}"
    
    def clear_screen(self):
        """清屏"""
        if self.use_animations:
            os.system('cls' if os.name == 'nt' else 'clear')
    
    def create_border(self, char: str = "═", width: Optional[int] = None) -> str:
        """创建装饰边框"""
        if width is None:
            width = self.screen_width
        return char * width
    
    def create_title_banner(self, title: str, subtitle: str = "") -> str:
        """创建标题横幅"""
        lines = []
        
        # 顶部边框
        lines.append(self.colorize(self.create_border("═"), self.theme.primary_color))
        
        # 主标题
        title_line = f"✦ {title} ✦"
        lines.append(self.colorize(title_line.center(self.screen_width), 
                                 self.theme.primary_color + self.theme.bold))
        
        # 副标题
        if subtitle:
            lines.append(self.colorize(subtitle.center(self.screen_width), 
                                     self.theme.secondary_color))
        
        # 底部边框
        lines.append(self.colorize(self.create_border("═"), self.theme.primary_color))
        
        return "\n".join(lines)
    
    def create_section_header(self, title: str, icon: str = "◆") -> str:
        """创建章节标题"""
        header = f"{icon} {title}"
        return self.colorize(header, self.theme.accent_color + self.theme.bold)
    
    def create_enhanced_menu(self, title: str, options: List[Dict[str, str]], 
                           show_shortcuts: bool = True) -> str:
        """创建增强菜单"""
        lines = []
        
        # 菜单标题
        lines.append(self.create_section_header(title, "🎯"))
        lines.append(self.colorize("─" * (len(title) + 5), self.theme.dim_color))
        lines.append("")
        
        # 菜单选项
        for i, option in enumerate(options, 1):
            # 选项编号和图标
            number = self.colorize(f"[{i}]", self.theme.primary_color + self.theme.bold)
            icon = option.get("icon", "▶")
            name = option.get("name", f"选项{i}")
            desc = option.get("description", "")
            shortcut = option.get("shortcut", "")
            
            # 主选项行
            option_line = f"{number} {icon} {name}"
            if shortcut and show_shortcuts:
                option_line += self.colorize(f" ({shortcut})", self.theme.dim_color)
            
            lines.append(self.colorize(option_line, self.theme.text_color))
            
            # 描述行
            if desc:
                desc_line = f"    {desc}"
                lines.append(self.colorize(desc_line, self.theme.dim_color))
            
            lines.append("")  # 空行分隔
        
        return "\n".join(lines)
    
    def create_player_dashboard(self, player: Player, is_current: bool = False) -> str:
        """创建玩家仪表板"""
        lines = []
        
        # 玩家标识
        if is_current:
            status_icon = "👑"
            name_color = self.theme.primary_color + self.theme.bold
        else:
            status_icon = "  "
            name_color = self.theme.text_color
        
        # 玩家名称和头像
        avatar_icon = "🏛️" if player.avatar.name.value == "EMPEROR" else "🧙"
        name_line = f"{status_icon} {avatar_icon} {player.name}"
        lines.append(self.colorize(name_line, name_color))
        
        # 资源状态条
        resources = [
            ("⚡", "气", player.qi, 10, self.theme.primary_color),
            ("🌟", "道行", player.dao_xing, 20, self.theme.secondary_color),
            ("💫", "诚意", player.cheng_yi, 10, self.theme.accent_color)
        ]
        
        for icon, name, current, max_val, color in resources:
            bar = self.create_progress_bar(current, max_val, 15, color)
            resource_line = f"  {icon} {name}: {bar} {current}"
            lines.append(resource_line)
        
        # 手牌信息
        hand_icon = "🃏"
        hand_line = f"  {hand_icon} 手牌: {len(player.hand)} 张"
        lines.append(self.colorize(hand_line, self.theme.text_color))
        
        # 位置信息
        zone_icons = {"天": "☁️", "地": "🌍", "人": "👥"}
        position_name = getattr(player.position, 'value', str(player.position))
        zone_icon = zone_icons.get(position_name, "📍")
        zone_line = f"  {zone_icon} 位置: {position_name}"
        lines.append(self.colorize(zone_line, self.theme.text_color))
        
        return "\n".join(lines)
    
    def create_progress_bar(self, current: int, maximum: int, width: int = 20, 
                          color: str = "") -> str:
        """创建进度条"""
        if maximum == 0:
            percentage = 0
        else:
            percentage = min(current / maximum, 1.0)
        
        filled = int(width * percentage)
        empty = width - filled
        
        # 使用Unicode字符创建更美观的进度条
        fill_char = "█"
        empty_char = "░"
        
        bar = fill_char * filled + empty_char * empty
        
        if color:
            bar = self.colorize(bar, color)
        
        return f"[{bar}]"
    
    def create_notification(self, message: str, msg_type: MessageType = MessageType.INFO, 
                          auto_dismiss: bool = True) -> str:
        """创建通知消息"""
        # 图标和颜色映射
        type_config = {
            MessageType.INFO: ("ℹ️", self.theme.primary_color),
            MessageType.SUCCESS: ("✅", self.theme.success_color),
            MessageType.WARNING: ("⚠️", self.theme.warning_color),
            MessageType.ERROR: ("❌", self.theme.error_color),
            MessageType.ACHIEVEMENT: ("🏆", self.theme.accent_color),
            MessageType.WISDOM: ("📚", self.theme.secondary_color)
        }
        
        icon, color = type_config.get(msg_type, ("ℹ️", self.theme.text_color))
        
        # 创建通知框
        notification = f"{icon} {message}"
        
        if auto_dismiss:
            self.last_notification_time = time.time()
        
        return self.colorize(notification, color + self.theme.bold)
    
    def create_card_display(self, cards: List[str], enhanced_cards: Dict[str, Any], 
                          show_effects: bool = True) -> str:
        """创建卡牌显示"""
        lines = []
        
        if not cards:
            return self.colorize("手中没有卡牌", self.theme.dim_color)
        
        lines.append(self.create_section_header("手牌", "🃏"))
        lines.append("")
        
        for i, card_name in enumerate(cards, 1):
            # 卡牌基本信息
            card_line = f"[{i}] {card_name}"
            
            # 增强卡牌效果
            if show_effects and card_name in enhanced_cards:
                card_data = enhanced_cards[card_name]
                cost = card_data.get("cost", 1)
                qi_effect = card_data.get("qi_effect", 0)
                dao_effect = card_data.get("dao_xing_effect", 1)
                
                effect_text = f" (消耗:{cost}气, +{qi_effect}气 +{dao_effect}道行)"
                card_line += self.colorize(effect_text, self.theme.dim_color)
            
            lines.append(self.colorize(card_line, self.theme.text_color))
        
        return "\n".join(lines)
    
    def create_game_status_panel(self, game_state: GameState, season_info: Dict[str, Any]) -> str:
        """创建游戏状态面板"""
        lines = []
        
        # 回合信息
        turn_info = f"第 {game_state.turn} 轮"
        lines.append(self.colorize(turn_info, self.theme.primary_color + self.theme.bold))
        
        # 季节信息
        if season_info:
            season_icons = {"春": "🌸", "夏": "☀️", "秋": "🍂", "冬": "❄️"}
            season = season_info.get("season", "春")
            icon = season_icons.get(season, "🌸")
            effect = season_info.get("special_effect", "")
            
            season_line = f"{icon} {season}季 - {effect}"
            lines.append(self.colorize(season_line, self.theme.secondary_color))
        
        # 当前玩家
        current_player = game_state.get_current_player()
        current_line = f"👑 当前玩家: {current_player.name}"
        lines.append(self.colorize(current_line, self.theme.accent_color))
        
        return "\n".join(lines)
    
    def create_help_panel(self, context: str = "main") -> str:
        """创建帮助面板"""
        lines = []
        
        lines.append(self.create_section_header("帮助信息", "❓"))
        lines.append("")
        
        if context == "main":
            help_items = [
                ("出牌", "消耗气来获得道行和特殊效果"),
                ("移动", "在天地人三界间移动，消耗1气"),
                ("冥想", "恢复气并获得诚意"),
                ("研习", "消耗气来获得道行"),
                ("易经学习", "学习易经知识，获得智慧点数")
            ]
        elif context == "cards":
            help_items = [
                ("卡牌效果", "每张卡牌都有独特的气消耗和效果"),
                ("季节奖励", "某些卡牌在特定季节有额外效果"),
                ("连招系统", "连续出相关卡牌可获得奖励"),
                ("卡牌学习", "从卡牌中学习易经智慧")
            ]
        else:
            help_items = [("通用帮助", "输入数字选择对应选项")]
        
        for title, desc in help_items:
            help_line = f"• {title}: {desc}"
            lines.append(self.colorize(help_line, self.theme.text_color))
        
        return "\n".join(lines)
    
    def animate_text(self, text: str, delay: float = 0.03) -> None:
        """文本动画效果"""
        if not self.use_animations:
            print(text)
            return
        
        for char in text:
            print(char, end='', flush=True)
            if char != ' ':
                time.sleep(delay)
        print()
    
    def show_loading_animation(self, message: str = "加载中", duration: float = 2.0) -> None:
        """显示加载动画"""
        if not self.use_animations:
            print(f"{message}...")
            time.sleep(duration)
            return
        
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        end_time = time.time() + duration
        
        while time.time() < end_time:
            for frame in frames:
                if time.time() >= end_time:
                    break
                print(f"\r{frame} {message}...", end='', flush=True)
                time.sleep(0.1)
        
        print(f"\r✅ {message}完成!    ")
    
    def create_achievement_popup(self, achievement_name: str, description: str, 
                               rewards: Dict[str, int]) -> str:
        """创建成就弹窗"""
        lines = []
        
        # 成就标题
        lines.append(self.colorize("🎉 恭喜获得成就! 🎉", self.theme.accent_color + self.theme.bold))
        lines.append(self.create_border("─", 40))
        
        # 成就名称
        lines.append(self.colorize(f"🏆 {achievement_name}", self.theme.secondary_color + self.theme.bold))
        
        # 成就描述
        lines.append(self.colorize(f"📜 {description}", self.theme.text_color))
        
        # 奖励信息
        if rewards:
            reward_parts = []
            reward_icons = {"qi": "⚡", "dao_xing": "🌟", "cheng_yi": "💫", "wisdom": "🧠"}
            
            for resource, amount in rewards.items():
                if amount > 0:
                    icon = reward_icons.get(resource, "🎁")
                    reward_parts.append(f"+{amount}{icon}")
            
            if reward_parts:
                reward_line = f"🎁 奖励: {' '.join(reward_parts)}"
                lines.append(self.colorize(reward_line, self.theme.success_color))
        
        lines.append(self.create_border("─", 40))
        
        return "\n".join(lines)
    
    def get_enhanced_input(self, prompt: str, input_type: str = "text", 
                         valid_options: Optional[List[str]] = None) -> str:
        """增强输入获取"""
        # 美化提示符
        styled_prompt = self.colorize(f"▶ {prompt}", self.theme.primary_color)
        
        while True:
            try:
                user_input = input(f"{styled_prompt} ").strip()
                
                if input_type == "number":
                    return str(int(user_input))
                elif input_type == "choice" and valid_options:
                    if user_input.lower() in [opt.lower() for opt in valid_options]:
                        return user_input
                    else:
                        error_msg = f"请选择: {', '.join(valid_options)}"
                        print(self.create_notification(error_msg, MessageType.ERROR))
                        continue
                else:
                    return user_input
                    
            except ValueError:
                error_msg = "请输入有效的数字"
                print(self.create_notification(error_msg, MessageType.ERROR))
            except KeyboardInterrupt:
                print(self.create_notification("游戏已取消", MessageType.INFO))
                sys.exit(0)
    
    def display_game_screen(self, game_state: GameState, player: Player, 
                          season_info: Dict[str, Any], show_help: bool = False) -> None:
        """显示完整游戏界面"""
        self.clear_screen()
        
        # 游戏标题
        print(self.create_title_banner("天机变 - 易经策略游戏", "在游戏中体验易经智慧"))
        print()
        
        # 游戏状态面板
        print(self.create_game_status_panel(game_state, season_info))
        print()
        
        # 玩家状态
        print(self.create_section_header("玩家状态"))
        for p in game_state.players:
            is_current = (p == player)
            print(self.create_player_dashboard(p, is_current))
            print()
        
        # 帮助信息
        if show_help:
            print(self.create_help_panel())
            print()

# 全局UI实例
ui_experience = EnhancedUIExperience()