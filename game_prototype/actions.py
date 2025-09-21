import random
import copy
import logging
from typing import Dict, Any, Optional
from game_state import GameState, Zone, Player, AvatarName, BonusType, Modifiers
from card_base import GuaCard, YaoCiTask
from game_data import GAME_DECK, GENERIC_YAO_CI_POOL
from yijing_actions import (
    enhanced_play_card, enhanced_meditate, enhanced_study,
    biangua_transformation, wuxing_interaction, divine_fortune, consult_yijing
)
from wisdom_system import wisdom_system
from tutorial_system import tutorial_system, TutorialType
from achievement_system import achievement_system
from enhanced_cards import enhanced_card_system, CardType

# 导入优雅编程模式
from elegant_patterns import (
    ActionType, ResourceType, GamePhase, MessageType,
    require_resource, log_action, performance_monitor, 
    validate_game_state, generate_possible_moves
)

def check_zone_control(gs: GameState, zone_name: str): # This function mutates state, which is an exception to the pattern for now for simplicity.
    """Check and update zone control based on influence markers."""
    zone_data = gs.board.gua_zones[zone_name]
    markers = zone_data["markers"]
    
    if not markers:
        zone_data["controller"] = None
        return
    
    # Find player with most influence
    max_influence = max(markers.values())
    players_with_max = [player for player, influence in markers.items() if influence == max_influence]
    
    # Check if control threshold is met (simplified: need more than half of base limit)
    control_threshold = gs.board.base_limit // 2 + 1
    
    if len(players_with_max) == 1 and max_influence >= control_threshold:
        zone_data["controller"] = players_with_max[0]
    else:
        zone_data["controller"] = None

@log_action(ActionType.PLAY_CARD)
@performance_monitor(threshold_ms=50.0)
@require_resource(ResourceType.QI, 1)
def play_card(game_state: GameState, card_index: int, zone_choice: str, mods: Modifiers) -> Optional[GameState]:
    """
    打出卡牌到指定区域
    
    Args:
        game_state: 游戏状态
        card_index: 卡牌索引
        zone_choice: 目标区域
        mods: 修正值
        
    Returns:
        新的游戏状态或None（如果操作失败）
    """
    new_state = copy.deepcopy(game_state)
    player = new_state.get_current_player()
    
    # 验证卡牌索引
    if not (0 <= card_index < len(player.hand)): 
        logging.warning(f"无效的卡牌索引: {card_index}")
        return None
        
    card_to_play = player.hand.pop(card_index)
    
    # 验证区域选择
    if zone_choice not in card_to_play.associated_guas: 
        logging.warning(f"卡牌 {card_to_play.name} 不能放置在 {zone_choice} 区域")
        return None
        
    player.current_task_card = card_to_play
    influence_to_place = 1 + mods.extra_influence
    zone_markers = new_state.board.gua_zones[zone_choice]["markers"]
    zone_markers[player.name] = zone_markers.get(player.name, 0) + influence_to_place
    player.placed_influence_this_turn = True
    check_zone_control(new_state, zone_choice)
    
    # Update achievement tracking
    card_rarity = getattr(card_to_play, 'rarity', 'common')  # Default to common if no rarity
    achievement_system.on_card_played(player.name, card_rarity)
    
    logging.info(f"玩家 {player.name} 成功打出卡牌 {card_to_play.name} 到 {zone_choice}")
    return new_state

