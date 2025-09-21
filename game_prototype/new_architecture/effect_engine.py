"""
通用效果执行器 - 数据驱动的卡牌效果系统
基于JSON配置文件执行各种游戏效果，实现逻辑与内容的分离
"""

import json
import os
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import random

class EffectResult(Enum):
    """效果执行结果"""
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    PARTIAL = "partial"

@dataclass
class GameState:
    """游戏状态数据结构"""
    player_attributes: Dict[str, int]
    opponent_attributes: Dict[str, int]
    player_hand: List[str]
    opponent_hand: List[str]
    turn_number: int
    active_buffs: List[Dict]
    active_debuffs: List[Dict]
    shields: Dict[str, int]
    
class EffectEngine:
    """通用效果执行器"""
    
    def __init__(self, data_path: str = "data"):
        """初始化效果引擎"""
        self.data_path = data_path
        self.effects_config = self._load_effects_config()
        self.cards_config = self._load_cards_config()
        self.hexagrams_config = self._load_hexagrams_config()
        
        # 效果执行器映射
        self.effect_handlers = {
            "MODIFY_ATTRIBUTE": self._handle_modify_attribute,
            "DRAW_CARDS": self._handle_draw_cards,
            "HEAL": self._handle_heal,
            "DAMAGE": self._handle_damage,
            "SHIELD": self._handle_shield,
            "BUFF": self._handle_buff,
            "DEBUFF": self._handle_debuff,
            "TRANSFORM": self._handle_transform,
            "SPECIAL_ACTION": self._handle_special_action,
            "CONDITIONAL": self._handle_conditional
        }
        
    def _load_effects_config(self) -> Dict:
        """加载效果配置"""
        try:
            with open(os.path.join(self.data_path, "effects.json"), 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("警告：未找到effects.json配置文件")
            return {}
    
    def _load_cards_config(self) -> Dict:
        """加载卡牌配置"""
        try:
            with open(os.path.join(self.data_path, "cards.json"), 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("警告：未找到cards.json配置文件")
            return {}
    
    def _load_hexagrams_config(self) -> Dict:
        """加载卦象配置"""
        try:
            with open(os.path.join(self.data_path, "hexagrams.json"), 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("警告：未找到hexagrams.json配置文件")
            return {}
    
    def execute_card_effects(self, card_id: str, game_state: GameState, 
                           caster: str = "player") -> List[Dict]:
        """执行卡牌效果"""
        if card_id not in self.cards_config.get("cards", {}):
            return [{"result": EffectResult.FAILED, "message": f"未知卡牌: {card_id}"}]
        
        card_data = self.cards_config["cards"][card_id]
        effects = card_data.get("effects", [])
        
        results = []
        for effect in effects:
            result = self.execute_effect(effect, game_state, caster)
            results.append(result)
            
            # 如果有效果失败且是必需的，停止执行后续效果
            if result["result"] == EffectResult.FAILED and effect.get("required", True):
                break
                
        return results
    
    def execute_effect(self, effect: Dict, game_state: GameState, 
                      caster: str = "player") -> Dict:
        """执行单个效果"""
        effect_type = effect.get("type")
        
        if effect_type not in self.effect_handlers:
            return {
                "result": EffectResult.FAILED,
                "message": f"未知效果类型: {effect_type}"
            }
        
        # 验证效果参数
        validation_result = self._validate_effect_parameters(effect)
        if not validation_result["valid"]:
            return {
                "result": EffectResult.FAILED,
                "message": f"参数验证失败: {validation_result['message']}"
            }
        
        # 检查前置条件
        if not self._check_conditions(effect, game_state):
            return {
                "result": EffectResult.BLOCKED,
                "message": "前置条件不满足"
            }
        
        # 执行效果
        try:
            handler = self.effect_handlers[effect_type]
            return handler(effect, game_state, caster)
        except Exception as e:
            return {
                "result": EffectResult.FAILED,
                "message": f"效果执行异常: {str(e)}"
            }
    
    def _validate_effect_parameters(self, effect: Dict) -> Dict:
        """验证效果参数"""
        effect_type = effect.get("type")
        if effect_type not in self.effects_config.get("effect_types", {}):
            return {"valid": False, "message": f"未知效果类型: {effect_type}"}
        
        type_config = self.effects_config["effect_types"][effect_type]
        parameters = type_config.get("parameters", {})
        
        for param_name, param_config in parameters.items():
            if param_config.get("required", False) and param_name not in effect:
                return {"valid": False, "message": f"缺少必需参数: {param_name}"}
            
            if param_name in effect:
                value = effect[param_name]
                
                # 类型检查
                expected_type = param_config.get("type")
                if expected_type == "number" and not isinstance(value, (int, float)):
                    return {"valid": False, "message": f"参数{param_name}应为数字"}
                elif expected_type == "string" and not isinstance(value, str):
                    return {"valid": False, "message": f"参数{param_name}应为字符串"}
                
                # 值范围检查
                if "valid_values" in param_config and value not in param_config["valid_values"]:
                    return {"valid": False, "message": f"参数{param_name}值无效"}
                
                if "min" in param_config and value < param_config["min"]:
                    return {"valid": False, "message": f"参数{param_name}值过小"}
                
                if "max" in param_config and value > param_config["max"]:
                    return {"valid": False, "message": f"参数{param_name}值过大"}
        
        return {"valid": True, "message": "参数验证通过"}
    
    def _check_conditions(self, effect: Dict, game_state: GameState) -> bool:
        """检查效果前置条件"""
        conditions = effect.get("conditions", [])
        
        for condition in conditions:
            if not self._evaluate_condition(condition, game_state):
                return False
        
        return True
    
    def _evaluate_condition(self, condition: Dict, game_state: GameState) -> bool:
        """评估单个条件"""
        condition_type = condition.get("type")
        
        if condition_type == "attribute_check":
            target = condition.get("target", "player")
            attribute = condition.get("attribute")
            operator = condition.get("operator", ">=")
            value = condition.get("value", 0)
            
            if target == "player":
                current_value = game_state.player_attributes.get(attribute, 0)
            else:
                current_value = game_state.opponent_attributes.get(attribute, 0)
            
            return self._compare_values(current_value, operator, value)
        
        elif condition_type == "card_count":
            target = condition.get("target", "player")
            operator = condition.get("operator", ">=")
            value = condition.get("value", 0)
            
            if target == "player":
                current_count = len(game_state.player_hand)
            else:
                current_count = len(game_state.opponent_hand)
            
            return self._compare_values(current_count, operator, value)
        
        elif condition_type == "turn_number":
            operator = condition.get("operator", ">=")
            value = condition.get("value", 1)
            
            return self._compare_values(game_state.turn_number, operator, value)
        
        return True
    
    def _compare_values(self, current: Union[int, float], operator: str, 
                       target: Union[int, float]) -> bool:
        """比较数值"""
        if operator == ">=":
            return current >= target
        elif operator == "<=":
            return current <= target
        elif operator == "==":
            return current == target
        elif operator == "!=":
            return current != target
        elif operator == ">":
            return current > target
        elif operator == "<":
            return current < target
        return False
    
    # 具体效果处理器
    def _handle_modify_attribute(self, effect: Dict, game_state: GameState, 
                                caster: str) -> Dict:
        """处理属性修改效果"""
        attribute = effect["attribute"]
        value = effect["value"]
        target = effect.get("target", "self")
        
        if target == "self":
            target_attrs = game_state.player_attributes if caster == "player" else game_state.opponent_attributes
        elif target == "opponent":
            target_attrs = game_state.opponent_attributes if caster == "player" else game_state.player_attributes
        else:  # all
            # 对所有目标应用效果
            game_state.player_attributes[attribute] = max(0, 
                game_state.player_attributes.get(attribute, 0) + value)
            game_state.opponent_attributes[attribute] = max(0, 
                game_state.opponent_attributes.get(attribute, 0) + value)
            return {
                "result": EffectResult.SUCCESS,
                "message": f"所有目标的{attribute}修改了{value}",
                "details": {"attribute": attribute, "value": value, "target": "all"}
            }
        
        old_value = target_attrs.get(attribute, 0)
        new_value = max(0, old_value + value)  # 确保不为负数
        target_attrs[attribute] = new_value
        
        return {
            "result": EffectResult.SUCCESS,
            "message": f"{attribute}从{old_value}变为{new_value}",
            "details": {"attribute": attribute, "old_value": old_value, "new_value": new_value}
        }
    
    def _handle_draw_cards(self, effect: Dict, game_state: GameState, 
                          caster: str) -> Dict:
        """处理抽卡效果"""
        amount = effect["amount"]
        card_type = effect.get("card_type", "any")
        
        # 简化实现：随机选择卡牌
        available_cards = list(self.cards_config.get("cards", {}).keys())
        if card_type != "any":
            # 根据卡牌类型过滤
            available_cards = [card_id for card_id in available_cards 
                             if self.cards_config["cards"][card_id].get("type") == card_type]
        
        drawn_cards = random.sample(available_cards, min(amount, len(available_cards)))
        
        if caster == "player":
            game_state.player_hand.extend(drawn_cards)
        else:
            game_state.opponent_hand.extend(drawn_cards)
        
        return {
            "result": EffectResult.SUCCESS,
            "message": f"抽取了{len(drawn_cards)}张卡牌",
            "details": {"cards": drawn_cards, "amount": len(drawn_cards)}
        }
    
    def _handle_heal(self, effect: Dict, game_state: GameState, caster: str) -> Dict:
        """处理治疗效果"""
        amount = effect["amount"]
        heal_type = effect.get("type", "health")
        
        target_attrs = game_state.player_attributes if caster == "player" else game_state.opponent_attributes
        
        if heal_type in ["health", "both"]:
            old_health = target_attrs.get("health", 0)
            target_attrs["health"] = min(100, old_health + amount)  # 假设最大生命值为100
        
        if heal_type in ["energy", "both"]:
            old_energy = target_attrs.get("energy", 0)
            target_attrs["energy"] = min(100, old_energy + amount)  # 假设最大能量为100
        
        return {
            "result": EffectResult.SUCCESS,
            "message": f"恢复了{amount}点{heal_type}",
            "details": {"amount": amount, "type": heal_type}
        }
    
    def _handle_damage(self, effect: Dict, game_state: GameState, caster: str) -> Dict:
        """处理伤害效果"""
        amount = effect["amount"]
        damage_type = effect.get("damage_type", "direct")
        target = effect.get("target", "opponent")
        
        if target == "opponent":
            target_attrs = game_state.opponent_attributes if caster == "player" else game_state.player_attributes
        elif target == "self":
            target_attrs = game_state.player_attributes if caster == "player" else game_state.opponent_attributes
        else:  # all
            # 对所有目标造成伤害
            game_state.player_attributes["health"] = max(0, 
                game_state.player_attributes.get("health", 100) - amount)
            game_state.opponent_attributes["health"] = max(0, 
                game_state.opponent_attributes.get("health", 100) - amount)
            return {
                "result": EffectResult.SUCCESS,
                "message": f"对所有目标造成{amount}点{damage_type}伤害",
                "details": {"amount": amount, "type": damage_type, "target": "all"}
            }
        
        # 检查护盾
        shield_key = f"{caster}_shield" if target == "self" else f"{'opponent' if caster == 'player' else 'player'}_shield"
        shield_amount = game_state.shields.get(shield_key, 0)
        
        if shield_amount > 0:
            absorbed = min(shield_amount, amount)
            game_state.shields[shield_key] = shield_amount - absorbed
            amount -= absorbed
            
            if amount <= 0:
                return {
                    "result": EffectResult.BLOCKED,
                    "message": f"伤害被护盾完全吸收",
                    "details": {"absorbed": absorbed, "remaining_shield": game_state.shields[shield_key]}
                }
        
        old_health = target_attrs.get("health", 100)
        new_health = max(0, old_health - amount)
        target_attrs["health"] = new_health
        
        return {
            "result": EffectResult.SUCCESS,
            "message": f"造成{amount}点{damage_type}伤害",
            "details": {"amount": amount, "type": damage_type, "old_health": old_health, "new_health": new_health}
        }
    
    def _handle_shield(self, effect: Dict, game_state: GameState, caster: str) -> Dict:
        """处理护盾效果"""
        amount = effect["amount"]
        duration = effect.get("duration", 1)
        shield_type = effect.get("shield_type", "physical")
        
        shield_key = f"{caster}_shield"
        current_shield = game_state.shields.get(shield_key, 0)
        game_state.shields[shield_key] = current_shield + amount
        
        return {
            "result": EffectResult.SUCCESS,
            "message": f"获得{amount}点{shield_type}护盾",
            "details": {"amount": amount, "type": shield_type, "duration": duration}
        }
    
    def _handle_buff(self, effect: Dict, game_state: GameState, caster: str) -> Dict:
        """处理增益效果"""
        buff_type = effect["buff_type"]
        amount = effect["amount"]
        duration = effect.get("duration", 3)
        
        buff_data = {
            "type": buff_type,
            "amount": amount,
            "duration": duration,
            "caster": caster
        }
        
        game_state.active_buffs.append(buff_data)
        
        return {
            "result": EffectResult.SUCCESS,
            "message": f"获得{buff_type}增益效果",
            "details": buff_data
        }
    
    def _handle_debuff(self, effect: Dict, game_state: GameState, caster: str) -> Dict:
        """处理负面效果"""
        debuff_type = effect["debuff_type"]
        amount = effect["amount"]
        duration = effect.get("duration", 2)
        target = effect.get("target", "opponent")
        
        debuff_data = {
            "type": debuff_type,
            "amount": amount,
            "duration": duration,
            "target": target,
            "caster": caster
        }
        
        game_state.active_debuffs.append(debuff_data)
        
        return {
            "result": EffectResult.SUCCESS,
            "message": f"施加{debuff_type}负面效果",
            "details": debuff_data
        }
    
    def _handle_transform(self, effect: Dict, game_state: GameState, caster: str) -> Dict:
        """处理转换效果"""
        transform_type = effect["transform_type"]
        source = effect["source"]
        target = effect["target"]
        
        # 简化实现
        return {
            "result": EffectResult.SUCCESS,
            "message": f"将{source}转换为{target}",
            "details": {"type": transform_type, "source": source, "target": target}
        }
    
    def _handle_special_action(self, effect: Dict, game_state: GameState, caster: str) -> Dict:
        """处理特殊行动效果"""
        action_type = effect["action_type"]
        power = effect.get("power", 1)
        
        # 根据行动类型执行不同逻辑
        if action_type == "meditation":
            # 冥想：恢复能量和智慧
            target_attrs = game_state.player_attributes if caster == "player" else game_state.opponent_attributes
            target_attrs["energy"] = min(100, target_attrs.get("energy", 0) + power * 10)
            target_attrs["wisdom"] = min(100, target_attrs.get("wisdom", 0) + power * 5)
        
        elif action_type == "divination":
            # 占卜：增加运气，可能获得额外信息
            target_attrs = game_state.player_attributes if caster == "player" else game_state.opponent_attributes
            target_attrs["luck"] = min(100, target_attrs.get("luck", 0) + power * 8)
        
        return {
            "result": EffectResult.SUCCESS,
            "message": f"执行{action_type}特殊行动",
            "details": {"action": action_type, "power": power}
        }
    
    def _handle_conditional(self, effect: Dict, game_state: GameState, caster: str) -> Dict:
        """处理条件效果"""
        condition = effect["condition"]
        effect_if_true = effect["effect_if_true"]
        effect_if_false = effect.get("effect_if_false", [])
        
        if self._evaluate_condition(condition, game_state):
            results = []
            for sub_effect in effect_if_true:
                result = self.execute_effect(sub_effect, game_state, caster)
                results.append(result)
            return {
                "result": EffectResult.SUCCESS,
                "message": "条件为真，执行相应效果",
                "details": {"condition_met": True, "sub_results": results}
            }
        else:
            results = []
            for sub_effect in effect_if_false:
                result = self.execute_effect(sub_effect, game_state, caster)
                results.append(result)
            return {
                "result": EffectResult.SUCCESS,
                "message": "条件为假，执行备选效果",
                "details": {"condition_met": False, "sub_results": results}
            }
    
    def update_turn_effects(self, game_state: GameState):
        """更新回合效果（buff/debuff持续时间等）"""
        # 更新buff持续时间
        game_state.active_buffs = [
            buff for buff in game_state.active_buffs 
            if self._update_effect_duration(buff)
        ]
        
        # 更新debuff持续时间
        game_state.active_debuffs = [
            debuff for debuff in game_state.active_debuffs 
            if self._update_effect_duration(debuff)
        ]
        
        # 更新护盾（可能有时间限制）
        # 这里简化处理，实际可能需要更复杂的逻辑
    
    def _update_effect_duration(self, effect: Dict) -> bool:
        """更新效果持续时间，返回是否继续保持"""
        effect["duration"] -= 1
        return effect["duration"] > 0
    
    def get_effect_description(self, effect: Dict) -> str:
        """获取效果的文字描述"""
        effect_type = effect.get("type", "unknown")
        
        if effect_type == "MODIFY_ATTRIBUTE":
            attribute = effect.get("attribute", "unknown")
            value = effect.get("value", 0)
            sign = "+" if value >= 0 else ""
            return f"{attribute}{sign}{value}"
        
        elif effect_type == "DRAW_CARDS":
            amount = effect.get("amount", 1)
            return f"抽{amount}张卡"
        
        elif effect_type == "HEAL":
            amount = effect.get("amount", 0)
            heal_type = effect.get("type", "health")
            return f"恢复{amount}点{heal_type}"
        
        elif effect_type == "DAMAGE":
            amount = effect.get("amount", 0)
            return f"造成{amount}点伤害"
        
        elif effect_type == "SHIELD":
            amount = effect.get("amount", 0)
            return f"获得{amount}点护盾"
        
        elif effect_type == "BUFF":
            buff_type = effect.get("buff_type", "unknown")
            amount = effect.get("amount", 0)
            return f"{buff_type}+{amount}"
        
        elif effect_type == "DEBUFF":
            debuff_type = effect.get("debuff_type", "unknown")
            amount = effect.get("amount", 0)
            return f"{debuff_type}-{amount}"
        
        else:
            return f"{effect_type}效果"