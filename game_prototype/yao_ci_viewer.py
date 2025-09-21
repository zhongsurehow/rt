#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爻辞典藏 - 文化体验模块
提供完整的爻辞查看和文化学习体验
"""

import time
import random

# 尝试导入增强功能
try:
    from quick_enhancements import QuickEnhancements
    ENHANCEMENTS_AVAILABLE = True
    enhancer = QuickEnhancements()
except ImportError:
    ENHANCEMENTS_AVAILABLE = False
    enhancer = None

class YaoCiViewer:
    """爻辞查看器"""
    
    def __init__(self):
        self.enhancer = enhancer
        self.available_hexagrams = ["乾", "坤", "震", "巽", "坎", "离", "艮", "兑"] if enhancer else []
    
    def colorize(self, text, color):
        """文字着色"""
        if self.enhancer:
            return self.enhancer.colorize(text, color)
        return text
    
    def print_with_delay(self, text, delay=0.03):
        """打字机效果"""
        if self.enhancer:
            self.enhancer.print_with_delay(text, delay)
        else:
            print(text)
    
    def show_welcome(self):
        """显示欢迎界面"""
        print("\n" + "="*60)
        print(self.colorize("📜 爻辞典藏 - 易经文化宝库 📜", "cyan"))
        print("="*60)
        
        welcome_text = """
        欢迎来到爻辞典藏！这里收录了《易经》的智慧精华。
        
        在这里，您可以：
        🔍 查看完整的卦象爻辞
        🎭 体验水墨风格的文化展示
        ✨ 获得随机的易经智慧
        📚 深入理解古老的哲学思想
        
        让我们一起探索这座智慧的宝库吧！
        """
        
        self.print_with_delay(welcome_text, 0.02)
        input(f"\n{self.colorize('按回车键继续...', 'yellow')}")
    
    def show_main_menu(self):
        """显示主菜单"""
        print("\n" + "─"*50)
        print(self.colorize("📜 爻辞典藏主菜单", "cyan"))
        print("─"*50)
        
        if ENHANCEMENTS_AVAILABLE:
            menu_options = [
                ("1", "🔍 查看特定卦象爻辞", "green"),
                ("2", "🎲 随机爻辞智慧", "blue"),
                ("3", "📚 八卦概览", "purple"),
                ("4", "✨ 今日智慧", "yellow"),
                ("5", "🎭 完整爻辞展示", "cyan"),
                ("0", "🔙 返回主菜单", "red")
            ]
            
            for num, desc, color in menu_options:
                print(f"   {self.colorize(num, color)}. {desc}")
        else:
            print("   1. 🔍 查看特定卦象爻辞")
            print("   2. 🎲 随机爻辞智慧")
            print("   3. 📚 八卦概览")
            print("   4. ✨ 今日智慧")
            print("   5. 🎭 完整爻辞展示")
            print("   0. 🔙 返回主菜单")
    
    def show_hexagram_list(self):
        """显示可用卦象列表"""
        if not ENHANCEMENTS_AVAILABLE:
            print("❌ 增强功能不可用，无法显示爻辞")
            return None
        
        print(f"\n{self.colorize('📋 可查看的卦象', 'cyan')}:")
        print("─"*30)
        
        for i, hexagram in enumerate(self.available_hexagrams, 1):
            symbol = self.enhancer.gua_symbols.get(hexagram, "?")
            print(f"   {i}. {self.colorize(hexagram, 'yellow')} {symbol}")
        
        print(f"   0. {self.colorize('返回', 'red')}")
        
        while True:
            try:
                choice = input(f"\n请选择卦象 (0-{len(self.available_hexagrams)}): ").strip()
                if choice == "0":
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(self.available_hexagrams):
                    return self.available_hexagrams[choice_num - 1]
                else:
                    print(f"请输入0-{len(self.available_hexagrams)}之间的数字")
            except ValueError:
                print("请输入有效数字")
            except KeyboardInterrupt:
                return None
    
    def show_hexagram_overview(self):
        """显示八卦概览"""
        print(f"\n{self.colorize('📚 八卦概览', 'cyan')}")
        print("="*50)
        
        if ENHANCEMENTS_AVAILABLE:
            for hexagram in self.available_hexagrams:
                if hexagram in self.enhancer.yao_ci_database:
                    data = self.enhancer.yao_ci_database[hexagram]
                    symbol = self.enhancer.gua_symbols.get(hexagram, "?")
                    
                    print(f"\n{self.colorize(f'{symbol} {data[\"name\"]}', 'yellow')}")
                    print(f"   性质：{data['nature']}")
                    print(f"   德性：{data['attribute']}")
                    
                    # 显示一个代表性爻辞
                    if 'yao_lines' in data and data['yao_lines']:
                        yao = data['yao_lines'][0]  # 取第一爻
                        print(f"   代表爻辞：{self.colorize(yao['text'], 'green')}")
                        print(f"   意境：{yao['imagery']}")
                    elif 'key_yao' in data:
                        yao = data['key_yao']
                        print(f"   核心爻辞：{self.colorize(yao['text'], 'green')}")
                        print(f"   意境：{yao['imagery']}")
                    
                    print("   " + "─"*40)
        else:
            print("❌ 增强功能不可用，无法显示详细信息")
        
        input(f"\n{self.colorize('按回车键返回...', 'yellow')}")
    
    def show_random_wisdom(self):
        """显示随机智慧"""
        if ENHANCEMENTS_AVAILABLE:
            self.enhancer.show_random_wisdom()
        else:
            print("❌ 增强功能不可用，无法显示随机智慧")
        
        input(f"\n{self.colorize('按回车键返回...', 'yellow')}")
    
    def show_daily_wisdom(self):
        """显示今日智慧"""
        print(f"\n{self.colorize('✨ 今日智慧 ✨', 'cyan')}")
        print("="*40)
        
        # 基于日期的伪随机选择，确保同一天显示相同内容
        import datetime
        today = datetime.date.today()
        random.seed(today.toordinal())
        
        if ENHANCEMENTS_AVAILABLE:
            # 从所有爻辞中选择今日智慧
            all_wisdom = []
            for hexagram_data in self.enhancer.yao_ci_database.values():
                if 'yao_lines' in hexagram_data:
                    for yao in hexagram_data['yao_lines']:
                        all_wisdom.append({
                            'hexagram': hexagram_data['name'],
                            'symbol': self.enhancer.gua_symbols.get(hexagram_data['name'], '?'),
                            'text': yao['text'],
                            'wisdom': yao['wisdom'],
                            'imagery': yao['imagery']
                        })
                elif 'key_yao' in hexagram_data:
                    yao = hexagram_data['key_yao']
                    all_wisdom.append({
                        'hexagram': hexagram_data['name'],
                        'symbol': self.enhancer.gua_symbols.get(hexagram_data['name'], '?'),
                        'text': yao['text'],
                        'wisdom': yao['wisdom'],
                        'imagery': yao['imagery']
                    })
            
            if all_wisdom:
                wisdom = random.choice(all_wisdom)
                
                print(f"📅 {today.strftime('%Y年%m月%d日')}")
                print(f"\n┌─ 来自 {wisdom['symbol']} {self.colorize(wisdom['hexagram'], 'yellow')} ─┐")
                print(f"│")
                print(f"│ {self.colorize('古文', 'green')}: {self.colorize(wisdom['text'], 'white')}")
                print(f"│")
                print(f"│ {self.colorize('意境', 'purple')}: {wisdom['imagery']}")
                print(f"│")
                print(f"│ {self.colorize('智慧', 'cyan')}: {wisdom['wisdom']}")
                print(f"│")
                print("└─────────────────────────────────────┘")
                
                print(f"\n{self.colorize('💡 思考', 'yellow')}: 今日如何将这份智慧应用到生活中？")
        else:
            print("❌ 增强功能不可用，无法显示今日智慧")
        
        # 重置随机种子
        random.seed()
        
        input(f"\n{self.colorize('按回车键返回...', 'yellow')}")
    
    def show_complete_display(self):
        """显示完整爻辞展示"""
        hexagram = self.show_hexagram_list()
        if hexagram and ENHANCEMENTS_AVAILABLE:
            print(f"\n{self.colorize('正在展开古卷...', 'yellow')}")
            time.sleep(1)
            self.enhancer.show_yao_ci_display(hexagram)
    
    def run(self):
        """运行爻辞查看器"""
        self.show_welcome()
        
        while True:
            self.show_main_menu()
            
            try:
                choice = input(f"\n请选择 (0-5): ").strip()
                
                if choice == "0":
                    print(f"\n{self.colorize('📜 愿易经智慧伴您前行！', 'cyan')}")
                    break
                elif choice == "1":
                    # 查看特定卦象
                    hexagram = self.show_hexagram_list()
                    if hexagram and ENHANCEMENTS_AVAILABLE:
                        self.enhancer.show_hexagram_cultural_display(hexagram)
                        input(f"\n{self.colorize('按回车键返回...', 'yellow')}")
                elif choice == "2":
                    # 随机智慧
                    self.show_random_wisdom()
                elif choice == "3":
                    # 八卦概览
                    self.show_hexagram_overview()
                elif choice == "4":
                    # 今日智慧
                    self.show_daily_wisdom()
                elif choice == "5":
                    # 完整展示
                    self.show_complete_display()
                else:
                    print("请输入0-5之间的数字")
                    
            except KeyboardInterrupt:
                print(f"\n\n{self.colorize('📜 愿易经智慧伴您前行！', 'cyan')}")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")

def start_yao_ci_viewer():
    """启动爻辞查看器"""
    viewer = YaoCiViewer()
    viewer.run()

if __name__ == "__main__":
    start_yao_ci_viewer()