@log_action(ActionType.MOVE)
@performance_monitor(threshold_ms=30.0)
@require_resource(ResourceType.ACTION_POINTS, 1)
def move(game_state: GameState, target_zone_str: str, mods: Modifiers) -> Optional[GameState]:
    """
    移动到指定区域
    
    Args:
        game_state: 游戏状态
        target_zone_str: 目标区域名称
        mods: 修正值
        
    Returns:
        新的游戏状态或None（如果操作失败）
    """
    new_state = copy.deepcopy(game_state)
    player = new_state.get_current_player()
    
    # Convert string to Zone enum
    try:
        target_zone = Zone(target_zone_str)
    except ValueError:
        logging.warning(f"无效的区域名称: {target_zone_str}")
        return None
    
    # 验证移动目标
    if player.position == target_zone:
        logging.warning(f"玩家 {player.name} 已在 {target_zone.value} 区域")
        return None
    
    # Check if player has enough Qi
    qi_cost = max(1 - mods.qi_discount, 0)
    if player.qi < qi_cost:
        logging.warning(f"玩家 {player.name} 气不足，需要 {qi_cost}")
        return None
    
    # Move player
    player.position = target_zone
    player.qi -= qi_cost
    player.moved_this_turn = True
    new_state.board.player_positions[player.name] = target_zone
    
    logging.info(f"玩家 {player.name} 移动到 {target_zone.value}")
    return new_state

@log_action(ActionType.STUDY)
@performance_monitor(threshold_ms=40.0)
@require_resource(ResourceType.QI, 1)
def study(game_state: GameState, mods: Modifiers) -> Optional[GameState]:
    """
    学习行动，消耗气获得诚意
    
    Args:
        game_state: 游戏状态
        mods: 修正值
        
    Returns:
        新的游戏状态或None（如果操作失败）
    """
    new_state = copy.deepcopy(game_state)
    player = new_state.get_current_player()
    
    qi_cost = max(1 - mods.qi_discount, 0)
    if player.qi < qi_cost: 
        logging.warning(f"玩家 {player.name} 气不足，需要 {qi_cost}")
        return None
        
    player.qi -= qi_cost
    player.cheng_yi += 1
    player.studied_this_turn = True
    
    # Update achievement tracking
    achievement_system.on_study_action(player.name)
    
    logging.info(f"玩家 {player.name} 学习获得诚意，当前诚意: {player.cheng_yi}")
    return new_state

@log_action(ActionType.MEDITATE)
@performance_monitor(threshold_ms=40.0)
def meditate(game_state: GameState, mods: Modifiers) -> GameState:
    """
    冥想行动，获得气并可能触发智慧
    
    Args:
        game_state: 游戏状态
        mods: 修正值
        
    Returns:
        新的游戏状态
    """
    new_state = copy.deepcopy(game_state)
    current_player = new_state.get_current_player()
    
    # Base Qi gain with modifiers
    qi_gain = 2 + mods.extra_qi_gain
    
    # Position-based bonuses
    if current_player.position == Zone.TIAN:  # Heaven realm bonus for meditation
        qi_gain += 1
    elif current_player.position == Zone.DI:  # Earth realm provides stability
        qi_gain += 1
    
    current_player.qi += qi_gain
    
    # Cheng Yi bonus for deep meditation
    if current_player.cheng_yi >= 3:
        current_player.qi += 1  # Extra Qi for experienced practitioners
    
    # Check for wisdom triggers
    triggered_quotes = wisdom_system.check_wisdom_triggers(current_player, "meditate", {})
    for quote in triggered_quotes:
        wisdom_system.display_wisdom_activation(quote)
        wisdom_system.apply_wisdom_effects(current_player, quote)
    
    # Update achievement tracking
    achievement_system.on_meditation(current_player.name)
    
    logging.info(f"玩家 {current_player.name} 冥想获得 {qi_gain} 气，当前气: {current_player.qi}")
    return new_state

