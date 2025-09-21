"""
交互式演卦教程系统
将传统的文档阅读变为解决谜题的互动体验
"""

import random
import time

# 尝试导入快速增强功能
try:
    from quick_enhancements import QuickEnhancements
    QUICK_ENHANCEMENTS_AVAILABLE = True
    quick_enhancer = QuickEnhancements()
except ImportError:
    QUICK_ENHANCEMENTS_AVAILABLE = False
    quick_enhancer = None

class InteractiveTutorial:
    def __init__(self):
        self.enhancer = quick_enhancer if QUICK_ENHANCEMENTS_AVAILABLE else None
        self.current_lesson = 0
        self.player_progress = {
            'lessons_completed': [],
            'total_score': 0,
            'understanding_level': 0
        }
        
        # 教程关卡设计
        self.lessons = [
            {
                'title': '第一课：阴阳初识',
                'scenario': '你面前有一个失衡的太极图，阳气过盛，即将爆炸！',
                'problem': '阳气: 90, 阴气: 10',
                'goal': '使用手中的卦象牌，让阴阳达到平衡',
                'available_cards': ['坤卦 (增加30阴气)', '巽卦 (增加15阴气，减少5阳气)'],
                'correct_solution': 1,  # 坤卦
                'explanation': '坤卦代表大地之德，能够大幅增加阴气，是平衡阳气过盛的最佳选择。'
            },
            {
                'title': '第二课：五行相生',
                'scenario': '一位修行者的五行失调，木气不足，影响了整体修为',
                'problem': '木: 20, 火: 60, 土: 50, 金: 70, 水: 40',
                'goal': '选择正确的五行调和方案',
                'available_cards': ['水生木 (水-10, 木+20)', '金克木 (金+10, 木-10)', '木生火 (木-5, 火+15)'],
                'correct_solution': 0,  # 水生木
                'explanation': '五行相生：水生木。当木气不足时，应该增强水气来滋养木气，这是自然的生克规律。'
            },
            {
                'title': '第三课：卦象组合',
                'scenario': '两个修行者要进行卦象对决，你需要选择最佳的应对策略',
                'problem': '对手打出了"乾卦"(纯阳)，你的阴阳各为50',
                'goal': '选择最佳的应对卦象',
                'available_cards': ['坤卦 (纯阴)', '坎卦 (阴中有阳)', '离卦 (阳中有阴)'],
                'correct_solution': 1,  # 坎卦
                'explanation': '面对纯阳的乾卦，坎卦(阴中有阳)是最佳应对，既能制衡对方的阳气，又保持自身的平衡。'
            },
            {
                'title': '第四课：境界提升',
                'scenario': '你已达到筑基期巅峰，需要突破到金丹期',
                'problem': '当前境界: 筑基期 (道行: 95/100)，需要完美的阴阳平衡才能突破',
                'goal': '在保持阴阳平衡的同时，获得最后5点道行',
                'available_cards': ['太极归一 (阴阳各+2, 道行+5)', '纯阳突破 (阳+10, 道行+8)', '纯阴凝聚 (阴+10, 道行+8)'],
                'correct_solution': 0,  # 太极归一
                'explanation': '突破境界需要阴阳平衡，太极归一既能提升道行，又能保持完美平衡，是修行的至高境界。'
            },
            {
                'title': '第五课：实战应用',
                'scenario': '在一场重要的修行大会上，你面临最终挑战',
                'problem': '你需要在3回合内，从混乱状态恢复到完美平衡',
                'goal': '综合运用所学知识，制定最佳策略',
                'available_cards': ['多种卦象组合'],
                'correct_solution': -1,  # 综合判断
                'explanation': '这是对你所有学习成果的综合考验，需要灵活运用阴阳五行的智慧。'
            }
        ]
    
    def colorize(self, text, color):
        """颜色化文本"""
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
        print(f"  {self.colorize('🎓 交互式演卦教程 🎓', 'cyan')}")
        print("="*60)
        
        welcome_text = """
        欢迎来到《易经》的奇妙世界！
        
        在这里，你不需要死记硬背复杂的理论，
        而是通过解决实际问题来学习古老的智慧。
        
        每一个关卡都是一个谜题，
        每一次选择都是一次领悟。
        
        准备好开始你的修行之旅了吗？
        """
        
        self.print_with_delay(welcome_text)
        
        input(f"\n{self.colorize('按回车键开始第一课...', 'yellow')}")
    
    def show_lesson_intro(self, lesson_index):
        """显示课程介绍"""
        lesson = self.lessons[lesson_index]
        
        print("\n" + "="*60)
        print(f"  {self.colorize(lesson['title'], 'yellow')}")
        print("="*60)
        
        # 显示场景
        print(f"\n📖 {self.colorize('场景描述', 'cyan')}:")
        self.print_with_delay(f"   {lesson['scenario']}")
        
        # 显示问题状态
        print(f"\n📊 {self.colorize('当前状态', 'red')}:")
        self.print_with_delay(f"   {lesson['problem']}")
        
        # 显示目标
        print(f"\n🎯 {self.colorize('你的任务', 'green')}:")
        self.print_with_delay(f"   {lesson['goal']}")
        
        if self.enhancer:
            self.enhancer.show_loading_animation("准备谜题", 2)
    
    def present_choices(self, lesson_index):
        """展示选择项"""
        lesson = self.lessons[lesson_index]
        
        print(f"\n🃏 {self.colorize('可用选项', 'purple')}:")
        print("-" * 40)
        
        for i, card in enumerate(lesson['available_cards']):
            print(f"  {i + 1}. {self.colorize(card, 'white')}")
        
        print("-" * 40)
        
        while True:
            try:
                choice = input(f"\n请选择你的策略 (1-{len(lesson['available_cards'])}): ")
                choice_index = int(choice) - 1
                
                if 0 <= choice_index < len(lesson['available_cards']):
                    return choice_index
                else:
                    print(f"{self.colorize('❌ 无效选择，请重新输入', 'red')}")
            except ValueError:
                print(f"{self.colorize('❌ 请输入数字', 'red')}")
    
    def evaluate_choice(self, lesson_index, choice_index):
        """评估选择结果"""
        lesson = self.lessons[lesson_index]
        
        if lesson['correct_solution'] == -1:  # 综合判断题
            return self.evaluate_comprehensive_choice(lesson_index, choice_index)
        
        is_correct = choice_index == lesson['correct_solution']
        
        print("\n" + "="*50)
        
        if is_correct:
            print(f"  {self.colorize('🎉 正确！', 'green')}")
            if self.enhancer:
                self.enhancer.show_victory_celebration()
            score = 20
        else:
            print(f"  {self.colorize('❌ 不太对...', 'red')}")
            score = 5
            
        print("="*50)
        
        # 显示解释
        print(f"\n💡 {self.colorize('智慧解析', 'cyan')}:")
        self.print_with_delay(f"   {lesson['explanation']}")
        
        # 更新进度
        self.player_progress['total_score'] += score
        self.player_progress['lessons_completed'].append(lesson_index)
        
        if is_correct:
            self.player_progress['understanding_level'] += 1
        
        return is_correct, score
    
    def evaluate_comprehensive_choice(self, lesson_index, choice_index):
        """评估综合应用题"""
        # 这里可以设计更复杂的评估逻辑
        strategies = [
            "保守稳健策略",
            "激进突破策略", 
            "平衡调和策略"
        ]
        
        if choice_index < len(strategies):
            strategy = strategies[choice_index]
            print(f"\n你选择了：{self.colorize(strategy, 'yellow')}")
            
            # 模拟策略效果
            if choice_index == 2:  # 平衡策略通常是最佳选择
                print(f"{self.colorize('🎉 优秀的选择！平衡是易经的核心智慧。', 'green')}")
                return True, 25
            else:
                print(f"{self.colorize('👍 不错的尝试，但平衡策略可能更好。', 'yellow')}")
                return False, 15
        
        return False, 5
    
    def show_progress(self):
        """显示学习进度"""
        completed = len(self.player_progress['lessons_completed'])
        total = len(self.lessons)
        score = self.player_progress['total_score']
        level = self.player_progress['understanding_level']
        
        print("\n" + "="*50)
        print(f"  {self.colorize('📈 学习进度', 'cyan')}")
        print("="*50)
        print(f"已完成课程: {self.colorize(f'{completed}/{total}', 'green')}")
        print(f"总分: {self.colorize(str(score), 'yellow')}")
        print(f"理解等级: {self.colorize(f'Lv.{level}', 'purple')}")
        
        # 显示等级称号
        if level >= 4:
            title = "易学大师"
            color = 'purple'
        elif level >= 3:
            title = "修行有成"
            color = 'blue'
        elif level >= 2:
            title = "初窥门径"
            color = 'green'
        else:
            title = "初学者"
            color = 'white'
            
        print(f"当前称号: {self.colorize(title, color)}")
        print("="*50)
    
    def run_lesson(self, lesson_index):
        """运行单个课程"""
        if lesson_index >= len(self.lessons):
            return False
            
        self.show_lesson_intro(lesson_index)
        choice_index = self.present_choices(lesson_index)
        is_correct, score = self.evaluate_choice(lesson_index, choice_index)
        
        print(f"\n本课得分: {self.colorize(f'+{score}', 'green')}")
        
        input(f"\n{self.colorize('按回车键继续...', 'yellow')}")
        
        return True
    
    def run_full_tutorial(self):
        """运行完整教程"""
        self.show_welcome()
        
        for i in range(len(self.lessons)):
            success = self.run_lesson(i)
            if not success:
                break
                
            self.show_progress()
            
            if i < len(self.lessons) - 1:
                continue_choice = input(f"\n继续下一课？(y/n): ").lower()
                if continue_choice != 'y':
                    break
        
        self.show_final_results()
    
    def show_final_results(self):
        """显示最终结果"""
        print("\n" + "="*60)
        print(f"  {self.colorize('🎓 教程完成！', 'cyan')}")
        print("="*60)
        
        score = self.player_progress['total_score']
        level = self.player_progress['understanding_level']
        
        if score >= 80:
            grade = "优秀"
            color = 'green'
            message = "你已经掌握了易经的核心智慧！"
        elif score >= 60:
            grade = "良好"
            color = 'blue'
            message = "你对易经有了很好的理解！"
        elif score >= 40:
            grade = "及格"
            color = 'yellow'
            message = "你已经入门，继续努力！"
        else:
            grade = "需要加强"
            color = 'red'
            message = "建议重新学习基础概念。"
        
        print(f"\n最终评价: {self.colorize(grade, color)}")
        print(f"总分: {self.colorize(str(score), 'yellow')}")
        print(f"理解等级: {self.colorize(f'Lv.{level}', 'purple')}")
        print(f"\n{message}")
        
        if self.enhancer and score >= 60:
            self.enhancer.show_victory_celebration()
        
        print(f"\n{self.colorize('恭喜你完成了交互式演卦教程！', 'cyan')}")
        print("现在你可以在实际游戏中运用这些智慧了。")

def start_interactive_tutorial():
    """启动交互式教程"""
    tutorial = InteractiveTutorial()
    tutorial.run_full_tutorial()

if __name__ == "__main__":
    start_interactive_tutorial()