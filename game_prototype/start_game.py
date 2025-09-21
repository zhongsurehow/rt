#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天机变 - 游戏启动器
选择不同版本的游戏界面
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

class GameLauncher:
    """游戏启动器"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("天机变 - 游戏启动器")
        self.root.geometry("400x300")
        self.root.configure(bg="#f5f5dc")
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        # 标题
        title_label = tk.Label(
            self.root,
            text="天机变",
            font=("华文行楷", 32, "bold"),
            fg="#8b4513",
            bg="#f5f5dc"
        )
        title_label.pack(pady=30)
        
        subtitle_label = tk.Label(
            self.root,
            text="易经主题策略游戏",
            font=("宋体", 14),
            fg="#666666",
            bg="#f5f5dc"
        )
        subtitle_label.pack(pady=10)
        
        # 按钮框架
        button_frame = tk.Frame(self.root, bg="#f5f5dc")
        button_frame.pack(pady=40)
        
        # 游戏版本选择
        versions = [
            ("完整版GUI", "simple_gui_game.py", "包含完整游戏逻辑的图形界面"),
            ("测试版GUI", "test_gui.py", "简化的界面测试版本"),
            ("命令行版", "main.py", "原始的命令行游戏版本")
        ]
        
        for name, script, desc in versions:
            btn = tk.Button(
                button_frame,
                text=name,
                font=("宋体", 12),
                width=15,
                height=2,
                bg="#daa520",
                fg="white",
                command=lambda s=script, n=name: self.launch_game(s, n)
            )
            btn.pack(pady=8)
            
            desc_label = tk.Label(
                button_frame,
                text=desc,
                font=("宋体", 9),
                fg="#666666",
                bg="#f5f5dc"
            )
            desc_label.pack(pady=(0, 10))
        
        # 退出按钮
        quit_btn = tk.Button(
            button_frame,
            text="退出",
            font=("宋体", 12),
            width=15,
            height=1,
            bg="#cd853f",
            fg="white",
            command=self.root.quit
        )
        quit_btn.pack(pady=20)
    
    def launch_game(self, script_name, game_name):
        """启动游戏"""
        if not os.path.exists(script_name):
            messagebox.showerror("错误", f"找不到游戏文件: {script_name}")
            return
        
        try:
            # 启动游戏
            subprocess.Popen([sys.executable, script_name])
            messagebox.showinfo("启动", f"{game_name} 已启动！")
        except Exception as e:
            messagebox.showerror("错误", f"启动游戏失败: {e}")
    
    def run(self):
        """运行启动器"""
        self.root.mainloop()

def main():
    """主函数"""
    launcher = GameLauncher()
    launcher.run()

if __name__ == "__main__":
    main()