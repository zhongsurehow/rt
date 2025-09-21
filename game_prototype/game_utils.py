"""
游戏工具函数模块
提供通用的游戏功能函数，提高代码复用性和可维护性
"""

import random
import time
from typing import List, Dict, Any, Optional, Tuple
from game_state import GameState, Player
from config_manager import ConfigManager

def format_game_header(title: str, subtitle: str = "") -> str:
    """格式化游戏标题"""
    lines = [
        "🌟 " + title,
        "=" * 50
    ]
    if subtitle:
        lines.append(subtitle)
    return "\n".join(lines)

def format_player_info(player: Player, show_detailed: bool = True) -> str:
    """格式化玩家信息显示"""
    info_lines = [f"👤 {player.name}"]
    
    if show_detailed:
        info_lines.extend([
            f"⚡ 气: {player.qi}",
            f"🌟 道行: {player.dao_xing}",
            f"💫 诚意: {player.cheng_yi}",
            f"🃏 手牌数: {len(player.hand)}"
        ])
    else:
        info_lines.append(f"⚡{player.qi} 🌟{player.dao_xing} 💫{player.cheng_yi} 🃏{len(player.hand)}")
    
    return " | ".join(info_lines) if not show_detailed else "\n".join(info_lines)

def format_season_info(season_data: Dict[str, Any]) -> str:
    """格式化季节信息"""
    season_icons = {
        "春": "🌸",
        "夏": "☀️", 
        "秋": "🍂",
        "冬": "❄️"
    }
    
    season = season_data.get('season', '春')
    icon = season_icons.get(season, "🌸")
    effect = season_data.get('special_effect', '')
    
    return f"{icon} {season}季 - {effect}"

def get_user_choice(prompt: str, valid_choices: List[str], case_sensitive: bool = False) -> str:
    """获取用户选择，带输入验证"""
    if not case_sensitive:
        valid_choices_lower = [choice.lower() for choice in valid_choices]
    
    while True:
        choice = input(prompt).strip()
        
        if not case_sensitive:
            choice_lower = choice.lower()
            if choice_lower in valid_choices_lower:
                # 返回原始格式的选择
                return valid_choices[valid_choices_lower.index(choice_lower)]
        else:
            if choice in valid_choices:
                return choice
        
        print(f"❌ 无效选择，请选择: {', '.join(valid_choices)}")

def get_user_number(prompt: str, min_val: int, max_val: int) -> int:
    """获取用户输入的数字，带范围验证"""
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"❌ 数字必须在{min_val}-{max_val}之间")
        except ValueError:
            print("❌ 请输入有效的数字")

def simulate_ai_thinking(duration: float = 1.0, show_dots: bool = True) -> None:
    """模拟AI思考过程"""
    if show_dots:
        print("🤖 AI思考中", end="", flush=True)
        for _ in range(3):
            time.sleep(duration / 3)
            print(".", end="", flush=True)
        print()
    else:
        time.sleep(duration)

def calculate_combo_bonus(combo_count: int, base_bonus: int = 2) -> int:
    """计算连招奖励"""
    if combo_count <= 1:
        return 0
    
    # 连招奖励递增，但有上限
    bonus = base_bonus * combo_count
    max_bonus = base_bonus * 5  # 最大5倍奖励
    
    return min(bonus, max_bonus)

def generate_strategy_hint(player: Player, game_state: GameState, config: ConfigManager) -> str:
    """生成策略提示"""
    hints = []
    
    # 资源状态提示
    if player.qi < 3:
        hints.append("💡 气不足，考虑使用恢复类卡牌")
    
    if player.dao_xing < 5:
        hints.append("💡 道行较低，专注于修炼提升")
    
    # 手牌数量提示
    if len(player.hand) > 8:
        hints.append("💡 手牌较多，可以考虑积极出牌")
    elif len(player.hand) < 3:
        hints.append("💡 手牌不足，注意补充")
    
    # 胜利条件提示
    victory_threshold = config.get("victory_conditions.base_dao_xing", 100)
    if player.dao_xing >= victory_threshold * 0.8:
        hints.append("🏆 接近胜利！保持领先优势")
    
    return random.choice(hints) if hints else "💡 保持冷静，观察局势"

def format_achievement_notification(achievement_name: str, description: str, rewards: Dict[str, int]) -> str:
    """格式化成就通知"""
    lines = [
        f"🏆 获得成就: {achievement_name}",
        f"📜 {description}"
    ]
    
    if rewards:
        reward_parts = []
        for resource, amount in rewards.items():
            if amount > 0:
                icons = {"qi": "⚡", "dao_xing": "🌟", "cheng_yi": "💫", "wisdom": "🧠"}
                icon = icons.get(resource, "🎁")
                reward_parts.append(f"+{amount}{icon}")
        
        if reward_parts:
            lines.append(f"🎁 奖励: {' '.join(reward_parts)}")
    
    return "\n".join(lines)

def validate_card_play(player: Player, card_name: str, game_state: GameState) -> Tuple[bool, str]:
    """验证卡牌是否可以出牌"""
    # 检查玩家是否有这张卡
    if card_name not in [card.name for card in player.hand]:
        return False, "❌ 您没有这张卡牌"
    
    # 检查资源是否足够（这里可以根据具体卡牌需求扩展）
    # 基础检查：是否有足够的气
    if player.qi < 1:
        return False, "❌ 气不足，无法出牌"
    
    return True, "✅ 可以出牌"

def calculate_seasonal_bonus(season: str, card_type: str, base_value: int) -> int:
    """计算季节性奖励"""
    seasonal_multipliers = {
        "春": {"生长": 1.5, "恢复": 1.2},
        "夏": {"攻击": 1.3, "活力": 1.4},
        "秋": {"收获": 1.6, "智慧": 1.3},
        "冬": {"防御": 1.4, "沉思": 1.5}
    }
    
    multiplier = seasonal_multipliers.get(season, {}).get(card_type, 1.0)
    return int(base_value * multiplier)

def format_game_summary(game_state: GameState, winner: Optional[Player] = None) -> str:
    """格式化游戏总结"""
    lines = [
        "🎮 游戏结束",
        "=" * 30
    ]
    
    if winner:
        lines.append(f"🏆 获胜者: {winner.name}")
        lines.append(f"🌟 最终道行: {winner.dao_xing}")
    
    lines.append("\n📊 最终排名:")
    sorted_players = sorted(game_state.players, key=lambda p: p.dao_xing, reverse=True)
    
    for i, player in enumerate(sorted_players, 1):
        rank_icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        lines.append(f"{rank_icon} {player.name}: 道行{player.dao_xing}")
    
    return "\n".join(lines)

def get_random_wisdom_quote() -> str:
    """获取随机的易经智慧语录"""
    quotes = [
        "天行健，君子以自强不息",
        "地势坤，君子以厚德载物", 
        "穷则变，变则通，通则久",
        "一阴一阳之谓道",
        "知者不惑，仁者不忧，勇者不惧",
        "君子藏器于身，待时而动",
        "同声相应，同气相求",
        "积善之家，必有余庆"
    ]
    
    return f"💭 {random.choice(quotes)}"

def create_progress_bar(current: int, maximum: int, width: int = 20) -> str:
    """创建进度条"""
    if maximum <= 0:
        return "█" * width
    
    filled = int((current / maximum) * width)
    bar = "█" * filled + "░" * (width - filled)
    percentage = int((current / maximum) * 100)
    
    return f"[{bar}] {percentage}%"