@performance_monitor(threshold_ms=100.0)
def get_valid_actions(game_state: GameState, player: Player, ap: int, mods: Modifiers, **flags) -> Dict[int, Dict[str, Any]]:
    """
    获取当前玩家的所有有效行动
    
    Args:
        game_state: 游戏状态
        player: 当前玩家
        ap: 行动点数
        mods: 修正值
        
    Returns:
        行动字典，键为行动ID，值为行动信息
    """
    actions = {}
    action_id = 1
    
    # 使用生成器获取可能的行动
    for action_info in generate_possible_moves(game_state):
        actions[action_id] = action_info
        action_id += 1
    
    # Always allow pass action
    actions[action_id] = {
        "action": "pass",
        "cost": 0,
        "description": "Pass (结束回合) [空]",
        "args": []
    }
    action_id += 1
    
    # Enhanced play card actions (with Yijing effects)
    for i, card in enumerate(player.hand):
        if ap >= 1:  # Playing a card costs 1 AP
            for gua in card.associated_guas:
                actions[action_id] = {
                    "action": enhanced_play_card,
                    "cost": 1,
                    "description": f"Play {card.name} to {gua} [阴阳]",
                    "args": [i, gua]
                }
                action_id += 1
    
    # Move action
    if ap >= 1 and player.qi >= 1:  # Moving costs 1 AP and 1 Qi
        for zone in Zone:
            if zone != player.position:
                actions[action_id] = {
                    "action": move,
                    "cost": 1,
                    "description": f"Move to {zone.value}",
                    "args": [zone.value]
                }
                action_id += 1
    
    # Enhanced study action (with Yijing wisdom)
    if ap >= 1:
        actions[action_id] = {
            "action": enhanced_study,
            "cost": 1,
            "description": "Study (draw cards, gain wisdom) [书]",
            "args": []
        }
        action_id += 1
    
    # Enhanced meditate action (with Yijing cultivation)
    if ap >= 1:
        actions[action_id] = {
            "action": enhanced_meditate,
            "cost": 1,
            "description": "Meditate (cultivate Qi, balance Yin-Yang) 🧘",
            "args": []
        }
        action_id += 1
    
    # Biangua transformation (change hexagram)
    if ap >= 1 and player.cheng_yi >= 3:
        actions[action_id] = {
            "action": "biangua_prompt",
            "cost": 1,
            "description": "Biangua (transform hexagram) 🔄",
            "args": []
        }
        action_id += 1
    
    # Divine fortune (占卜运势)
    if ap >= 1 and player.qi >= 3:
        actions[action_id] = {
            "action": divine_fortune,
            "cost": 1,
            "description": "Divine Fortune (占卜运势) 🔮",
            "args": []
        }
        action_id += 1
    
    # View wisdom progress (no cost)
    actions[action_id] = {
        "action": "wisdom_progress",
        "cost": 0,
        "description": "View Wisdom Progress (查看智慧收集进度) [卷]",
        "args": []
    }
    action_id += 1
    
    # Tutorial system actions (no cost)
    actions[action_id] = {
        "action": "tutorial_menu",
        "cost": 0,
        "description": "Tutorial Menu (教学菜单) 🎓",
        "args": []
    }
    action_id += 1
    
    actions[action_id] = {
        "action": "learning_progress",
        "cost": 0,
        "description": "Learning Progress (学习进度) [统计]",
        "args": []
    }
    action_id += 1
    
    # Achievement system actions (no cost)
    actions[action_id] = {
        "action": "achievement_progress",
        "cost": 0,
        "description": "Achievement Progress (成就进度) 🏆",
        "args": []
    }
    action_id += 1
    
    actions[action_id] = {
        "action": "achievement_list",
        "cost": 0,
        "description": "Achievement List (成就列表) [目标]",
        "args": []
    }
    action_id += 1
    
    # Enhanced card system actions
    actions[action_id] = {
        "action": "view_enhanced_cards",
        "cost": 0,
        "description": "View Enhanced Cards (查看增强卡牌) [卡牌]",
        "args": []
    }
    action_id += 1
    
    if ap >= 1:
        actions[action_id] = {
            "action": "use_enhanced_card",
            "cost": 1,
            "description": "Use Enhanced Card (使用增强卡牌) [闪]",
            "args": []
        }
        action_id += 1
    
    # Consult Yijing for guidance
    if ap >= 1 and player.dao_xing >= 2:
        actions[action_id] = {
            "action": "consult_yijing_prompt",
            "cost": 1,
            "description": "Consult Yijing (咨询易经) [卷]",
            "args": []
        }
        action_id += 1
    
    return actions
