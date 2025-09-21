#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天机变 - 增强版游戏演示
展示新的UI增强功能和交互体验
"""

import sys
import os
import time

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_ui_experience import EnhancedUIExperience, MessageType
from interactive_game_flow import InteractiveGameFlow
from game_state import GameState, Player, Avatar, AvatarName
from config_manager import ConfigManager
from card_base import GuaCard
from enhanced_game_mechanics import enhanced_mechanics

def create_demo_game():
    """创建演示游戏"""
    # 初始化系统
    enhanced_ui = EnhancedUIExperience()
    config_manager = ConfigManager()
    
    # 创建玩家
    avatar1 = Avatar(AvatarName.EMPEROR, "帝王", "统治天下的能力")
    avatar2 = Avatar(AvatarName.HERMIT, "隐士", "深藏不露的智慧")
    
    player1 = Player("玩家", avatar1)
    player2 = Player("AI对手", avatar2)
    
    # 设置游戏数据
    player1.qi = 10
    player1.dao_xing = 5
    player1.cheng_yi = 3
    
    player2.qi = 8
    player2.dao_xing = 4
    player2.cheng_yi = 2
    
    # 创建游戏状态
    game_state = GameState([player1, player2])
    game_state.turn = 3
    
    return enhanced_ui, game_state, player1, player2

def demo_ui_features():
    """演示UI功能"""
    enhanced_ui, game_state, player1, player2 = create_demo_game()
    
    # 清屏并显示标题
    enhanced_ui.clear_screen()
    enhanced_ui.create_title_banner("天机变 - 易经策略游戏", "体验全新的增强用户界面")
    
    print("\n🎨 UI增强功能演示")
    print("=" * 60)
    
    # 1. 通知系统演示
    print("\n1️⃣ 通知系统:")
    notifications = [
        ("欢迎来到天机变游戏！", MessageType.INFO),
        ("游戏开始，祝您好运！", MessageType.SUCCESS),
        ("注意：气值不足时无法出牌", MessageType.WARNING),
        ("连接服务器失败", MessageType.ERROR),
        ("获得成就：初学者", MessageType.ACHIEVEMENT),
        ("易经智慧：天行健，君子以自强不息", MessageType.WISDOM)
    ]
    
    for message, msg_type in notifications:
        notification = enhanced_ui.create_notification(message, msg_type)
        print(notification)
        time.sleep(0.5)
    
    # 2. 进度条演示
    print("\n2️⃣ 进度条系统:")
    resources = [
        ("气", 10, 15, enhanced_ui.theme.primary_color),
        ("道行", 5, 10, enhanced_ui.theme.success_color),
        ("诚意", 3, 8, enhanced_ui.theme.accent_color)
    ]
    
    for name, current, maximum, color in resources:
        progress_bar = enhanced_ui.create_progress_bar(current, maximum, 20, color)
        print(f"{name}: {progress_bar} {current}/{maximum}")
    
    # 3. 菜单系统演示
    print("\n3️⃣ 增强菜单系统:")
    menu_options = [
        {"key": "1", "text": "开始新游戏", "description": "创建一个新的游戏会话"},
        {"key": "2", "text": "加载游戏", "description": "从保存的文件加载游戏"},
        {"key": "3", "text": "游戏设置", "description": "调整游戏配置和偏好"},
        {"key": "4", "text": "易经学习", "description": "学习易经知识和智慧"},
        {"key": "5", "text": "退出游戏", "description": "退出到桌面"}
    ]
    
    menu_display = enhanced_ui.create_enhanced_menu("主菜单", menu_options)
    print(menu_display)
    
    # 4. 玩家仪表板演示
    print("\n4️⃣ 玩家仪表板:")
    dashboard1 = enhanced_ui.create_player_dashboard(player1, is_current=True)
    dashboard2 = enhanced_ui.create_player_dashboard(player2, is_current=False)
    print(dashboard1)
    print(dashboard2)
    
    # 5. 游戏状态面板演示
    print("\n5️⃣ 游戏状态面板:")
    season_info = {
        "name": "春季",
        "icon": "🌸", 
        "description": "万物复苏，生机盎然",
        "effects": ["木属性卡牌效果+1", "恢复类行动效果+1"]
    }
    
    status_panel = enhanced_ui.create_game_status_panel(game_state, season_info)
    print(status_panel)
    
    return enhanced_ui, game_state, player1

def demo_interactive_features():
    """演示交互功能"""
    enhanced_ui, game_state, player1 = demo_ui_features()
    
    print("\n🎮 交互功能演示")
    print("=" * 60)
    
    # 6. 文本动画演示
    print("\n6️⃣ 文本动画效果:")
    enhanced_ui.animate_text("欢迎来到天机变的世界，在这里您将体验易经的智慧与策略的完美结合！")
    
    # 7. 加载动画演示
    print("\n7️⃣ 加载动画:")
    enhanced_ui.show_loading_animation("初始化游戏系统", 2.0)
    
    # 8. 成就弹窗演示
    print("\n8️⃣ 成就系统:")
    achievement_popup = enhanced_ui.create_achievement_popup(
        "易经学者",
        "学习了10个易经卦象的含义",
        {"经验": 100, "智慧点": 5}
    )
    print(achievement_popup)
    
    # 9. 完整游戏界面演示
    print("\n9️⃣ 完整游戏界面:")
    enhanced_ui.clear_screen()
    season_info = {
        "name": "夏季",
        "icon": "☀️",
        "description": "阳气旺盛，火属性增强"
    }
    
    enhanced_ui.display_game_screen(
        game_state=game_state,
        player=player1,
        season_info=season_info,
        show_help=True
    )

def demo_complete_experience():
    """完整体验演示"""
    print("\n🌟 完整游戏体验演示")
    print("=" * 60)
    
    enhanced_ui = EnhancedUIExperience()
    
    # 显示欢迎界面
    enhanced_ui.clear_screen()
    enhanced_ui.create_title_banner("天机变", "易经策略游戏 - 增强版")
    
    # 显示功能特性
    features = [
        "🎨 美观的界面设计 - 采用现代化的UI设计理念",
        "🌈 丰富的色彩系统 - 支持多种主题和配色方案", 
        "📊 可视化进度显示 - 直观的进度条和状态指示器",
        "🎭 流畅的动画效果 - 文本动画和加载动画",
        "⌨️ 增强的输入体验 - 智能输入验证和提示",
        "🎮 交互式游戏流程 - 引导式的游戏体验",
        "🏆 成就系统 - 激励玩家探索和学习",
        "📚 易经教育功能 - 寓教于乐的学习体验",
        "🎯 智能AI对手 - 具有挑战性的游戏体验",
        "⚙️ 可配置设置 - 个性化的游戏体验"
    ]
    
    print("\n✨ 新增功能特性:")
    for i, feature in enumerate(features, 1):
        print(f"  {i:2d}. {feature}")
        time.sleep(0.3)
    
    print(f"\n{enhanced_ui.colorize('🎉 天机变增强版已准备就绪！', enhanced_ui.theme.success_color)}")
    print(f"{enhanced_ui.colorize('现在您可以享受全新的游戏体验了！', enhanced_ui.theme.primary_color)}")

def main():
    """主演示函数"""
    try:
        print("🚀 启动天机变增强版演示...")
        time.sleep(1)
        
        # 演示UI功能
        demo_interactive_features()
        
        # 等待用户输入
        print(f"\n{'-' * 60}")
        input("按回车键查看完整功能列表...")
        
        # 显示完整体验
        demo_complete_experience()
        
        print(f"\n{'-' * 60}")
        print("🎊 演示完成！感谢您体验天机变增强版！")
        
    except KeyboardInterrupt:
        print("\n\n👋 演示已中断，感谢您的体验！")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()