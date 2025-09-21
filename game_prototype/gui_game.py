#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天机变 - 图形界面版本
基于tkinter的游戏GUI实现
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
from PIL import Image, ImageTk
import xml.etree.ElementTree as ET
from io import BytesIO
import cairosvg
from typing import Dict, List, Optional, Any

# 导入游戏核心模块
from game_state import GameState, Player, Zone
from game_data import GAME_DECK, EMPEROR_AVATAR, HERMIT_AVATAR
from main import setup_game, play_turn
from bot_player import get_bot_choice
from config_manager import ConfigManager

class SVGImageLoader:
    """SVG图片加载器"""
    
    @staticmethod
    def load_svg_as_image(svg_path: str, width: int = None, height: int = None) -> ImageTk.PhotoImage:
        """加载SVG文件并转换为tkinter可用的图片"""
        try:
            if not os.path.exists(svg_path):
                # 如果文件不存在，创建一个简单的占位图
                return SVGImageLoader.create_placeholder_image(width or 100, height or 100)
            
            # 读取SVG文件
            with open(svg_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            
            # 转换SVG为PNG
            png_data = cairosvg.svg2png(
                bytestring=svg_content.encode('utf-8'),
                output_width=width,
                output_height=height
            )
            
            # 创建PIL图像
            pil_image = Image.open(BytesIO(png_data))
            
            # 转换为tkinter图像
            return ImageTk.PhotoImage(pil_image)
            
        except Exception as e:
            print(f"加载SVG图片失败 {svg_path}: {e}")
            return SVGImageLoader.create_placeholder_image(width or 100, height or 100)
    
    @staticmethod
    def create_placeholder_image(width: int, height: int, color: str = "#cccccc") -> ImageTk.PhotoImage:
        """创建占位图片"""
        pil_image = Image.new('RGB', (width, height), color)
        return ImageTk.PhotoImage(pil_image)

class GameGUI:
    """游戏图形界面主类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("天机变 - 易经策略游戏")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f5f5dc")
        
        # 游戏状态
        self.game_state: Optional[GameState] = None
        self.multiplayer_manager = None
        self.current_player_index = 0
        
        # 配置管理器
        self.config_manager = ConfigManager()
        
        # 图片缓存
        self.images: Dict[str, ImageTk.PhotoImage] = {}
        
        # 初始化界面
        self.setup_ui()
        self.load_images()
        
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
    
    def load_images(self):
        """加载游戏图片资源"""
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        
        try:
            # 加载卡牌图片
            self.images["qian_card"] = SVGImageLoader.load_svg_as_image(
                os.path.join(assets_dir, "cards", "qian_card.svg"), 120, 180
            )
            self.images["kun_card"] = SVGImageLoader.load_svg_as_image(
                os.path.join(assets_dir, "cards", "kun_card.svg"), 120, 180
            )
            self.images["card_back"] = SVGImageLoader.load_svg_as_image(
                os.path.join(assets_dir, "cards", "card_back.svg"), 120, 180
            )
            
            # 加载UI图片
            self.images["game_board"] = SVGImageLoader.load_svg_as_image(
                os.path.join(assets_dir, "ui", "game_board.svg"), 600, 400
            )
            self.images["emperor_avatar"] = SVGImageLoader.load_svg_as_image(
                os.path.join(assets_dir, "ui", "player_avatar_emperor.svg"), 80, 80
            )
            self.images["hermit_avatar"] = SVGImageLoader.load_svg_as_image(
                os.path.join(assets_dir, "ui", "player_avatar_hermit.svg"), 80, 80
            )
            self.images["influence_marker"] = SVGImageLoader.load_svg_as_image(
                os.path.join(assets_dir, "ui", "influence_marker.svg"), 30, 30
            )
            
            # 加载图标
            self.images["qi_icon"] = SVGImageLoader.load_svg_as_image(
                os.path.join(assets_dir, "icons", "qi_icon.svg"), 24, 24
            )
            self.images["dao_xing_icon"] = SVGImageLoader.load_svg_as_image(
                os.path.join(assets_dir, "icons", "dao_xing_icon.svg"), 24, 24
            )
            self.images["cheng_yi_icon"] = SVGImageLoader.load_svg_as_image(
                os.path.join(assets_dir, "icons", "cheng_yi_icon.svg"), 24, 24
            )
            
        except Exception as e:
            print(f"加载图片资源时出错: {e}")
            # 使用占位图片
            for key in ["qian_card", "kun_card", "card_back"]:
                self.images[key] = SVGImageLoader.create_placeholder_image(120, 180)
            for key in ["game_board"]:
                self.images[key] = SVGImageLoader.create_placeholder_image(600, 400)
            for key in ["emperor_avatar", "hermit_avatar"]:
                self.images[key] = SVGImageLoader.create_placeholder_image(80, 80)
            for key in ["influence_marker"]:
                self.images[key] = SVGImageLoader.create_placeholder_image(30, 30)
            for key in ["qi_icon", "dao_xing_icon", "cheng_yi_icon"]:
                self.images[key] = SVGImageLoader.create_placeholder_image(24, 24)
    
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
        board_frame = ttk.Frame(parent)
        board_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 棋盘标题
        board_title = tk.Label(
            board_frame,
            text="天地人三才棋盘",
            font=("宋体", 16, "bold"),
            bg="#f5f5dc"
        )
        board_title.pack(pady=10)
        
        # 棋盘画布
        self.board_canvas = tk.Canvas(
            board_frame,
            width=600,
            height=400,
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
        canvas.create_rectangle(50, 50, 550, 150, fill="#87ceeb", outline="#4682b4", width=2)
        canvas.create_text(300, 100, text="天", font=("华文行楷", 24, "bold"), fill="#2c3e50")
        
        # 人区域
        canvas.create_rectangle(50, 170, 550, 270, fill="#98fb98", outline="#228b22", width=2)
        canvas.create_text(300, 220, text="人", font=("华文行楷", 24, "bold"), fill="#2c3e50")
        
        # 地区域
        canvas.create_rectangle(50, 290, 550, 390, fill="#deb887", outline="#8b7355", width=2)
        canvas.create_text(300, 340, text="地", font=("华文行楷", 24, "bold"), fill="#2c3e50")
        
        # 绘制八卦位置
        gua_positions = [
            (150, 100, "乾", "#daa520"),  # 天-乾
            (450, 100, "离", "#ff4500"),  # 天-离
            (100, 220, "兑", "#ff69b4"),  # 人-兑
            (500, 220, "震", "#32cd32"),  # 人-震
            (150, 340, "坤", "#cd853f"),  # 地-坤
            (450, 340, "坎", "#4169e1"),  # 地-坎
            (300, 100, "艮", "#8b4513"),  # 天-艮
            (300, 340, "巽", "#9370db"),  # 地-巽
        ]
        
        for x, y, gua_name, color in gua_positions:
            canvas.create_oval(x-20, y-20, x+20, y+20, fill=color, outline="black", width=2)
            canvas.create_text(x, y, text=gua_name, font=("宋体", 12, "bold"), fill="white")
        
        # 绘制太极中心
        canvas.create_oval(275, 195, 325, 245, fill="#ecf0f1", outline="#bdc3c7", width=2)
        canvas.create_text(300, 220, text="太极", font=("宋体", 10, "bold"), fill="#2c3e50")
        
        # 如果游戏已开始，绘制影响力标记
        if self.game_state:
            self.draw_influence_markers()
    
    def draw_influence_markers(self):
        """绘制影响力标记"""
        # 这里可以根据游戏状态绘制玩家的影响力标记
        # 暂时用简单的圆点表示
        pass
    
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
        info_frame = ttk.LabelFrame(parent, text="玩家信息", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        if self.game_state:
            current_player = self.game_state.players[self.current_player_index]
            
            # 玩家头像
            avatar_image = self.images.get("emperor_avatar", self.images.get("hermit_avatar"))
            if avatar_image:
                avatar_label = tk.Label(info_frame, image=avatar_image)
                avatar_label.pack(pady=5)
            
            # 玩家名称
            name_label = tk.Label(
                info_frame,
                text=current_player.name,
                font=("宋体", 14, "bold")
            )
            name_label.pack()
            
            # 资源信息
            resources_frame = ttk.Frame(info_frame)
            resources_frame.pack(fill=tk.X, pady=10)
            
            # 道行
            dao_frame = ttk.Frame(resources_frame)
            dao_frame.pack(fill=tk.X, pady=2)
            if "dao_xing_icon" in self.images:
                tk.Label(dao_frame, image=self.images["dao_xing_icon"]).pack(side=tk.LEFT)
            tk.Label(dao_frame, text=f"道行: {current_player.dao_xing}").pack(side=tk.LEFT, padx=5)
            
            # 气
            qi_frame = ttk.Frame(resources_frame)
            qi_frame.pack(fill=tk.X, pady=2)
            if "qi_icon" in self.images:
                tk.Label(qi_frame, image=self.images["qi_icon"]).pack(side=tk.LEFT)
            tk.Label(qi_frame, text=f"气: {current_player.qi}").pack(side=tk.LEFT, padx=5)
            
            # 诚意
            cheng_yi_frame = ttk.Frame(resources_frame)
            cheng_yi_frame.pack(fill=tk.X, pady=2)
            if "cheng_yi_icon" in self.images:
                tk.Label(cheng_yi_frame, image=self.images["cheng_yi_icon"]).pack(side=tk.LEFT)
            tk.Label(cheng_yi_frame, text=f"诚意: {current_player.cheng_yi}").pack(side=tk.LEFT, padx=5)
            
            # 影响力标记
            influence_label = tk.Label(
                info_frame,
                text=f"影响力标记: {current_player.influence_markers}",
                font=("宋体", 12)
            )
            influence_label.pack(pady=5)
            
            # 当前位置
            position_label = tk.Label(
                info_frame,
                text=f"当前位置: {current_player.position.value}",
                font=("宋体", 12)
            )
            position_label.pack(pady=5)
    
    def create_action_buttons(self, parent):
        """创建行动按钮"""
        action_frame = ttk.LabelFrame(parent, text="行动选择", padding=10)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 行动按钮
        actions = [
            ("演卦", self.action_play_card),
            ("升沉", self.action_move),
            ("布局", self.action_place_influence),
            ("研习", self.action_study),
            ("结束回合", self.end_turn)
        ]
        
        for action_name, command in actions:
            button = tk.Button(
                action_frame,
                text=action_name,
                font=("宋体", 12),
                width=12,
                command=command
            )
            button.pack(pady=2, fill=tk.X)
    
    def create_game_log(self, parent):
        """创建游戏日志"""
        log_frame = ttk.LabelFrame(parent, text="游戏日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建文本框和滚动条
        text_frame = ttk.Frame(log_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(
            text_frame,
            width=30,
            height=15,
            wrap=tk.WORD,
            state=tk.DISABLED
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
        
        # 手牌画布
        self.hand_canvas = tk.Canvas(
            hand_frame,
            height=200,
            bg="#f5f5dc"
        )
        self.hand_canvas.pack(fill=tk.X)
        
        # 绘制手牌
        self.draw_hand_cards()
    
    def draw_hand_cards(self):
        """绘制手牌"""
        if not self.game_state:
            return
        
        canvas = self.hand_canvas
        canvas.delete("all")
        
        current_player = self.game_state.players[self.current_player_index]
        hand_cards = current_player.hand
        
        # 计算卡牌位置
        card_width = 120
        card_height = 180
        spacing = 10
        start_x = 20
        
        for i, card in enumerate(hand_cards):
            x = start_x + i * (card_width + spacing)
            y = 10
            
            # 绘制卡牌背景
            canvas.create_rectangle(
                x, y, x + card_width, y + card_height,
                fill="#f5f5dc", outline="#8b4513", width=2
            )
            
            # 绘制卡牌名称
            canvas.create_text(
                x + card_width // 2, y + 20,
                text=card.name,
                font=("宋体", 12, "bold"),
                fill="#8b4513"
            )
            
            # 绘制卡牌描述
            canvas.create_text(
                x + card_width // 2, y + card_height // 2,
                text=card.description[:20] + "..." if len(card.description) > 20 else card.description,
                font=("宋体", 10),
                fill="#666666",
                width=card_width - 20
            )
            
            # 绑定点击事件
            canvas.tag_bind(
                canvas.create_rectangle(x, y, x + card_width, y + card_height, fill="", outline=""),
                "<Button-1>",
                lambda event, card_index=i: self.select_card(card_index)
            )
    
    def select_card(self, card_index: int):
        """选择卡牌"""
        if not self.game_state:
            return
        
        current_player = self.game_state.players[self.current_player_index]
        if 0 <= card_index < len(current_player.hand):
            selected_card = current_player.hand[card_index]
            self.add_log(f"选择了卡牌: {selected_card.name}")
            # 这里可以添加卡牌选择的逻辑
    
    def update_game_display(self):
        """更新游戏显示"""
        if not self.game_state:
            return
        
        # 更新当前玩家信息
        current_player = self.game_state.players[self.current_player_index]
        self.current_player_label.config(text=f"当前玩家: {current_player.name}")
        
        # 重新创建控制面板以更新玩家信息
        # 这里可以优化为只更新必要的部分
        
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
        self.add_log("选择演卦行动")
        messagebox.showinfo("行动", "演卦功能开发中...")
    
    def action_move(self):
        """升沉行动"""
        self.add_log("选择升沉行动")
        messagebox.showinfo("行动", "升沉功能开发中...")
    
    def action_place_influence(self):
        """布局行动"""
        self.add_log("选择布局行动")
        messagebox.showinfo("行动", "布局功能开发中...")
    
    def action_study(self):
        """研习行动"""
        self.add_log("选择研习行动")
        messagebox.showinfo("行动", "研习功能开发中...")
    
    def end_turn(self):
        """结束回合"""
        self.add_log(f"{self.game_state.players[self.current_player_index].name} 结束回合")
        
        # 切换到下一个玩家
        self.current_player_index = (self.current_player_index + 1) % len(self.game_state.players)
        
        # 更新显示
        self.update_game_display()
    
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
            # 这里添加保存游戏的逻辑
            messagebox.showinfo("保存", f"游戏已保存到 {filename}")
    
    def load_game(self):
        """加载游戏"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            # 这里添加加载游戏的逻辑
            messagebox.showinfo("加载", f"从 {filename} 加载游戏")
    
    def show_game_menu(self):
        """显示游戏菜单"""
        menu_window = tk.Toplevel(self.root)
        menu_window.title("游戏菜单")
        menu_window.geometry("300x200")
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
            button.pack(pady=5)
    
    def show_rules(self):
        """显示游戏规则"""
        rules_window = tk.Toplevel(self.root)
        rules_window.title("游戏规则")
        rules_window.geometry("600x400")
        
        text_widget = tk.Text(rules_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        rules_text = """
天机变 - 游戏规则

游戏目标：
通过演卦、布局、升沉等行动，在天地人三才棋盘上获得影响力，
最终达到胜利条件。

基本概念：
- 道行：代表玩家的修为和智慧
- 气：用于执行各种行动的能量
- 诚意：影响某些特殊行动的效果
- 影响力标记：在棋盘上标记控制区域

行动类型：
1. 演卦：打出手牌，获得卦牌效果
2. 升沉：在天地人三才之间移动
3. 布局：在棋盘上放置影响力标记
4. 研习：抽取新的卦牌

胜利条件：
- 达到指定的道行值
- 控制足够的棋盘区域
- 完成特定的任务目标

更多详细规则请参考游戏文档。
        """
        
        text_widget.insert(tk.END, rules_text)
        text_widget.config(state=tk.DISABLED)
    
    def show_yijing_guide(self):
        """显示易经指南"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("易经知识")
        guide_window.geometry("600x400")
        
        text_widget = tk.Text(guide_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        guide_text = """
易经知识指南

八卦基础：
乾☰ - 天，代表刚健、创造
坤☷ - 地，代表柔顺、承载
震☳ - 雷，代表动、奋起
巽☴ - 风，代表入、顺从
坎☵ - 水，代表险、智慧
离☲ - 火，代表明、美丽
艮☶ - 山，代表止、稳重
兑☱ - 泽，代表悦、交流

三才理论：
天 - 代表理想、精神层面
人 - 代表现实、社会层面  
地 - 代表物质、基础层面

阴阳理论：
阴阳相互依存、相互转化
阴爻 ⚋ 代表柔、静、退
阳爻 ⚊ 代表刚、动、进

五行相生相克：
金生水，水生木，木生火，火生土，土生金
金克木，木克土，土克水，水克火，火克金
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
            "开发：AI助手\n"
            "基于Python + tkinter"
        )
    
    def run(self):
        """运行游戏"""
        self.root.mainloop()

def main():
    """主函数"""
    try:
        # 检查依赖
        import cairosvg
        from PIL import Image, ImageTk
    except ImportError as e:
        print(f"缺少必要的依赖库: {e}")
        print("请安装: pip install pillow cairosvg")
        return
    
    # 创建并运行游戏
    game = GameGUI()
    game.run()

if __name__ == "__main__":
    main()