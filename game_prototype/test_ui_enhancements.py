#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI增强系统测试脚本
测试新的用户界面和交互体验功能
"""

import sys
import time
from game_state import GameState, Player
from enhanced_ui_experience import EnhancedUIExperience, MessageType
from interactive_game_flow import InteractiveGameFlow

def test_ui_components():
    """测试UI组件"""
    print("🧪 测试UI增强系统...")
    
    ui = EnhancedUIExperience()
    
    # 测试标题横幅
    print("\n1. 测试标题横幅:")
    print(ui.create_title_banner("天机变", "易经策略游戏"))
    
    # 测试菜单
    print("\n2. 测试增强菜单:")
    menu_options = [
        {"key": "1", "text": "开始游戏", "description": "开始新的游戏"},
        {"key": "2", "text": "加载游戏", "description": "加载已保存的游戏"},
        {"key": "3", "text": "设置", "description": "游戏设置"},
        {"key": "0", "text": "退出", "description": "退出游戏"}
    ]
    print(ui.create_enhanced_menu("主菜单", menu_options))
    
    # 测试通知
    print("\n3. 测试通知系统:")
    print(ui.create_notification("这是一条信息", MessageType.INFO))
    print(ui.create_notification("操作成功！", MessageType.SUCCESS))
    print(ui.create_notification("注意警告", MessageType.WARNING))
    print(ui.create_notification("发生错误", MessageType.ERROR))
    
    # 测试进度条
    print("\n4. 测试进度条:")
    for i in range(0, 101, 20):
        progress_bar = ui.create_progress_bar(i, 100, 30, ui.theme.success_color)
        print(f"进度: {progress_bar} {i}%")
    
    # 测试玩家仪表板
    print("\n5. 测试玩家仪表板:")
    from game_state import Avatar, AvatarName
    test_avatar = Avatar(AvatarName.HERMIT, "隐士", "智慧能力")
    test_player = Player("测试玩家", test_avatar)
    test_player.qi = 5
    test_player.dao_xing = 3
    test_player.hand = ["乾卦", "坤卦", "震卦"]
    test_player.position = (2, 3)
    
    dashboard = ui.create_player_dashboard(test_player, is_current=True)
    print(dashboard)
    
    print("\n✅ UI组件测试完成！")

def test_interactive_flow():
    """测试交互式流程"""
    print("\n🎮 测试交互式游戏流程...")
    
    # 创建测试游戏状态
    from game_state import Avatar, AvatarName
    avatar1 = Avatar(AvatarName.EMPEROR, "帝王", "统治能力")
    avatar2 = Avatar(AvatarName.HERMIT, "隐士", "智慧能力")
    player1 = Player("测试玩家1", avatar1)
    player2 = Player("AI玩家", avatar2)
    
    game_state = GameState([player1, player2])
    
    player1.qi = 5
    player1.dao_xing = 2
    player1.hand = ["乾卦", "坤卦", "震卦"]
    
    player2.qi = 4
    player2.dao_xing = 1
    player2.hand = ["巽卦", "坎卦"]
    
    game_state.players = [player1, player2]
    game_state.current_player_index = 0
    game_state.turn = 5
    game_state.season = "春"
    
    # 测试游戏界面显示
    ui = EnhancedUIExperience()
    season_info = {
        "name": "春",
        "description": "万物复苏的季节",
        "bonus": "木属性卡牌效果+1"
    }
    
    print("\n6. 测试游戏界面显示:")
    ui.display_game_screen(game_state, player1, season_info, show_help=False)
    
    print("\n✅ 交互式流程测试完成！")

def test_animations():
    """测试动画效果"""
    print("\n🎬 测试动画效果...")
    
    ui = EnhancedUIExperience()
    
    # 测试文本动画
    print("\n7. 测试文本动画:")
    ui.animate_text("欢迎来到天机变游戏！", 0.05)
    
    # 测试加载动画
    print("\n8. 测试加载动画:")
    ui.show_loading_animation("初始化游戏", 3.0)
    
    # 测试成就弹窗
    print("\n9. 测试成就弹窗:")
    achievement_popup = ui.create_achievement_popup(
        "初学者", 
        "完成第一次游戏", 
        {"道行": 1, "经验": 10}
    )
    print(achievement_popup)
    
    print("\n✅ 动画效果测试完成！")

def test_input_system():
    """测试输入系统"""
    print("\n⌨️ 测试输入系统...")
    
    ui = EnhancedUIExperience()
    
    print("\n10. 测试增强输入:")
    
    # 测试选择输入
    print("请选择一个选项:")
    choice = ui.get_enhanced_input(
        "选择 (a/b/c)", 
        "choice", 
        ["a", "b", "c"]
    )
    print(f"您选择了: {choice}")
    
    # 测试文本输入
    name = ui.get_enhanced_input("请输入您的名字", "text")
    print(f"您的名字是: {name}")
    
    print("\n✅ 输入系统测试完成！")

def main():
    """主测试函数"""
    print("🚀 开始UI增强系统测试")
    print("=" * 50)
    
    try:
        # 运行各项测试
        test_ui_components()
        test_interactive_flow()
        test_animations()
        
        # 询问是否测试输入系统（需要用户交互）
        print("\n是否测试输入系统？(需要用户交互)")
        response = input("输入 'y' 进行测试，其他键跳过: ").strip().lower()
        
        if response == 'y':
            test_input_system()
        else:
            print("跳过输入系统测试")
        
        print("\n🎉 所有测试完成！")
        print("UI增强系统运行正常")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()