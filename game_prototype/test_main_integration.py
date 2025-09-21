#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试主游戏UI集成
"""

import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_ui_experience import EnhancedUIExperience, MessageType
from interactive_game_flow import InteractiveGameFlow
from game_state import GameState, Player, Avatar, AvatarName
from config_manager import ConfigManager

def test_main_integration():
    """测试主游戏UI集成"""
    print("🧪 测试主游戏UI集成...")
    
    try:
        # 初始化系统
        config_manager = ConfigManager()
        enhanced_ui = EnhancedUIExperience()
        interactive_flow = InteractiveGameFlow()
        
        print("✅ 系统初始化成功")
        
        # 测试UI显示
        enhanced_ui.clear_screen()
        enhanced_ui.create_title_banner("天机变 - 易经策略游戏", "体验易经智慧的策略游戏")
        
        # 创建测试玩家
        avatar1 = Avatar(AvatarName.EMPEROR, "帝王", "统治能力")
        avatar2 = Avatar(AvatarName.HERMIT, "隐士", "智慧能力")
        player1 = Player("测试玩家", avatar1)
        player2 = Player("AI玩家", avatar2)
        
        # 设置一些测试数据
        player1.qi = 8
        player1.dao_xing = 3
        player1.cheng_yi = 2
        
        # 创建游戏状态
        game_state = GameState([player1, player2])
        
        # 测试游戏界面显示
        enhanced_ui.display_game_screen(
            game_state=game_state,
            player=player1,
            season_info={"name": "春季", "icon": "🌸", "description": "万物复苏的季节"}
        )
        
        print("\n✅ UI集成测试成功！")
        print("🎉 增强的用户界面系统已成功集成到主游戏中")
        
        # 显示功能特性
        notification = enhanced_ui.create_notification("UI增强功能已激活", MessageType.SUCCESS)
        print(notification)
        
        features = [
            "🎨 美观的界面设计",
            "🌈 彩色文本显示", 
            "📊 可视化进度条",
            "🎭 动画效果",
            "⌨️ 增强输入体验",
            "🎮 交互式游戏流程"
        ]
        
        print("\n🌟 新增功能特性:")
        for feature in features:
            print(f"  {feature}")
            
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_main_integration()