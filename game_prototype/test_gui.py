#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天机变 - GUI测试程序
简单的界面测试，验证基本功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os

class TestGameGUI:
    """测试版游戏界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("天机变 - 测试版")
        self.root.geometry("800x600")
        self.root.configure(bg="#f5f5dc")
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        # 标题
        title_label = tk.Label(
            self.root,
            text="天机变 - 易经策略游戏",
            font=("华文行楷", 32, "bold"),
            fg="#8b4513",
            bg="#f5f5dc"
        )
        title_label.pack(pady=30)
        
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 左侧：游戏棋盘
        board_frame = ttk.LabelFrame(main_frame, text="天地人三才棋盘", padding=10)
        board_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 棋盘画布
        self.canvas = tk.Canvas(
            board_frame,
            width=400,
            height=300,
            bg="#fff8dc",
            relief=tk.RAISED,
            borderwidth=2
        )
        self.canvas.pack()
        
        # 绘制简单棋盘
        self.draw_board()
        
        # 右侧：控制面板
        control_frame = ttk.LabelFrame(main_frame, text="游戏控制", padding=10)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 玩家信息
        info_frame = ttk.LabelFrame(control_frame, text="玩家信息", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(info_frame, text="玩家: 测试玩家", font=("宋体", 12)).pack(anchor=tk.W)
        tk.Label(info_frame, text="道行: 5", font=("宋体", 12)).pack(anchor=tk.W)
        tk.Label(info_frame, text="气: 3", font=("宋体", 12)).pack(anchor=tk.W)
        tk.Label(info_frame, text="诚意: 2", font=("宋体", 12)).pack(anchor=tk.W)
        
        # 行动按钮
        action_frame = ttk.LabelFrame(control_frame, text="行动选择", padding=10)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        actions = [
            ("演卦", "#ff6b6b", self.test_action),
            ("升沉", "#4ecdc4", self.test_action),
            ("布局", "#45b7d1", self.test_action),
            ("研习", "#96ceb4", self.test_action)
        ]
        
        for text, color, command in actions:
            btn = tk.Button(
                action_frame,
                text=text,
                font=("宋体", 12),
                bg=color,
                fg="white",
                width=10,
                command=lambda t=text: command(t)
            )
            btn.pack(pady=3, fill=tk.X)
        
        # 手牌区域
        hand_frame = ttk.LabelFrame(control_frame, text="手牌", padding=10)
        hand_frame.pack(fill=tk.BOTH, expand=True)
        
        # 示例手牌
        cards = ["乾卦", "坤卦", "震卦"]
        for i, card in enumerate(cards):
            card_btn = tk.Button(
                hand_frame,
                text=f"{card}\n(示例卡牌)",
                font=("宋体", 10),
                width=12,
                height=3,
                bg="#ffe4b5",
                command=lambda c=card: self.select_card(c)
            )
            card_btn.pack(pady=2, fill=tk.X)
        
        # 底部状态栏
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="游戏界面测试 - 所有功能正常",
            font=("宋体", 11),
            fg="#666666",
            bg="#f5f5dc"
        )
        self.status_label.pack(side=tk.LEFT)
        
        # 检查资源按钮
        check_btn = tk.Button(
            status_frame,
            text="检查资源",
            font=("宋体", 10),
            command=self.check_assets
        )
        check_btn.pack(side=tk.RIGHT)
    
    def draw_board(self):
        """绘制棋盘"""
        canvas = self.canvas
        
        # 绘制三个区域
        # 天区域
        canvas.create_rectangle(20, 20, 380, 100, fill="#87ceeb", outline="#4682b4", width=2)
        canvas.create_text(200, 60, text="天", font=("华文行楷", 18, "bold"))
        
        # 人区域
        canvas.create_rectangle(20, 110, 380, 190, fill="#98fb98", outline="#228b22", width=2)
        canvas.create_text(200, 150, text="人", font=("华文行楷", 18, "bold"))
        
        # 地区域
        canvas.create_rectangle(20, 200, 380, 280, fill="#deb887", outline="#8b7355", width=2)
        canvas.create_text(200, 240, text="地", font=("华文行楷", 18, "bold"))
        
        # 绘制八卦位置
        gua_positions = [
            (80, 60, "乾"), (320, 60, "离"),
            (80, 150, "兑"), (320, 150, "震"),
            (80, 240, "坤"), (320, 240, "坎"),
            (200, 60, "艮"), (200, 240, "巽")
        ]
        
        for x, y, gua in gua_positions:
            canvas.create_oval(x-12, y-12, x+12, y+12, fill="#daa520", outline="black")
            canvas.create_text(x, y, text=gua, font=("宋体", 9, "bold"), fill="white")
    
    def test_action(self, action_name):
        """测试行动"""
        self.status_label.config(text=f"执行行动: {action_name}")
        messagebox.showinfo("行动", f"执行了 {action_name} 行动")
    
    def select_card(self, card_name):
        """选择卡牌"""
        self.status_label.config(text=f"选择了卡牌: {card_name}")
        messagebox.showinfo("卡牌", f"选择了 {card_name}")
    
    def check_assets(self):
        """检查资源文件"""
        assets_path = "assets"
        if os.path.exists(assets_path):
            # 检查各个子文件夹
            folders = ["cards", "ui", "icons"]
            found_files = []
            
            for folder in folders:
                folder_path = os.path.join(assets_path, folder)
                if os.path.exists(folder_path):
                    files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]
                    found_files.extend([f"{folder}/{f}" for f in files])
            
            if found_files:
                file_list = "\n".join(found_files)
                messagebox.showinfo("资源检查", f"找到以下资源文件:\n\n{file_list}")
            else:
                messagebox.showwarning("资源检查", "未找到SVG资源文件")
        else:
            messagebox.showerror("资源检查", "assets文件夹不存在")
    
    def run(self):
        """运行程序"""
        self.root.mainloop()

def main():
    """主函数"""
    app = TestGameGUI()
    app.run()

if __name__ == "__main__":
    main()