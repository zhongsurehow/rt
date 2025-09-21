"""
增强的游戏机制 - 增加策略深度和趣味性
Enhanced Game Mechanics for deeper strategy and more fun
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random

class ActionType(Enum):
    """行动类型"""
    PLAY_CARD = "出牌"
    MOVE = "移动"
    MEDITATE = "冥想"
    STUDY = "研习"
    COMBO = "连招"
    SPECIAL = "特殊行动"

class ComboType(Enum):
    """连招类型"""
    YIN_YANG = "阴阳调和"      # 阴阳卦牌组合
    FIVE_ELEMENTS = "五行相生"  # 五行卦牌组合
    TRIGRAM_SYNC = "三才同步"   # 同类三角卦组合
    SEASONAL = "四时轮转"       # 季节性卦牌组合

@dataclass
class ComboEffect:
    """连招效果"""
    name: str
    description: str
    qi_bonus: int
    dao_xing_bonus: int
    special_effect: Optional[str]
    wisdom_points: int

@dataclass
class SeasonalBonus:
    """季节性奖励"""
    season: str
    bonus_cards: List[str]  # 本季节获得奖励的卦牌
    qi_multiplier: float
    dao_xing_multiplier: float
    special_effect: str

@dataclass
class AchievementCondition:
    """成就条件"""
    name: str
    description: str
    condition_type: str  # "combo", "cards_played", "dao_xing", "wisdom"
    target_value: int
    reward_qi: int
    reward_dao_xing: int
    reward_wisdom: int

class EnhancedGameMechanics:
    """增强的游戏机制管理器"""
    
    def __init__(self):
        self.combo_effects = self._initialize_combo_effects()
        self.seasonal_bonuses = self._initialize_seasonal_bonuses()
        self.achievements = self._initialize_achievements()
        self.current_season = "春"
        self.turn_count = 0
        
    def _initialize_combo_effects(self) -> Dict[ComboType, List[ComboEffect]]:
        """初始化连招效果"""
        return {
            ComboType.YIN_YANG: [
                ComboEffect(
                    name="太极和谐",
                    description="阴阳卦牌完美平衡，获得额外奖励",
                    qi_bonus=3,
                    dao_xing_bonus=2,
                    special_effect="下回合行动次数+1",
                    wisdom_points=5
                ),
                ComboEffect(
                    name="阴阳互补",
                    description="阴阳相济，相得益彰",
                    qi_bonus=2,
                    dao_xing_bonus=1,
                    special_effect="防御力+2",
                    wisdom_points=3
                )
            ],
            ComboType.FIVE_ELEMENTS: [
                ComboEffect(
                    name="五行相生",
                    description="五行卦牌按相生顺序出牌",
                    qi_bonus=4,
                    dao_xing_bonus=3,
                    special_effect="获得五行护盾",
                    wisdom_points=8
                ),
                ComboEffect(
                    name="生生不息",
                    description="五行循环，生机勃勃",
                    qi_bonus=3,
                    dao_xing_bonus=2,
                    special_effect="每回合恢复1点气",
                    wisdom_points=6
                )
            ],
            ComboType.TRIGRAM_SYNC: [
                ComboEffect(
                    name="三才合一",
                    description="天地人三才同步，威力倍增",
                    qi_bonus=5,
                    dao_xing_bonus=3,
                    special_effect="本回合所有行动效果翻倍",
                    wisdom_points=10
                )
            ],
            ComboType.SEASONAL: [
                ComboEffect(
                    name="顺应天时",
                    description="顺应季节变化，获得天时之利",
                    qi_bonus=2,
                    dao_xing_bonus=2,
                    special_effect="季节奖励翻倍",
                    wisdom_points=4
                )
            ]
        }
    
    def _initialize_seasonal_bonuses(self) -> Dict[str, SeasonalBonus]:
        """初始化季节性奖励"""
        return {
            "春": SeasonalBonus(
                season="春",
                bonus_cards=["震", "巽", "屯", "随"],  # 春季对应雷风卦
                qi_multiplier=1.2,
                dao_xing_multiplier=1.0,
                special_effect="生机勃勃：每回合额外获得1点气"
            ),
            "夏": SeasonalBonus(
                season="夏",
                bonus_cards=["离", "乾", "大有", "丰"],  # 夏季对应火天卦
                qi_multiplier=1.0,
                dao_xing_multiplier=1.3,
                special_effect="阳气旺盛：道行获得增加30%"
            ),
            "秋": SeasonalBonus(
                season="秋",
                bonus_cards=["兑", "乾", "履", "夬"],  # 秋季对应泽天卦
                qi_multiplier=1.1,
                dao_xing_multiplier=1.1,
                special_effect="收获季节：所有奖励增加10%"
            ),
            "冬": SeasonalBonus(
                season="冬",
                bonus_cards=["坎", "艮", "蒙", "颐"],  # 冬季对应水山卦
                qi_multiplier=1.0,
                dao_xing_multiplier=1.0,
                special_effect="韬光养晦：防御力翻倍，学习效果增强"
            )
        }
    
    def _initialize_achievements(self) -> List[AchievementCondition]:
        """初始化成就系统"""
        return [
            AchievementCondition(
                name="初窥门径",
                description="首次成功施展连招",
                condition_type="combo",
                target_value=1,
                reward_qi=2,
                reward_dao_xing=1,
                reward_wisdom=5
            ),
            AchievementCondition(
                name="连招大师",
                description="成功施展10次连招",
                condition_type="combo",
                target_value=10,
                reward_qi=5,
                reward_dao_xing=3,
                reward_wisdom=15
            ),
            AchievementCondition(
                name="卦牌收集家",
                description="使用过20种不同的卦牌",
                condition_type="cards_played",
                target_value=20,
                reward_qi=3,
                reward_dao_xing=2,
                reward_wisdom=10
            ),
            AchievementCondition(
                name="道行深厚",
                description="道行达到15点",
                condition_type="dao_xing",
                target_value=15,
                reward_qi=0,
                reward_dao_xing=0,
                reward_wisdom=20
            ),
            AchievementCondition(
                name="智慧如海",
                description="累积获得100点智慧",
                condition_type="wisdom",
                target_value=100,
                reward_qi=5,
                reward_dao_xing=5,
                reward_wisdom=0
            )
        ]
    
    def check_combo(self, played_cards: List[str]) -> Optional[ComboEffect]:
        """检查是否形成连招"""
        if len(played_cards) < 2:
            return None
        
        # 检查阴阳调和
        if self._check_yin_yang_combo(played_cards):
            return random.choice(self.combo_effects[ComboType.YIN_YANG])
        
        # 检查五行相生
        if self._check_five_elements_combo(played_cards):
            return random.choice(self.combo_effects[ComboType.FIVE_ELEMENTS])
        
        # 检查三才同步
        if self._check_trigram_sync_combo(played_cards):
            return random.choice(self.combo_effects[ComboType.TRIGRAM_SYNC])
        
        # 检查季节性连招
        if self._check_seasonal_combo(played_cards):
            return random.choice(self.combo_effects[ComboType.SEASONAL])
        
        return None
    
    def _check_yin_yang_combo(self, cards: List[str]) -> bool:
        """检查阴阳调和连招"""
        # 简化版：检查是否有乾坤组合
        return "乾" in cards and "坤" in cards
    
    def _check_five_elements_combo(self, cards: List[str]) -> bool:
        """检查五行相生连招"""
        # 五行对应的卦：木(震巽)、火(离)、土(坤艮)、金(乾兑)、水(坎)
        five_elements_cards = {
            "木": ["震", "巽"],
            "火": ["离"],
            "土": ["坤", "艮"],
            "金": ["乾", "兑"],
            "水": ["坎"]
        }
        
        elements_present = []
        for element, element_cards in five_elements_cards.items():
            if any(card in cards for card in element_cards):
                elements_present.append(element)
        
        return len(elements_present) >= 3
    
    def _check_trigram_sync_combo(self, cards: List[str]) -> bool:
        """检查三才同步连招"""
        # 简化版：检查是否有三个相同类型的卦
        trigram_types = {
            "天": ["乾"],
            "地": ["坤"],
            "雷": ["震"],
            "风": ["巽"],
            "水": ["坎"],
            "火": ["离"],
            "山": ["艮"],
            "泽": ["兑"]
        }
        
        for trigram_type, type_cards in trigram_types.items():
            if len([card for card in cards if card in type_cards]) >= 2:
                return True
        
        return False
    
    def _check_seasonal_combo(self, cards: List[str]) -> bool:
        """检查季节性连招"""
        current_bonus = self.seasonal_bonuses[self.current_season]
        return len([card for card in cards if card in current_bonus.bonus_cards]) >= 2
    
    def get_seasonal_bonus(self, card_name: str) -> Tuple[float, float]:
        """获取季节性奖励倍数"""
        current_bonus = self.seasonal_bonuses[self.current_season]
        if card_name in current_bonus.bonus_cards:
            return current_bonus.qi_multiplier, current_bonus.dao_xing_multiplier
        return 1.0, 1.0
    
    def advance_season(self):
        """推进季节"""
        seasons = ["春", "夏", "秋", "冬"]
        current_index = seasons.index(self.current_season)
        self.current_season = seasons[(current_index + 1) % 4]
    
    def get_current_season_info(self) -> Dict:
        """获取当前季节信息"""
        bonus = self.seasonal_bonuses[self.current_season]
        return {
            "season": bonus.season,
            "bonus_cards": bonus.bonus_cards,
            "special_effect": bonus.special_effect,
            "qi_multiplier": bonus.qi_multiplier,
            "dao_xing_multiplier": bonus.dao_xing_multiplier
        }
    
    def check_achievements(self, player_stats: Dict) -> List[AchievementCondition]:
        """检查成就完成情况"""
        completed_achievements = []
        
        for achievement in self.achievements:
            if achievement.condition_type == "combo" and player_stats.get("combos_performed", 0) >= achievement.target_value:
                completed_achievements.append(achievement)
            elif achievement.condition_type == "cards_played" and player_stats.get("unique_cards_played", 0) >= achievement.target_value:
                completed_achievements.append(achievement)
            elif achievement.condition_type == "dao_xing" and player_stats.get("dao_xing", 0) >= achievement.target_value:
                completed_achievements.append(achievement)
            elif achievement.condition_type == "wisdom" and player_stats.get("wisdom_points", 0) >= achievement.target_value:
                completed_achievements.append(achievement)
        
        return completed_achievements
    
    def get_random_hexagram(self) -> Optional[Dict]:
        """获取随机卦象"""
        hexagrams = [
            {"name": "乾为天", "trigrams": ("乾", "乾"), "meaning": "刚健中正，自强不息"},
            {"name": "坤为地", "trigrams": ("坤", "坤"), "meaning": "厚德载物，包容万象"},
            {"name": "水雷屯", "trigrams": ("坎", "震"), "meaning": "万物始生，艰难创业"},
            {"name": "山水蒙", "trigrams": ("艮", "坎"), "meaning": "启蒙教育，求知若渴"},
            {"name": "水天需", "trigrams": ("坎", "乾"), "meaning": "等待时机，蓄势待发"},
            {"name": "天水讼", "trigrams": ("乾", "坎"), "meaning": "争讼纠纷，慎重处理"},
            {"name": "地水师", "trigrams": ("坤", "坎"), "meaning": "统帅军队，纪律严明"},
            {"name": "水地比", "trigrams": ("坎", "坤"), "meaning": "亲密合作，和谐共处"}
        ]
        
        if hexagrams:
            return random.choice(hexagrams)
        return None

    def get_strategic_advice(self, player_hand: List[str], game_state: Dict) -> List[str]:
        """获取策略建议"""
        advice = []
        
        # 季节性建议
        current_bonus = self.seasonal_bonuses[self.current_season]
        seasonal_cards = [card for card in player_hand if card in current_bonus.bonus_cards]
        if seasonal_cards:
            advice.append(f"当前是{self.current_season}季，建议优先使用：{', '.join(seasonal_cards)}")
        
        # 连招建议
        if "乾" in player_hand and "坤" in player_hand:
            advice.append("手中有乾坤二卦，可以尝试阴阳调和连招")
        
        # 五行建议
        elements_in_hand = self._analyze_five_elements_in_hand(player_hand)
        if len(elements_in_hand) >= 3:
            advice.append(f"手中有{len(elements_in_hand)}种五行卦牌，可以尝试五行相生连招")
        
        return advice
    
    def _analyze_five_elements_in_hand(self, hand: List[str]) -> List[str]:
        """分析手牌中的五行元素"""
        five_elements_cards = {
            "木": ["震", "巽"],
            "火": ["离"],
            "土": ["坤", "艮"],
            "金": ["乾", "兑"],
            "水": ["坎"]
        }
        
        elements_present = []
        for element, element_cards in five_elements_cards.items():
            if any(card in hand for card in element_cards):
                elements_present.append(element)
        
        return elements_present

# 全局游戏机制实例
enhanced_mechanics = EnhancedGameMechanics()

def get_combo_effect(played_cards: List[str]) -> Optional[ComboEffect]:
    """获取连招效果"""
    return enhanced_mechanics.check_combo(played_cards)

def get_seasonal_multiplier(card_name: str) -> Tuple[float, float]:
    """获取季节性倍数"""
    return enhanced_mechanics.get_seasonal_bonus(card_name)

def get_current_season() -> str:
    """获取当前季节"""
    return enhanced_mechanics.current_season

def advance_game_season():
    """推进游戏季节"""
    enhanced_mechanics.advance_season()

def get_strategic_tips(player_hand: List[str], game_state: Dict) -> List[str]:
    """获取策略提示"""
    return enhanced_mechanics.get_strategic_advice(player_hand, game_state)