"""
架构适配器 - 整合新的数据驱动、事件总线和策略模式系统
确保新架构与现有系统的向后兼容性
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path

# 导入新架构组件
try:
    from .effect_engine import EffectEngine, GameState as EffectGameState
    from .event_bus import get_event_bus, emit, on, GameEvents
    from .strategy_patterns import (
        get_strategy_manager, 
        GameStateData as StrategyGameState, PlayerData as PlayerState,
        Difficulty
    )
    NEW_ARCHITECTURE_AVAILABLE = True
except ImportError:
    NEW_ARCHITECTURE_AVAILABLE = False

class ArchitectureAdapter:
    """架构适配器 - 整合所有新系统"""
    
    def __init__(self, game_data_path: str = None):
        """初始化适配器"""
        self.logger = logging.getLogger(__name__)
        
        # 设置数据路径
        if game_data_path is None:
            current_dir = Path(__file__).parent.parent
            game_data_path = current_dir / "data"
        
        self.data_path = Path(game_data_path)
        
        # 初始化各个系统
        self.effect_engine = None
        self.event_bus = get_event_bus()
        self.strategy_manager = get_strategy_manager() if NEW_ARCHITECTURE_AVAILABLE else None
        
        # 兼容性映射
        self.legacy_mappings = {}
        
        # 初始化系统
        self._initialize_systems()
        self._setup_event_listeners()
        self._load_legacy_mappings()
    
    def _initialize_systems(self):
        """初始化各个系统"""
        try:
            # 初始化效果引擎
            self.effect_engine = EffectEngine(str(self.data_path))
            self.logger.info("效果引擎初始化成功")
            
            # 发送系统初始化事件
            emit(GameEvents.SYSTEM_INITIALIZED, {
                "system": "architecture_adapter",
                "components": ["effect_engine", "event_bus", "strategy_manager"]
            })
            
        except Exception as e:
            self.logger.error(f"系统初始化失败: {e}")
            # 创建默认的效果引擎
            self.effect_engine = EffectEngine()
    
    def _setup_event_listeners(self):
        """设置事件监听器"""
        # 监听游戏状态变化
        on(GameEvents.GAME_STATE_CHANGED, self._on_game_state_changed)
        on(GameEvents.PLAYER_ACTION, self._on_player_action)
        on(GameEvents.CARD_PLAYED, self._on_card_played)
        on(GameEvents.TURN_STARTED, self._on_turn_started)
        on(GameEvents.VICTORY_ACHIEVED, self._on_victory_achieved)
    
    def _load_legacy_mappings(self):
        """加载遗留系统映射"""
        mapping_file = self.data_path / "legacy_mappings.json"
        
        if mapping_file.exists():
            try:
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    self.legacy_mappings = json.load(f)
                self.logger.info("遗留系统映射加载成功")
            except Exception as e:
                self.logger.warning(f"遗留系统映射加载失败: {e}")
        else:
            # 创建默认映射
            self._create_default_mappings()
    
    def _create_default_mappings(self):
        """创建默认的遗留系统映射"""
        self.legacy_mappings = {
            "card_mappings": {
                # 旧卡牌名称到新卡牌ID的映射
                "乾为天": "qian_card",
                "坤为地": "kun_card",
                "震为雷": "zhen_card",
                "巽为风": "xun_card",
                "坎为水": "kan_card",
                "离为火": "li_card",
                "艮为山": "gen_card",
                "兑为泽": "dui_card"
            },
            "attribute_mappings": {
                # 旧属性名到新属性名的映射
                "生命值": "health",
                "能量": "energy",
                "道值": "dao",
                "阳气": "yang",
                "阴气": "yin",
                "智慧": "wisdom",
                "运气": "luck"
            },
            "action_mappings": {
                # 旧行动类型到新行动类型的映射
                "使用卡牌": "play_card",
                "结束回合": "end_turn",
                "跳过": "pass",
                "投降": "surrender"
            }
        }
        
        # 保存默认映射
        try:
            mapping_file = self.data_path / "legacy_mappings.json"
            mapping_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.legacy_mappings, f, ensure_ascii=False, indent=2)
            
            self.logger.info("默认遗留系统映射已创建")
        except Exception as e:
            self.logger.warning(f"无法保存默认映射: {e}")
    
    # ==================== 事件处理器 ====================
    
    def _on_game_state_changed(self, event_data: Dict[str, Any]):
        """处理游戏状态变化事件"""
        self.logger.debug(f"游戏状态变化: {event_data}")
        
        # 检查胜利条件
        if "game_state" in event_data:
            self._check_victory_conditions(event_data["game_state"])
    
    def _on_player_action(self, event_data: Dict[str, Any]):
        """处理玩家行动事件"""
        self.logger.debug(f"玩家行动: {event_data}")
        
        # 记录行动历史
        player_id = event_data.get("player_id")
        action = event_data.get("action")
        
        if player_id and action:
            emit(GameEvents.ACTION_RECORDED, {
                "player_id": player_id,
                "action": action,
                "timestamp": event_data.get("timestamp")
            })
    
    def _on_card_played(self, event_data: Dict[str, Any]):
        """处理卡牌使用事件"""
        self.logger.debug(f"卡牌使用: {event_data}")
        
        # 执行卡牌效果
        if self.effect_engine:
            try:
                card_id = event_data.get("card_id")
                player_id = event_data.get("player_id")
                target_id = event_data.get("target_id")
                game_state = event_data.get("game_state")
                
                if card_id and game_state:
                    # 转换游戏状态格式
                    effect_game_state = self._convert_to_effect_game_state(game_state)
                    
                    # 执行效果
                    result = self.effect_engine.execute_card_effect(
                        card_id, player_id, target_id, effect_game_state
                    )
                    
                    # 发送效果执行结果事件
                    emit(GameEvents.EFFECT_EXECUTED, {
                        "card_id": card_id,
                        "player_id": player_id,
                        "target_id": target_id,
                        "result": result.value if hasattr(result, 'value') else str(result),
                        "game_state": effect_game_state
                    })
                    
            except Exception as e:
                self.logger.error(f"卡牌效果执行失败: {e}")
    
    def _on_turn_started(self, event_data: Dict[str, Any]):
        """处理回合开始事件"""
        self.logger.debug(f"回合开始: {event_data}")
        
        # AI决策
        current_player = event_data.get("current_player")
        game_state = event_data.get("game_state")
        
        if current_player and game_state:
            self._handle_ai_turn(current_player, game_state)
    
    def _on_victory_achieved(self, event_data: Dict[str, Any]):
        """处理胜利达成事件"""
        self.logger.info(f"胜利达成: {event_data}")
        
        # 记录胜利信息
        winner = event_data.get("winner")
        victory_type = event_data.get("victory_type")
        
        if winner and victory_type:
            emit(GameEvents.GAME_ENDED, {
                "winner": winner,
                "victory_type": victory_type,
                "game_duration": event_data.get("game_duration"),
                "final_state": event_data.get("final_state")
            })
    
    # ==================== 兼容性接口 ====================
    
    def convert_legacy_card_name(self, legacy_name: str) -> str:
        """转换遗留卡牌名称"""
        return self.legacy_mappings.get("card_mappings", {}).get(legacy_name, legacy_name)
    
    def convert_legacy_attribute(self, legacy_attr: str) -> str:
        """转换遗留属性名称"""
        return self.legacy_mappings.get("attribute_mappings", {}).get(legacy_attr, legacy_attr)
    
    def convert_legacy_action(self, legacy_action: str) -> str:
        """转换遗留行动类型"""
        return self.legacy_mappings.get("action_mappings", {}).get(legacy_action, legacy_action)
    
    def execute_legacy_card_effect(self, card_name: str, player_data: Dict, target_data: Dict = None) -> Dict[str, Any]:
        """执行遗留卡牌效果（兼容接口）"""
        try:
            # 转换卡牌名称
            card_id = self.convert_legacy_card_name(card_name)
            
            # 转换玩家数据
            player_id = player_data.get("id", "player1")
            
            # 创建简化的游戏状态
            game_state = EffectGameState(
                players={player_id: player_data},
                current_player=player_id
            )
            
            # 执行效果
            if self.effect_engine:
                result = self.effect_engine.execute_card_effect(
                    card_id, player_id, 
                    target_data.get("id") if target_data else None,
                    game_state
                )
                
                return {
                    "success": True,
                    "result": result.value if hasattr(result, 'value') else str(result),
                    "updated_state": game_state
                }
            else:
                return {"success": False, "error": "效果引擎未初始化"}
                
        except Exception as e:
            self.logger.error(f"遗留卡牌效果执行失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_ai_action(self, ai_player_data: Dict, game_state_data: Dict, difficulty: str = "normal") -> Dict[str, Any]:
        """获取AI行动（兼容接口）"""
        try:
            # 转换难度
            difficulty_map = {
                "easy": Difficulty.EASY,
                "normal": Difficulty.NORMAL,
                "hard": Difficulty.HARD,
                "expert": Difficulty.EXPERT
            }
            
            ai_difficulty = difficulty_map.get(difficulty.lower(), Difficulty.NORMAL)
            
            # 获取AI策略
            strategy_name = f"balanced_{ai_difficulty.name.lower()}"
            ai_strategy = self.strategy_manager.get_ai_strategy(strategy_name)
            
            if ai_strategy:
                # 转换游戏状态
                strategy_game_state = self._convert_to_strategy_game_state(game_state_data)
                ai_player_id = ai_player_data.get("id", "ai_player")
                
                # 获取AI行动
                action = ai_strategy.choose_action(strategy_game_state, ai_player_id)
                
                return {
                    "success": True,
                    "action": action,
                    "strategy": strategy_name
                }
            else:
                return {"success": False, "error": f"AI策略 {strategy_name} 未找到"}
                
        except Exception as e:
            self.logger.error(f"AI行动获取失败: {e}")
            return {"success": False, "error": str(e)}
    
    def check_victory_conditions(self, game_state_data: Dict, player_id: str) -> Dict[str, Any]:
        """检查胜利条件（兼容接口）"""
        try:
            # 转换游戏状态
            strategy_game_state = self._convert_to_strategy_game_state(game_state_data)
            
            # 检查所有胜利条件
            victory_results = self.strategy_manager.check_all_victory_conditions(
                strategy_game_state, player_id
            )
            
            # 获取胜利进度
            victory_progress = self.strategy_manager.get_victory_progress(
                strategy_game_state, player_id
            )
            
            return {
                "success": True,
                "victory_conditions": victory_results,
                "victory_progress": victory_progress,
                "has_won": any(victory_results.values())
            }
            
        except Exception as e:
            self.logger.error(f"胜利条件检查失败: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== 内部辅助方法 ====================
    
    def _convert_to_effect_game_state(self, game_state_data: Dict) -> EffectGameState:
        """转换为效果引擎的游戏状态格式"""
        return EffectGameState(
            players=game_state_data.get("players", {}),
            current_player=game_state_data.get("current_player", ""),
            turn_number=game_state_data.get("turn_number", 1),
            game_phase=game_state_data.get("game_phase", "playing")
        )
    
    def _convert_to_strategy_game_state(self, game_state_data: Dict) -> 'StrategyGameState':
        """转换为策略模式的游戏状态格式"""
        # 转换玩家状态
        players = {}
        for player_id, player_data in game_state_data.get("players", {}).items():
            players[player_id] = PlayerState(
                player_id=player_id,
                health=player_data.get("health", 100),
                energy=player_data.get("energy", 100),
                dao=player_data.get("dao", 0),
                yang=player_data.get("yang", 0),
                yin=player_data.get("yin", 0),
                wisdom=player_data.get("wisdom", 0),
                luck=player_data.get("luck", 0),
                cards_in_hand=player_data.get("cards_in_hand", []),
                active_buffs=player_data.get("active_buffs", []),
                active_debuffs=player_data.get("active_debuffs", [])
            )
        
        return StrategyGameState(
            players=players,
            turn_number=game_state_data.get("turn_number", 1),
            current_player=game_state_data.get("current_player", ""),
            game_phase=game_state_data.get("game_phase", "playing"),
            special_conditions=game_state_data.get("special_conditions", {})
        )
    
    def _check_victory_conditions(self, game_state_data: Dict):
        """检查胜利条件"""
        for player_id in game_state_data.get("players", {}):
            victory_check = self.check_victory_conditions(game_state_data, player_id)
            
            if victory_check.get("success") and victory_check.get("has_won"):
                # 发送胜利事件
                emit(GameEvents.VICTORY_ACHIEVED, {
                    "winner": player_id,
                    "victory_conditions": victory_check.get("victory_conditions"),
                    "final_state": game_state_data
                })
    
    def _handle_ai_turn(self, ai_player_id: str, game_state_data: Dict):
        """处理AI回合"""
        ai_player_data = game_state_data.get("players", {}).get(ai_player_id)
        
        if ai_player_data and ai_player_data.get("is_ai", False):
            ai_action = self.get_ai_action(ai_player_data, game_state_data)
            
            if ai_action.get("success"):
                # 发送AI行动事件
                emit(GameEvents.AI_ACTION_DECIDED, {
                    "ai_player_id": ai_player_id,
                    "action": ai_action.get("action"),
                    "strategy": ai_action.get("strategy")
                })

# 全局适配器实例
_global_adapter = None

def get_architecture_adapter() -> ArchitectureAdapter:
    """获取全局架构适配器实例"""
    global _global_adapter
    if _global_adapter is None:
        _global_adapter = ArchitectureAdapter()
    return _global_adapter

def initialize_new_architecture(game_data_path: str = None) -> ArchitectureAdapter:
    """初始化新架构"""
    global _global_adapter
    _global_adapter = ArchitectureAdapter(game_data_path)
    return _global_adapter

# 兼容性函数 - 为现有代码提供简单的迁移路径
def execute_card_effect_legacy(card_name: str, player_data: Dict, target_data: Dict = None) -> Dict[str, Any]:
    """遗留卡牌效果执行函数"""
    adapter = get_architecture_adapter()
    return adapter.execute_legacy_card_effect(card_name, player_data, target_data)

def get_ai_decision_legacy(ai_player_data: Dict, game_state_data: Dict, difficulty: str = "normal") -> Dict[str, Any]:
    """遗留AI决策函数"""
    adapter = get_architecture_adapter()
    return adapter.get_ai_action(ai_player_data, game_state_data, difficulty)

def check_win_conditions_legacy(game_state_data: Dict, player_id: str) -> Dict[str, Any]:
    """遗留胜利条件检查函数"""
    adapter = get_architecture_adapter()
    return adapter.check_victory_conditions(game_state_data, player_id)