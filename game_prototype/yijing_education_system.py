#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
易经教育系统 - 让玩家在游戏中学习易经知识
包含卦象解释、爻辞学习、哲学思想等教育内容
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import random

from card_base import GuaCard


class LearningLevel(Enum):
    """学习难度等级"""
    BEGINNER = "初学者"      # 基础概念
    INTERMEDIATE = "进阶者"  # 深入理解
    ADVANCED = "高级者"      # 哲学思辨
    MASTER = "大师级"        # 融会贯通


@dataclass
class YijingKnowledge:
    """易经知识点"""
    title: str
    content: str
    level: LearningLevel
    category: str
    related_guas: List[str]
    practical_wisdom: str  # 实用智慧
    

@dataclass
class LearningProgress:
    """学习进度"""
    player_name: str
    learned_guas: List[str]
    mastered_concepts: List[str]
    current_level: LearningLevel
    wisdom_points: int
    

class YijingEducationSystem:
    """易经教育系统"""
    
    def __init__(self):
        self.knowledge_base = self._build_knowledge_base()
        self.learning_paths = self._create_learning_paths()
        self.player_progress: Dict[str, LearningProgress] = {}
        
    def _build_knowledge_base(self) -> Dict[str, YijingKnowledge]:
        """构建易经知识库"""
        knowledge = {}
        
        # 基础八卦知识
        basic_trigrams = {
            "乾": YijingKnowledge(
                title="乾卦 - 天之象",
                content="乾为天，纯阳之卦。象征刚健、进取、领导。乾卦六爻皆阳，代表至刚至健之象。",
                level=LearningLevel.BEGINNER,
                category="八卦基础",
                related_guas=["乾为天", "天风姤", "天山遁", "天地否"],
                practical_wisdom="君子以自强不息。在困难面前保持坚韧不拔的精神。"
            ),
            "坤": YijingKnowledge(
                title="坤卦 - 地之象", 
                content="坤为地，纯阴之卦。象征柔顺、包容、承载。坤卦六爻皆阴，代表至柔至顺之象。",
                level=LearningLevel.BEGINNER,
                category="八卦基础",
                related_guas=["坤为地", "地雷复", "地泽临", "地天泰"],
                practical_wisdom="君子以厚德载物。以宽容和包容的心态对待他人。"
            ),
            "震": YijingKnowledge(
                title="震卦 - 雷之象",
                content="震为雷，象征动、奋起、震动。一阳在下，二阴在上，代表阳气初动。",
                level=LearningLevel.BEGINNER,
                category="八卦基础", 
                related_guas=["震为雷", "雷地豫", "雷水解", "雷风恒"],
                practical_wisdom="雷声震动，万物复苏。把握时机，果断行动。"
            ),
            "巽": YijingKnowledge(
                title="巽卦 - 风之象",
                content="巽为风，象征入、顺从、渗透。一阴在下，二阳在上，代表柔顺而入。",
                level=LearningLevel.BEGINNER,
                category="八卦基础",
                related_guas=["巽为风", "风天小畜", "风火家人", "风雷益"],
                practical_wisdom="风行水上，自然成文。以柔克刚，循序渐进。"
            ),
            "坎": YijingKnowledge(
                title="坎卦 - 水之象",
                content="坎为水，象征险、陷、流动。一阳在中，二阴在外，代表外柔内刚。",
                level=LearningLevel.BEGINNER,
                category="八卦基础",
                related_guas=["坎为水", "水泽节", "水雷屯", "水火既济"],
                practical_wisdom="水流不争先，却能穿石。保持内心的坚定，外表的柔和。"
            ),
            "离": YijingKnowledge(
                title="离卦 - 火之象",
                content="离为火，象征明、美丽、文明。一阴在中，二阳在外，代表外刚内柔。",
                level=LearningLevel.BEGINNER,
                category="八卦基础",
                related_guas=["离为火", "火山旅", "火风鼎", "火水未济"],
                practical_wisdom="火性向上，照亮黑暗。保持内心的谦逊，外表的光明。"
            ),
            "艮": YijingKnowledge(
                title="艮卦 - 山之象",
                content="艮为山，象征止、静、稳定。一阳在上，二阴在下，代表止而不动。",
                level=LearningLevel.BEGINNER,
                category="八卦基础",
                related_guas=["艮为山", "山火贲", "山天大畜", "山泽损"],
                practical_wisdom="山不动摇，静观其变。知止而后有定，定而后能静。"
            ),
            "兑": YijingKnowledge(
                title="兑卦 - 泽之象",
                content="兑为泽，象征悦、口、交流。一阴在上，二阳在下，代表内刚外柔。",
                level=LearningLevel.BEGINNER,
                category="八卦基础",
                related_guas=["兑为泽", "泽水困", "泽地萃", "泽山咸"],
                practical_wisdom="泽润万物，和悦待人。以诚待人，以和为贵。"
            ),
        }
        knowledge.update(basic_trigrams)
        
        # 进阶哲学概念
        advanced_concepts = {
            "阴阳": YijingKnowledge(
                title="阴阳哲学",
                content="阴阳是易经的核心概念。阴阳相对而生，相互依存，相互转化。阴中有阳，阳中有阴。",
                level=LearningLevel.INTERMEDIATE,
                category="哲学思想",
                related_guas=["乾", "坤", "既济", "未济"],
                practical_wisdom="万事万物都有阴阳两面，学会平衡和转化。"
            ),
            "五行": YijingKnowledge(
                title="五行相生相克",
                content="五行：金、木、水、火、土。相生：木生火，火生土，土生金，金生水，水生木。相克：木克土，土克水，水克火，火克金，金克木。",
                level=LearningLevel.INTERMEDIATE,
                category="哲学思想",
                related_guas=["乾", "震", "坎", "离", "坤"],
                practical_wisdom="理解事物间的相互关系，顺势而为。"
            ),
            "变化": YijingKnowledge(
                title="变化之道",
                content="易经的核心是变化。唯一不变的就是变化本身。通过观察变化的规律，我们可以预测未来，指导行动。",
                level=LearningLevel.ADVANCED,
                category="哲学思想",
                related_guas=["乾", "坤", "屯", "蒙"],
                practical_wisdom="适应变化，在变化中寻找机遇。"
            ),
            "中庸": YijingKnowledge(
                title="中庸之道",
                content="中庸不是平庸，而是恰到好处。既不过分，也不不及。在动态平衡中寻找最佳状态。",
                level=LearningLevel.ADVANCED,
                category="哲学思想",
                related_guas=["既济", "未济", "泰", "否"],
                practical_wisdom="凡事适度，避免极端，寻求平衡。"
            ),
        }
        knowledge.update(advanced_concepts)
        
        # 实用智慧
        practical_wisdom = {
            "时机": YijingKnowledge(
                title="把握时机",
                content="易经强调时机的重要性。同样的行动，在不同的时机会有不同的结果。观察时势，顺应天时。",
                level=LearningLevel.MASTER,
                category="实用智慧",
                related_guas=["屯", "蒙", "需", "讼"],
                practical_wisdom="识时务者为俊杰，顺势而为事半功倍。"
            ),
            "进退": YijingKnowledge(
                title="进退之道",
                content="知进退，明得失。该进则进，该退则退。进不盲目，退不懦弱。",
                level=LearningLevel.MASTER,
                category="实用智慧",
                related_guas=["遁", "大壮", "晋", "明夷"],
                practical_wisdom="进退有度，张弛有道。"
            ),
        }
        knowledge.update(practical_wisdom)
        
        return knowledge
    
    def _create_learning_paths(self) -> Dict[LearningLevel, List[str]]:
        """创建学习路径"""
        return {
            LearningLevel.BEGINNER: ["乾", "坤", "震", "巽", "坎", "离", "艮", "兑"],
            LearningLevel.INTERMEDIATE: ["阴阳", "五行"],
            LearningLevel.ADVANCED: ["变化", "中庸"],
            LearningLevel.MASTER: ["时机", "进退"],
        }
    
    def initialize_player(self, player_name: str):
        """初始化玩家学习进度"""
        self.player_progress[player_name] = LearningProgress(
            player_name=player_name,
            learned_guas=[],
            mastered_concepts=[],
            current_level=LearningLevel.BEGINNER,
            wisdom_points=0
        )
    
    def initialize_player_progress(self, player_name: str):
        """初始化玩家学习进度（别名方法）"""
        self.initialize_player(player_name)
    
    def learn_from_card(self, player_name: str, card: GuaCard) -> Optional[YijingKnowledge]:
        """从卦牌中学习知识"""
        if player_name not in self.player_progress:
            self.initialize_player(player_name)
        
        progress = self.player_progress[player_name]
        
        # 查找相关知识
        gua_name = card.name.split()[0] if " " in card.name else card.name
        
        # 寻找匹配的知识点
        for key, knowledge in self.knowledge_base.items():
            if gua_name in knowledge.related_guas or key == gua_name:
                if key not in progress.mastered_concepts:
                    progress.mastered_concepts.append(key)
                    progress.wisdom_points += self._get_wisdom_points(knowledge.level)
                    self._check_level_up(progress)
                    return knowledge
        
        return None
    
    def _get_wisdom_points(self, level: LearningLevel) -> int:
        """根据知识等级获取智慧点数"""
        points_map = {
            LearningLevel.BEGINNER: 1,
            LearningLevel.INTERMEDIATE: 2,
            LearningLevel.ADVANCED: 3,
            LearningLevel.MASTER: 5,
        }
        return points_map[level]
    
    def _check_level_up(self, progress: LearningProgress):
        """检查是否可以升级"""
        level_requirements = {
            LearningLevel.BEGINNER: 0,
            LearningLevel.INTERMEDIATE: 8,   # 学会基础八卦
            LearningLevel.ADVANCED: 15,     # 掌握进阶概念
            LearningLevel.MASTER: 25,       # 深度理解
        }
        
        for level, requirement in level_requirements.items():
            if progress.wisdom_points >= requirement:
                progress.current_level = level
    
    def get_random_wisdom(self, level: Optional[LearningLevel] = None) -> YijingKnowledge:
        """获取随机智慧"""
        if level is None:
            available_knowledge = list(self.knowledge_base.values())
        else:
            available_knowledge = [k for k in self.knowledge_base.values() if k.level == level]
        
        return random.choice(available_knowledge)
    
    def get_learning_suggestion(self, player_name: str) -> Optional[str]:
        """获取学习建议"""
        if player_name not in self.player_progress:
            return "开始你的易经学习之旅吧！"
        
        progress = self.player_progress[player_name]
        current_path = self.learning_paths[progress.current_level]
        
        # 找到下一个应该学习的概念
        for concept in current_path:
            if concept not in progress.mastered_concepts:
                knowledge = self.knowledge_base.get(concept)
                if knowledge:
                    return f"建议学习：{knowledge.title} - {knowledge.content[:50]}..."
        
        # 如果当前等级都学完了，建议升级
        next_level_map = {
            LearningLevel.BEGINNER: LearningLevel.INTERMEDIATE,
            LearningLevel.INTERMEDIATE: LearningLevel.ADVANCED,
            LearningLevel.ADVANCED: LearningLevel.MASTER,
        }
        
        if progress.current_level in next_level_map:
            return f"恭喜！你已经掌握了{progress.current_level.value}的知识，可以学习更高深的内容了！"
        
        return "你已经是易经大师了！继续在实践中运用这些智慧吧！"
    
    def get_player_progress(self, player_name: str) -> Optional[LearningProgress]:
        """获取玩家学习进度"""
        return self.player_progress.get(player_name)
    
    def get_random_knowledge(self, level: Optional[LearningLevel] = None) -> Optional[YijingKnowledge]:
        """获取随机知识点"""
        if level:
            # 筛选指定难度的知识点
            filtered_knowledge = [k for k in self.knowledge_base.values() if k.level == level]
            if filtered_knowledge:
                return random.choice(filtered_knowledge)
        
        # 返回任意知识点
        if self.knowledge_base:
            return random.choice(list(self.knowledge_base.values()))
        return None
    
    def record_learning(self, player_name: str, knowledge_title: str, points_earned: int = 1):
        """记录学习成果"""
        if player_name not in self.player_progress:
            self.initialize_player_progress(player_name)
        
        progress = self.player_progress[player_name]
        
        # 添加到已掌握概念
        if knowledge_title not in progress.mastered_concepts:
            progress.mastered_concepts.append(knowledge_title)
        
        # 增加智慧点数
        progress.wisdom_points += points_earned
        
        # 检查是否升级
        self._check_level_up(progress)
    
    def explain_card_meaning(self, card: GuaCard) -> str:
        """解释卦牌含义"""
        gua_name = card.name.split()[0] if " " in card.name else card.name
        
        # 查找相关知识
        for knowledge in self.knowledge_base.values():
            if gua_name in knowledge.related_guas or gua_name in knowledge.title:
                return f"【{knowledge.title}】\n{knowledge.content}\n\n💡 实用智慧：{knowledge.practical_wisdom}"
        
        # 如果没有找到特定知识，提供通用解释
        return f"【{card.name}】\n这是一张蕴含易经智慧的卦牌。每张卦牌都代表着特定的象征意义和人生哲理。\n\n💡 建议：仔细观察卦牌的效果，思考其背后的易经原理。"
    
    def get_daily_wisdom(self) -> str:
        """获取每日智慧"""
        wisdom_quotes = [
            "天行健，君子以自强不息。",
            "地势坤，君子以厚德载物。",
            "穷则变，变则通，通则久。",
            "君子藏器于身，待时而动。",
            "同声相应，同气相求。",
            "积善之家，必有余庆。",
            "知进退存亡而不失其正者，其唯圣人乎！",
            "易与天地准，故能弥纶天地之道。",
            "一阴一阳之谓道。",
            "刚柔相推而生变化。",
        ]
        return random.choice(wisdom_quotes)
    
    def create_learning_quiz(self, player_name: str) -> Dict:
        """创建学习小测验"""
        if player_name not in self.player_progress:
            self.initialize_player(player_name)
        
        progress = self.player_progress[player_name]
        
        # 根据玩家等级选择合适的题目
        available_concepts = [c for c in progress.mastered_concepts if c in self.knowledge_base]
        
        if not available_concepts:
            return {
                "question": "易经中的'易'字有几种含义？",
                "options": ["1种", "2种", "3种", "4种"],
                "correct": 2,
                "explanation": "易有三义：简易、变易、不易。"
            }
        
        # 随机选择一个已学概念进行测验
        concept = random.choice(available_concepts)
        knowledge = self.knowledge_base[concept]
        
        return {
            "question": f"关于{knowledge.title}，以下哪个说法是正确的？",
            "options": [
                knowledge.practical_wisdom,
                "这是错误的选项A",
                "这是错误的选项B", 
                "这是错误的选项C"
            ],
            "correct": 0,
            "explanation": knowledge.content
        }


# 全局教育系统实例
education_system = YijingEducationSystem()