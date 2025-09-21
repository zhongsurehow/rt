#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天机变 - 简化图形界面版本
仅使用tkinter标准库的游戏GUI实现
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import json
from typing import Dict, List, Optional, Any

# 导入游戏核心模块
try:
    from game_state import GameState, Player, Zone
    from game_data import GAME_DECK, EMPEROR_AVATAR, HERMIT_AVATAR
    from main import setup_game
    from bot_player import get_bot_choice
    from config_manager import ConfigManager
except ImportError as e:
    print(f"导入游戏模块失败: {e}")
    print("请确保在game_prototype目录下运行此程序")

class SimpleGameGUI:
    """简化版游戏图形界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("天机变 - 易经策略游戏")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f5f5dc")
        
        # 游戏状态
        self.game_state: Optional[GameState] = None
        self.multiplayer_manager = None
        self.current_player_index = 0
        self.selected_card_index = -1
        
        # 配置管理器
        try:
            self.config_manager = ConfigManager()
        except:
            self.config_manager = None
        
        # 初始化界面
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建主菜单栏
        self.create_menu()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 显示开始界面
        self.show_start_screen()
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 游戏菜单
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="游戏", menu=game_menu)
        game_menu.add_command(label="新游戏", command=self.new_game)
        game_menu.add_command(label="保存游戏", command=self.save_game)
        game_menu.add_command(label="加载游戏", command=self.load_game)
        game_menu.add_separator()
        game_menu.add_command(label="退出", command=self.root.quit)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="游戏规则", command=self.show_rules)
        help_menu.add_command(label="易经知识", command=self.show_yijing_guide)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def show_start_screen(self):
        """显示开始界面"""
        # 清空主框架
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # 创建开始界面
        start_frame = ttk.Frame(self.main_frame)
        start_frame.pack(expand=True, fill=tk.BOTH)
        
        # 游戏标题
        title_label = tk.Label(
            start_frame, 
            text="天机变", 
            font=("华文行楷", 48, "bold"),
            fg="#8b4513",
            bg="#f5f5dc"
        )
        title_label.pack(pady=50)
        
        # 副标题
        subtitle_label = tk.Label(
            start_frame,
            text="易经主题策略游戏",
            font=("宋体", 18),
            fg="#666666",
            bg="#f5f5dc"
        )
        subtitle_label.pack(pady=10)
        
        # 按钮框架
        button_frame = ttk.Frame(start_frame)
        button_frame.pack(pady=50)
        
        # 开始游戏按钮
        start_button = tk.Button(
            button_frame,
            text="开始新游戏",
            font=("宋体", 16),
            width=15,
            height=2,
            bg="#daa520",
            fg="white",
            command=self.show_game_setup
        )
        start_button.pack(pady=10)
        
        # 加载游戏按钮
        load_button = tk.Button(
            button_frame,
            text="加载游戏",
            font=("宋体", 16),
            width=15,
            height=2,
            bg="#708090",
            fg="white",
            command=self.load_game
        )
        load_button.pack(pady=10)
        
        # 游戏规则按钮
        rules_button = tk.Button(
            button_frame,
            text="游戏规则",
            font=("宋体", 16),
            width=15,
            height=2,
            bg="#4682b4",
            fg="white",
            command=self.show_rules
        )
        rules_button.pack(pady=10)
    
    def show_game_setup(self):
        """显示游戏设置界面"""
        # 清空主框架
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # 创建设置界面
        setup_frame = ttk.Frame(self.main_frame)
        setup_frame.pack(expand=True, fill=tk.BOTH)
        
        # 标题
        title_label = tk.Label(
            setup_frame,
            text="游戏设置",
            font=("宋体", 24, "bold"),
            fg="#8b4513",
            bg="#f5f5dc"
        )
        title_label.pack(pady=30)
        
        # 设置选项框架
        options_frame = ttk.Frame(setup_frame)
        options_frame.pack(pady=20)
        
        # 玩家数量选择
        player_count_frame = ttk.Frame(options_frame)
        player_count_frame.pack(pady=10)
        
        tk.Label(player_count_frame, text="玩家数量:", font=("宋体", 14)).pack(side=tk.LEFT, padx=10)
        self.player_count_var = tk.StringVar(value="2")
        player_count_combo = ttk.Combobox(
            player_count_frame,
            textvariable=self.player_count_var,
            values=["1", "2", "3", "4"],
            state="readonly",
            width=10
        )
        player_count_combo.pack(side=tk.LEFT, padx=10)
        
        # 玩家名称输入
        names_frame = ttk.Frame(options_frame)
        names_frame.pack(pady=20)
        
        tk.Label(names_frame, text="玩家名称:", font=("宋体", 14)).pack(anchor=tk.W)
        
        self.player_name_entries = []
        for i in range(4):
            name_frame = ttk.Frame(names_frame)
            name_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(name_frame, text=f"玩家{i+1}:", width=8).pack(side=tk.LEFT)
            entry = tk.Entry(name_frame, width=20)
            entry.pack(side=tk.LEFT, padx=10)
            if i == 0:
                entry.insert(0, "玩家")
            elif i == 1:
                entry.insert(0, "电脑")
            self.player_name_entries.append(entry)
        
        # 按钮框架
        button_frame = ttk.Frame(setup_frame)
        button_frame.pack(pady=30)
        
        # 开始游戏按钮
        start_button = tk.Button(
            button_frame,
            text="开始游戏",
            font=("宋体", 16),
            width=12,
            height=2,
            bg="#228b22",
            fg="white",
            command=self.start_new_game
        )
        start_button.pack(side=tk.LEFT, padx=10)
        
        # 返回按钮
        back_button = tk.Button(
            button_frame,
            text="返回",
            font=("宋体", 16),
            width=12,
            height=2,
            bg="#cd853f",
            fg="white",
            command=self.show_start_screen
        )
        back_button.pack(side=tk.LEFT, padx=10)
    
    def start_new_game(self):
        """开始新游戏"""
        try:
            # 获取玩家数量
            num_players = int(self.player_count_var.get())
            
            # 获取玩家名称
            player_names = []
            for i in range(num_players):
                name = self.player_name_entries[i].get().strip()
                if not name:
                    name = f"玩家{i+1}"
                player_names.append(name)
            
            # 初始化游戏
            self.game_state, self.multiplayer_manager = setup_game(num_players, player_names)
            self.current_player_index = 0
            self.selected_card_index = -1
            
            # 显示游戏界面
            self.show_game_screen()
            
        except Exception as e:
            messagebox.showerror("错误", f"启动游戏失败: {e}")
    
    def show_game_screen(self):
        """显示主游戏界面"""
        # 清空主框架
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # 创建游戏界面布局
        # 顶部信息栏
        self.create_top_info_bar()
        
        # 主游戏区域
        game_area = ttk.Frame(self.main_frame)
        game_area.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 左侧：游戏棋盘
        self.create_game_board(game_area)
        
        # 右侧：玩家信息和控制面板
        self.create_control_panel(game_area)
        
        # 底部：当前玩家手牌
        self.create_hand_area()
        
        # 更新界面
        self.update_game_display()
    
    def create_top_info_bar(self):
        """创建顶部信息栏"""
        info_frame = ttk.Frame(self.main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 当前回合信息
        self.turn_label = tk.Label(
            info_frame,
            text="回合 1",
            font=("宋体", 14, "bold"),
            bg="#f5f5dc"
        )
        self.turn_label.pack(side=tk.LEFT)
        
        # 当前玩家信息
        self.current_player_label = tk.Label(
            info_frame,
            text="当前玩家: 玩家1",
            font=("宋体", 14, "bold"),
            fg="#8b4513",
            bg="#f5f5dc"
        )
        self.current_player_label.pack(side=tk.LEFT, padx=20)
        
        # 游戏菜单按钮
        menu_button = tk.Button(
            info_frame,
            text="菜单",
            font=("宋体", 12),
            command=self.show_game_menu
        )
        menu_button.pack(side=tk.RIGHT)
    
    def create_game_board(self, parent):
        """创建游戏棋盘"""
        board_frame = ttk.LabelFrame(parent, text="天地人三才棋盘", padding=10)
        board_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 棋盘画布
        self.board_canvas = tk.Canvas(
            board_frame,
            width=500,
            height=350,
            bg="#fff8dc",
            relief=tk.RAISED,
            borderwidth=2
        )
        self.board_canvas.pack()
        
        # 绘制棋盘
        self.draw_game_board()
    
    def draw_game_board(self):
        """绘制游戏棋盘"""
        canvas = self.board_canvas
        
        # 清空画布
        canvas.delete("all")
        
        # 绘制三个区域
        # 天区域
        canvas.create_rectangle(30, 30, 470, 120, fill="#87ceeb", outline="#4682b4", width=2)
        canvas.create_text(250, 75, text="天", font=("华文行楷", 20, "bold"), fill="#2c3e50")
        canvas.create_text(250, 95, text="天行健，君子以自强不息", font=("宋体", 10), fill="#2c3e50")
        
        # 人区域
        canvas.create_rectangle(30, 140, 470, 230, fill="#98fb98", outline="#228b22", width=2)
        canvas.create_text(250, 185, text="人", font=("华文行楷", 20, "bold"), fill="#2c3e50")
        canvas.create_text(250, 205, text="人道中庸，和谐共处", font=("宋体", 10), fill="#2c3e50")
        
        # 地区域
        canvas.create_rectangle(30, 250, 470, 340, fill="#deb887", outline="#8b7355", width=2)
        canvas.create_text(250, 295, text="地", font=("华文行楷", 20, "bold"), fill="#2c3e50")
        canvas.create_text(250, 315, text="地势坤，君子以厚德载物", font=("宋体", 10), fill="#2c3e50")
        
        # 绘制八卦位置
        gua_positions = [
            (100, 75, "乾", "#daa520"),   # 天-乾
            (400, 75, "离", "#ff4500"),   # 天-离
            (70, 185, "兑", "#ff69b4"),   # 人-兑
            (430, 185, "震", "#32cd32"),  # 人-震
            (100, 295, "坤", "#cd853f"),  # 地-坤
            (400, 295, "坎", "#4169e1"),  # 地-坎
            (250, 75, "艮", "#8b4513"),   # 天-艮
            (250, 295, "巽", "#9370db"),  # 地-巽
        ]
        
        for x, y, gua_name, color in gua_positions:
            canvas.create_oval(x-15, y-15, x+15, y+15, fill=color, outline="black", width=2)
            canvas.create_text(x, y, text=gua_name, font=("宋体", 10, "bold"), fill="white")
        
        # 绘制太极中心
        canvas.create_oval(235, 170, 265, 200, fill="#ecf0f1", outline="#bdc3c7", width=2)
        canvas.create_text(250, 185, text="太极", font=("宋体", 8, "bold"), fill="#2c3e50")
        
        # 如果游戏已开始，绘制影响力标记
        if self.game_state:
            self.draw_influence_markers()
    
    def draw_influence_markers(self):
        """绘制影响力标记"""
        # 简单示例：在各个区域显示玩家的影响力标记数量
        if not self.game_state:
            return
        
        canvas = self.board_canvas
        
        # 显示每个玩家在各区域的影响力
        y_offset = 0
        for i, player in enumerate(self.game_state.players):
            color = ["red", "blue", "green", "yellow"][i % 4]
            
            # 在棋盘右侧显示玩家信息
            canvas.create_text(
                480, 50 + y_offset,
                text=f"{player.name}: {player.influence_markers}",
                font=("宋体", 10),
                fill=color,
                anchor="w"
            )
            y_offset += 20
    
    def create_control_panel(self, parent):
        """创建控制面板"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # 玩家信息区域
        self.create_player_info_panel(control_frame)
        
        # 行动按钮区域
        self.create_action_buttons(control_frame)
        
        # 游戏日志区域
        self.create_game_log(control_frame)
    
    def create_player_info_panel(self, parent):
        """创建玩家信息面板"""
        self.info_frame = ttk.LabelFrame(parent, text="玩家信息", padding=10)
        self.info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 这个方法会在update_game_display中被调用来更新内容
        self.update_player_info()
    
    def update_player_info(self):
        """更新玩家信息显示"""
        # 清空现有内容
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        
        if not self.game_state:
            return
        
        current_player = self.game_state.players[self.current_player_index]
        
        # 玩家名称
        name_label = tk.Label(
            self.info_frame,
            text=current_player.name,
            font=("宋体", 14, "bold")
        )
        name_label.pack(pady=5)
        
        # 头像类型
        avatar_label = tk.Label(
            self.info_frame,
            text=f"身份: {current_player.avatar.name.value}",
            font=("宋体", 12)
        )
        avatar_label.pack(pady=2)
        
        # 资源信息
        resources_info = [
            f"道行: {current_player.dao_xing}",
            f"气: {current_player.qi}",
            f"诚意: {current_player.cheng_yi}",
            f"影响力标记: {current_player.influence_markers}",
            f"当前位置: {current_player.position.value}",
            f"手牌数量: {len(current_player.hand)}"
        ]
        
        for info in resources_info:
            label = tk.Label(
                self.info_frame,
                text=info,
                font=("宋体", 11)
            )
            label.pack(pady=1, anchor=tk.W)
    
    def create_action_buttons(self, parent):
        """创建行动按钮"""
        action_frame = ttk.LabelFrame(parent, text="行动选择", padding=10)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 行动按钮
        actions = [
            ("演卦", self.action_play_card, "#ff6b6b"),
            ("升沉", self.action_move, "#4ecdc4"),
            ("布局", self.action_place_influence, "#45b7d1"),
            ("研习", self.action_study, "#96ceb4"),
            ("结束回合", self.end_turn, "#feca57")
        ]
        
        for action_name, command, color in actions:
            button = tk.Button(
                action_frame,
                text=action_name,
                font=("宋体", 12),
                width=12,
                bg=color,
                fg="white",
                command=command
            )
            button.pack(pady=3, fill=tk.X)
    
    def create_game_log(self, parent):
        """创建游戏日志"""
        log_frame = ttk.LabelFrame(parent, text="游戏日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建文本框和滚动条
        text_frame = ttk.Frame(log_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(
            text_frame,
            width=25,
            height=10,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("宋体", 10)
        )
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加初始日志
        self.add_log("游戏开始！")
    
    def create_hand_area(self):
        """创建手牌区域"""
        hand_frame = ttk.LabelFrame(self.main_frame, text="手牌", padding=10)
        hand_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 手牌显示框架
        self.hand_display_frame = ttk.Frame(hand_frame)
        self.hand_display_frame.pack(fill=tk.X)
        
        # 绘制手牌
        self.draw_hand_cards()
    
    def draw_hand_cards(self):
        """绘制手牌"""
        # 清空现有手牌显示
        for widget in self.hand_display_frame.winfo_children():
            widget.destroy()
        
        if not self.game_state:
            return
        
        current_player = self.game_state.players[self.current_player_index]
        hand_cards = current_player.hand
        
        if not hand_cards:
            no_cards_label = tk.Label(
                self.hand_display_frame,
                text="没有手牌",
                font=("宋体", 12),
                fg="#666666"
            )
            no_cards_label.pack(pady=20)
            return
        
        # 创建卡牌按钮
        cards_frame = ttk.Frame(self.hand_display_frame)
        cards_frame.pack(fill=tk.X, pady=10)
        
        for i, card in enumerate(hand_cards):
            # 创建卡牌框架
            card_frame = ttk.Frame(cards_frame)
            card_frame.pack(side=tk.LEFT, padx=5)
            
            # 卡牌按钮
            card_color = "#ffe4b5" if i == self.selected_card_index else "#f5f5dc"
            border_color = "#ff6b6b" if i == self.selected_card_index else "#8b4513"
            
            card_button = tk.Button(
                card_frame,
                text=f"{card.name}\n\n{card.description[:30]}{'...' if len(card.description) > 30 else ''}",
                font=("宋体", 10),
                width=15,
                height=6,
                bg=card_color,
                relief=tk.RAISED,
                borderwidth=2,
                command=lambda idx=i: self.select_card(idx)
            )
            card_button.pack()
            
            # 卡牌信息
            info_label = tk.Label(
                card_frame,
                text=f"等级: {getattr(card, 'level', '未知')}",
                font=("宋体", 9),
                fg="#666666"
            )
            info_label.pack()
    
    def select_card(self, card_index: int):
        """选择卡牌"""
        if not self.game_state:
            return
        
        current_player = self.game_state.players[self.current_player_index]
        if 0 <= card_index < len(current_player.hand):
            self.selected_card_index = card_index
            selected_card = current_player.hand[card_index]
            self.add_log(f"选择了卡牌: {selected_card.name}")
            
            # 重新绘制手牌以显示选中状态
            self.draw_hand_cards()
    
    def update_game_display(self):
        """更新游戏显示"""
        if not self.game_state:
            return
        
        # 更新当前玩家信息
        current_player = self.game_state.players[self.current_player_index]
        self.current_player_label.config(text=f"当前玩家: {current_player.name}")
        
        # 更新玩家信息面板
        self.update_player_info()
        
        # 重新绘制手牌
        self.draw_hand_cards()
        
        # 重新绘制棋盘
        self.draw_game_board()
    
    def add_log(self, message: str):
        """添加日志消息"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    # 游戏行动方法
    def action_play_card(self):
        """演卦行动"""
        if not self.game_state:
            return
        
        if self.selected_card_index == -1:
            messagebox.showwarning("提示", "请先选择一张卡牌")
            return
        
        current_player = self.game_state.players[self.current_player_index]
        if 0 <= self.selected_card_index < len(current_player.hand):
            selected_card = current_player.hand[self.selected_card_index]
            
            # 简单的卡牌效果处理
            self.add_log(f"{current_player.name} 演卦: {selected_card.name}")
            
            # 移除卡牌
            current_player.hand.pop(self.selected_card_index)
            self.selected_card_index = -1
            
            # 应用卡牌效果（简化版）
            if hasattr(selected_card, 'reward_dao_xing'):
                current_player.dao_xing += selected_card.reward_dao_xing
                if selected_card.reward_dao_xing > 0:
                    self.add_log(f"获得 {selected_card.reward_dao_xing} 点道行")
            
            if hasattr(selected_card, 'reward_cheng_yi'):
                current_player.cheng_yi += selected_card.reward_cheng_yi
                if selected_card.reward_cheng_yi > 0:
                    self.add_log(f"获得 {selected_card.reward_cheng_yi} 点诚意")
            
            # 更新显示
            self.update_game_display()
        else:
            messagebox.showerror("错误", "无效的卡牌选择")
    
    def action_move(self):
        """升沉行动"""
        if not self.game_state:
            return
        
        current_player = self.game_state.players[self.current_player_index]
        
        # 创建移动选择对话框
        move_window = tk.Toplevel(self.root)
        move_window.title("选择移动目标")
        move_window.geometry("300x200")
        move_window.configure(bg="#f5f5dc")
        
        tk.Label(move_window, text="选择移动到的位置:", font=("宋体", 12)).pack(pady=10)
        
        # 移动选项
        zones = [Zone.TIAN, Zone.REN, Zone.DI]
        for zone in zones:
            if zone != current_player.position:
                button = tk.Button(
                    move_window,
                    text=f"移动到 {zone.value}",
                    font=("宋体", 12),
                    width=15,
                    command=lambda z=zone: self.execute_move(z, move_window)
                )
                button.pack(pady=5)
        
        # 取消按钮
        cancel_button = tk.Button(
            move_window,
            text="取消",
            font=("宋体", 12),
            width=15,
            command=move_window.destroy
        )
        cancel_button.pack(pady=10)
    
    def execute_move(self, target_zone: Zone, window):
        """执行移动"""
        current_player = self.game_state.players[self.current_player_index]
        
        if current_player.qi >= 1:  # 假设移动需要1点气
            current_player.qi -= 1
            old_position = current_player.position
            current_player.position = target_zone
            
            self.add_log(f"{current_player.name} 从 {old_position.value} 移动到 {target_zone.value}")
            self.update_game_display()
            window.destroy()
        else:
            messagebox.showwarning("气不足", "移动需要至少1点气")
    
    def action_place_influence(self):
        """布局行动"""
        if not self.game_state:
            return
        
        current_player = self.game_state.players[self.current_player_index]
        
        if current_player.influence_markers > 0:
            current_player.influence_markers -= 1
            self.add_log(f"{current_player.name} 放置了一个影响力标记")
            self.update_game_display()
        else:
            messagebox.showwarning("提示", "没有可用的影响力标记")
    
    def action_study(self):
        """研习行动"""
        if not self.game_state:
            return
        
        current_player = self.game_state.players[self.current_player_index]
        
        if current_player.qi >= 2:  # 假设研习需要2点气
            current_player.qi -= 2
            
            # 简单的抽卡逻辑
            if GAME_DECK:
                import random
                new_card = random.choice(GAME_DECK)
                current_player.hand.append(new_card)
                self.add_log(f"{current_player.name} 研习获得卡牌: {new_card.name}")
                self.update_game_display()
            else:
                self.add_log(f"{current_player.name} 研习，但牌库已空")
        else:
            messagebox.showwarning("气不足", "研习需要至少2点气")
    
    def end_turn(self):
        """结束回合"""
        if not self.game_state:
            return
        
        current_player = self.game_state.players[self.current_player_index]
        self.add_log(f"{current_player.name} 结束回合")
        
        # 回合结束时的处理
        current_player.qi += 1  # 每回合恢复1点气
        
        # 切换到下一个玩家
        self.current_player_index = (self.current_player_index + 1) % len(self.game_state.players)
        self.selected_card_index = -1
        
        # 检查胜利条件
        self.check_victory()
        
        # 更新显示
        self.update_game_display()
        
        # 如果是AI玩家，自动执行回合
        next_player = self.game_state.players[self.current_player_index]
        if "电脑" in next_player.name or "AI" in next_player.name:
            self.root.after(1000, self.ai_turn)  # 1秒后执行AI回合
    
    def ai_turn(self):
        """AI玩家回合"""
        if not self.game_state:
            return
        
        current_player = self.game_state.players[self.current_player_index]
        self.add_log(f"{current_player.name} 正在思考...")
        
        # 简单的AI逻辑
        import random
        
        # 随机选择行动
        actions = ["play_card", "move", "place_influence", "study", "end_turn"]
        weights = [3, 2, 2, 2, 1]  # 偏向于打牌
        
        action = random.choices(actions, weights=weights)[0]
        
        if action == "play_card" and current_player.hand:
            # 随机打一张牌
            self.selected_card_index = random.randint(0, len(current_player.hand) - 1)
            self.action_play_card()
        elif action == "move" and current_player.qi >= 1:
            # 随机移动
            zones = [Zone.TIAN, Zone.REN, Zone.DI]
            available_zones = [z for z in zones if z != current_player.position]
            if available_zones:
                target_zone = random.choice(available_zones)
                current_player.qi -= 1
                old_position = current_player.position
                current_player.position = target_zone
                self.add_log(f"{current_player.name} 从 {old_position.value} 移动到 {target_zone.value}")
        elif action == "place_influence" and current_player.influence_markers > 0:
            self.action_place_influence()
        elif action == "study" and current_player.qi >= 2:
            self.action_study()
        else:
            # 结束回合
            self.end_turn()
            return
        
        # 继续AI回合或结束
        if random.random() < 0.3:  # 30%概率结束回合
            self.end_turn()
        else:
            self.root.after(1500, self.ai_turn)  # 1.5秒后继续
    
    def check_victory(self):
        """检查胜利条件"""
        if not self.game_state:
            return
        
        for player in self.game_state.players:
            # 简单的胜利条件：道行达到10点
            if player.dao_xing >= 10:
                messagebox.showinfo("游戏结束", f"{player.name} 获得胜利！\n道行达到 {player.dao_xing} 点")
                self.show_start_screen()
                return
    
    # 菜单功能方法
    def new_game(self):
        """新游戏"""
        self.show_game_setup()
    
    def save_game(self):
        """保存游戏"""
        if not self.game_state:
            messagebox.showwarning("警告", "没有正在进行的游戏")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                # 简化的保存逻辑
                save_data = {
                    "current_player_index": self.current_player_index,
                    "players": []
                }
                
                for player in self.game_state.players:
                    player_data = {
                        "name": player.name,
                        "dao_xing": player.dao_xing,
                        "qi": player.qi,
                        "cheng_yi": player.cheng_yi,
                        "influence_markers": player.influence_markers,
                        "position": player.position.value,
                        "hand_count": len(player.hand)
                    }
                    save_data["players"].append(player_data)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("保存", f"游戏已保存到 {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {e}")
    
    def load_game(self):
        """加载游戏"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                
                messagebox.showinfo("加载", f"从 {filename} 加载游戏（功能开发中）")
            except Exception as e:
                messagebox.showerror("错误", f"加载失败: {e}")
    
    def show_game_menu(self):
        """显示游戏菜单"""
        menu_window = tk.Toplevel(self.root)
        menu_window.title("游戏菜单")
        menu_window.geometry("250x300")
        menu_window.configure(bg="#f5f5dc")
        
        # 菜单按钮
        buttons = [
            ("继续游戏", menu_window.destroy),
            ("保存游戏", self.save_game),
            ("加载游戏", self.load_game),
            ("游戏规则", self.show_rules),
            ("返回主菜单", lambda: [menu_window.destroy(), self.show_start_screen()])
        ]
        
        for text, command in buttons:
            button = tk.Button(
                menu_window,
                text=text,
                font=("宋体", 12),
                width=15,
                command=command
            )
            button.pack(pady=8)
    
    def show_rules(self):
        """显示游戏规则"""
        rules_window = tk.Toplevel(self.root)
        rules_window.title("游戏规则")
        rules_window.geometry("600x500")
        
        # 创建滚动文本框
        text_frame = ttk.Frame(rules_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("宋体", 11))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        rules_text = """天机变 - 游戏规则

【游戏目标】
通过演卦、布局、升沉等行动，在天地人三才棋盘上获得影响力，
最终达到胜利条件（道行达到10点）。

【基本概念】
• 道行：代表玩家的修为和智慧，是主要的胜利条件
• 气：用于执行各种行动的能量，每回合自动恢复1点
• 诚意：影响某些特殊行动的效果
• 影响力标记：在棋盘上标记控制区域的标记物

【棋盘区域】
• 天：天行健，君子以自强不息
• 人：人道中庸，和谐共处  
• 地：地势坤，君子以厚德载物

【行动类型】
1. 演卦：打出手牌，获得卦牌效果
   - 选择手牌中的一张卡牌
   - 获得卡牌上的奖励效果
   - 卡牌被弃置

2. 升沉：在天地人三才之间移动
   - 消耗1点气
   - 移动到不同的区域
   - 不同区域可能有不同的效果

3. 布局：在棋盘上放置影响力标记
   - 消耗1个影响力标记
   - 在当前区域放置标记
   - 控制区域获得优势

4. 研习：抽取新的卦牌
   - 消耗2点气
   - 从牌库抽取1张新卡牌
   - 增加手牌选择

【胜利条件】
• 道行达到10点即可获得胜利
• 游戏支持1-4人游戏
• AI玩家会自动执行回合

【操作说明】
• 点击手牌选择卡牌
• 点击行动按钮执行对应行动
• 查看右侧面板了解当前状态
• 游戏日志显示所有行动记录

更多详细规则和策略请在游戏中探索发现！
        """
        
        text_widget.insert(tk.END, rules_text)
        text_widget.config(state=tk.DISABLED)
    
    def show_yijing_guide(self):
        """显示易经指南"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("易经知识")
        guide_window.geometry("600x500")
        
        # 创建滚动文本框
        text_frame = ttk.Frame(guide_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("宋体", 11))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        guide_text = """易经知识指南

【八卦基础】
乾☰ - 天，代表刚健、创造、领导
坤☷ - 地，代表柔顺、承载、包容
震☳ - 雷，代表动、奋起、震撼
巽☴ - 风，代表入、顺从、渗透
坎☵ - 水，代表险、智慧、流动
离☲ - 火，代表明、美丽、光明
艮☶ - 山，代表止、稳重、静止
兑☱ - 泽，代表悦、交流、喜悦

【三才理论】
天 - 代表理想、精神层面、高远目标
人 - 代表现实、社会层面、人际关系
地 - 代表物质、基础层面、实际行动

【阴阳理论】
阴阳相互依存、相互转化、相互制约
阴爻 ⚋ 代表柔、静、退、收敛
阳爻 ⚊ 代表刚、动、进、扩张

【五行相生相克】
相生：金生水，水生木，木生火，火生土，土生金
相克：金克木，木克土，土克水，水克火，火克金

【易经智慧】
• 变化是永恒的主题
• 平衡是和谐的基础
• 适时而动是成功的关键
• 知进退是智慧的体现

【在游戏中的应用】
• 不同的卦象对应不同的策略
• 天地人三才代表不同的发展路径
• 阴阳平衡影响行动的效果
• 五行相生相克影响卡牌组合

通过学习易经智慧，可以更好地理解游戏机制，
制定更有效的策略，体验中华文化的博大精深。
        """
        
        text_widget.insert(tk.END, guide_text)
        text_widget.config(state=tk.DISABLED)
    
    def show_about(self):
        """显示关于信息"""
        messagebox.showinfo(
            "关于",
            "天机变 v1.0\n\n"
            "一款基于易经文化的策略游戏\n"
            "融合传统智慧与现代游戏设计\n\n"
            "特色功能：\n"
            "• 图形化游戏界面\n"
            "• 易经文化教育\n"
            "• 多人游戏支持\n"
            "• AI对手挑战\n\n"
            "开发：AI助手\n"
            "基于Python + tkinter"
        )
    
    def run(self):
        """运行游戏"""
        self.root.mainloop()

def main():
    """主函数"""
    # 创建并运行游戏
    game = SimpleGameGUI()
    game.run()

if __name__ == "__main__":
    main()