#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速游戏测试脚本
测试游戏的基本运行流程
"""

import sys
import io
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

def test_game_startup():
    """测试游戏启动流程"""
    print("🎮 开始测试游戏启动流程...")
    
    try:
        # 模拟用户输入
        test_inputs = ['2', '测试玩家1', '1', '3']  # 2人游戏，玩家名，选择行动等
        
        with patch('builtins.input', side_effect=test_inputs):
            # 重定向输出以捕获游戏输出
            output_buffer = io.StringIO()
            
            try:
                with redirect_stdout(output_buffer):
                    # 导入并运行游戏主函数
                    from main import main
                    main()
            except (EOFError, KeyboardInterrupt, SystemExit):
                # 这些异常是正常的，因为我们模拟了有限的输入
                pass
            except Exception as e:
                print(f"❌ 游戏运行出现异常: {e}")
                return False
        
        # 检查输出
        output = output_buffer.getvalue()
        
        # 检查关键输出内容
        success_indicators = [
            "天机变",
            "易经策略游戏",
            "请输入玩家总数",
            "游戏开始"
        ]
        
        found_indicators = []
        for indicator in success_indicators:
            if indicator in output:
                found_indicators.append(indicator)
        
        print(f"✅ 找到 {len(found_indicators)}/{len(success_indicators)} 个成功指标")
        for indicator in found_indicators:
            print(f"  ✓ {indicator}")
        
        if len(found_indicators) >= 2:  # 至少找到2个指标就算成功
            print("✅ 游戏启动测试成功！")
            return True
        else:
            print("❌ 游戏启动测试失败")
            return False
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_core_modules():
    """测试核心模块导入"""
    print("\n🔧 测试核心模块导入...")
    
    modules_to_test = [
        'game_state',
        'core_engine', 
        'actions',
        'bot_player',
        'card_base',
        'achievement_system',
        'wisdom_system'
    ]
    
    success_count = 0
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ {module_name}: {e}")
    
    print(f"\n📊 模块导入成功率: {success_count}/{len(modules_to_test)} ({success_count/len(modules_to_test)*100:.1f}%)")
    return success_count == len(modules_to_test)

def main():
    """主测试函数"""
    print("🚀 天机变游戏快速测试")
    print("=" * 50)
    
    # 测试模块导入
    modules_ok = test_core_modules()
    
    # 测试游戏启动
    startup_ok = test_game_startup()
    
    print("\n" + "=" * 50)
    print("📋 测试总结:")
    print(f"  模块导入: {'✅ 通过' if modules_ok else '❌ 失败'}")
    print(f"  游戏启动: {'✅ 通过' if startup_ok else '❌ 失败'}")
    
    if modules_ok and startup_ok:
        print("\n🎉 所有测试通过！游戏运行正常。")
        return True
    else:
        print("\n⚠️  部分测试失败，需要进一步检查。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)