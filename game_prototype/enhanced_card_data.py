"""
增强的卦牌数据 - 包含详细的易经教学内容
Enhanced Card Data with comprehensive I Ching educational content
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class GuaType(Enum):
    """卦的类型"""
    QIAN = "乾"  # 天
    KUN = "坤"   # 地
    ZHEN = "震"  # 雷
    XUN = "巽"   # 风
    KAN = "坎"   # 水
    LI = "离"    # 火
    GEN = "艮"   # 山
    DUI = "兑"   # 泽

@dataclass
class YaoLine:
    """爻线数据"""
    position: int  # 位置 (1-6, 从下到上)
    type: str     # "阳" 或 "阴"
    text: str     # 爻辞
    meaning: str  # 含义解释
    wisdom: str   # 人生智慧

@dataclass
class EnhancedCard:
    """增强的卦牌数据"""
    # 基础信息
    name: str
    chinese_name: str
    number: int  # 卦序 (1-64)
    
    # 卦象信息
    upper_trigram: GuaType  # 上卦
    lower_trigram: GuaType  # 下卦
    symbol: str            # 卦象符号
    
    # 游戏属性
    cost: int
    qi_effect: int
    dao_xing_effect: int
    special_effect: Optional[str]
    
    # 教学内容
    judgment: str          # 卦辞
    judgment_meaning: str  # 卦辞含义
    image: str            # 象辞
    image_meaning: str    # 象辞含义
    yao_lines: List[YaoLine]  # 六爻
    
    # 哲学内容
    philosophy: str       # 哲学思想
    life_wisdom: str     # 人生智慧
    modern_application: str  # 现代应用
    
    # 学习提示
    learning_tips: List[str]
    difficulty_level: int  # 学习难度 (1-5)

# 详细的卦牌数据库
ENHANCED_CARDS = {
    "乾": EnhancedCard(
        name="Qian",
        chinese_name="乾",
        number=1,
        upper_trigram=GuaType.QIAN,
        lower_trigram=GuaType.QIAN,
        symbol="☰☰",
        cost=3,
        qi_effect=2,
        dao_xing_effect=1,
        special_effect="连续行动",
        judgment="乾：元，亨，利，贞。",
        judgment_meaning="乾卦象征天，具有元始、亨通、和谐、正固四种品德。",
        image="天行健，君子以自强不息。",
        image_meaning="天的运行刚健不息，君子应效法天道，自强不息。",
        yao_lines=[
            YaoLine(1, "阳", "初九：潜龙，勿用。", "如潜伏的龙，时机未到，不宜行动。", "韬光养晦，积蓄力量"),
            YaoLine(2, "阳", "九二：见龙在田，利见大人。", "龙出现在田野，有利于见到大人。", "崭露头角，寻求指导"),
            YaoLine(3, "阳", "九三：君子终日乾乾，夕惕若，厉无咎。", "君子整日勤奋，晚上警惕，虽危险但无过失。", "勤奋谨慎，持续努力"),
            YaoLine(4, "阳", "九四：或跃在渊，无咎。", "或许跃起在深渊上，没有过失。", "审时度势，把握机会"),
            YaoLine(5, "阳", "九五：飞龙在天，利见大人。", "飞龙在天空，有利于见到大人。", "功成名就，德高望重"),
            YaoLine(6, "阳", "上九：亢龙有悔。", "过于高亢的龙会有悔恨。", "物极必反，适可而止")
        ],
        philosophy="乾卦体现了刚健、进取、创造的精神，是阳刚之道的典型代表。",
        life_wisdom="人生如龙，需要经历潜伏、成长、奋斗、成功等阶段，关键是把握时机，自强不息。",
        modern_application="在现代社会中，乾卦精神体现为创新精神、领导力、持续学习和自我提升。",
        learning_tips=[
            "乾卦是六十四卦之首，代表纯阳之卦",
            "六爻皆阳，象征天的刚健特性",
            "龙是乾卦的象征，代表君子品格",
            "自强不息是乾卦的核心精神"
        ],
        difficulty_level=2
    ),
    
    "坤": EnhancedCard(
        name="Kun",
        chinese_name="坤",
        number=2,
        upper_trigram=GuaType.KUN,
        lower_trigram=GuaType.KUN,
        symbol="☷☷",
        cost=2,
        qi_effect=1,
        dao_xing_effect=2,
        special_effect="防御强化",
        judgment="坤：元亨，利牝马之贞。君子有攸往，先迷后得主，利西南得朋，东北丧朋。安贞吉。",
        judgment_meaning="坤卦象征地，具有包容、承载的品德，如雌马般柔顺而坚贞。",
        image="地势坤，君子以厚德载物。",
        image_meaning="大地的形势坤厚，君子应效法大地，以深厚的德行承载万物。",
        yao_lines=[
            YaoLine(1, "阴", "初六：履霜，坚冰至。", "踩到霜，坚冰将至。", "见微知著，防患未然"),
            YaoLine(2, "阴", "六二：直，方，大，不习无不利。", "正直、方正、宽大，不学习也无不利。", "品德天成，自然而然"),
            YaoLine(3, "阴", "六三：含章可贞。或从王事，无成有终。", "含蓄美德可以坚持。或许从事王事，无成就但有结果。", "内敛含蓄，默默奉献"),
            YaoLine(4, "阴", "六四：括囊；无咎，无誉。", "扎紧口袋；没有过失，也没有赞誉。", "谨言慎行，明哲保身"),
            YaoLine(5, "阴", "六五：黄裳，元吉。", "黄色的衣裳，大吉。", "中正之德，吉祥如意"),
            YaoLine(6, "阴", "上六：龙战于野，其血玄黄。", "龙在野外争斗，血流成河。", "阴极阳生，变化在即")
        ],
        philosophy="坤卦体现了柔顺、包容、承载的精神，是阴柔之道的典型代表。",
        life_wisdom="人生需要既有乾卦的刚健，也要有坤卦的柔顺，刚柔并济才能成就大事。",
        modern_application="在现代社会中，坤卦精神体现为团队合作、包容理解、可持续发展的理念。",
        learning_tips=[
            "坤卦是六十四卦第二卦，与乾卦相对",
            "六爻皆阴，象征地的柔顺特性",
            "厚德载物是坤卦的核心精神",
            "柔顺不等于软弱，而是一种智慧"
        ],
        difficulty_level=2
    ),
    
    "屯": EnhancedCard(
        name="Zhun",
        chinese_name="屯",
        number=3,
        upper_trigram=GuaType.KAN,
        lower_trigram=GuaType.ZHEN,
        symbol="☵☳",
        cost=2,
        qi_effect=1,
        dao_xing_effect=1,
        special_effect="资源积累",
        judgment="屯：元亨利贞。勿用，有攸往，利建侯。",
        judgment_meaning="屯卦象征初生的困难，虽然艰难但终将亨通，适合建立基业。",
        image="云雷，屯；君子以经纶。",
        image_meaning="云和雷象征屯卦，君子应当经营治理，建立秩序。",
        yao_lines=[
            YaoLine(1, "阳", "初九：磐桓；利居贞，利建侯。", "徘徊不前；适合安居守正，适合建立诸侯。", "稳扎稳打，建立根基"),
            YaoLine(2, "阴", "六二：屯如邅如，乘马班如。匪寇婚媾，女子贞不字，十年乃字。", "困难重重，骑马徘徊。不是强盗而是求婚，女子坚贞不嫁，十年后才嫁。", "坚持原则，等待时机"),
            YaoLine(3, "阴", "六三：即鹿无虞，惟入于林中，君子几不如舍，往吝。", "追鹿没有向导，只能进入林中，君子不如放弃，前往会有困难。", "量力而行，适时放弃"),
            YaoLine(4, "阴", "六四：乘马班如，求婚媾，往吉，无不利。", "骑马徘徊，求婚，前往吉利，无不利。", "主动出击，把握机会"),
            YaoLine(5, "阳", "九五：屯其膏，小贞吉，大贞凶。", "积聚财富，小事守正吉利，大事守正凶险。", "适度积累，不可贪大"),
            YaoLine(6, "阴", "上六：乘马班如，泣血涟如。", "骑马徘徊，哭得血泪涟涟。", "困境极致，需要坚持")
        ],
        philosophy="屯卦体现了万事开头难的道理，强调在困难中坚持和积累的重要性。",
        life_wisdom="创业初期必然困难重重，关键是要有耐心和毅力，稳扎稳打地建立基础。",
        modern_application="在现代创业和项目管理中，屯卦提醒我们要做好长期准备，不急于求成。",
        learning_tips=[
            "屯卦由震下坎上组成，象征雷在水下",
            "屯字本意为草木初生，象征新生事物的艰难",
            "这是第一个由不同卦组成的复卦",
            "体现了阴阳相济的哲学思想"
        ],
        difficulty_level=3
    )
}

# 卦象组合效果
TRIGRAM_COMBINATIONS = {
    (GuaType.QIAN, GuaType.QIAN): {"name": "乾为天", "effect": "大吉，获得额外行动"},
    (GuaType.KUN, GuaType.KUN): {"name": "坤为地", "effect": "防御加倍，获得稳定收益"},
    (GuaType.KAN, GuaType.ZHEN): {"name": "水雷屯", "effect": "资源积累，下回合获得额外资源"},
    # 可以继续添加更多组合...
}

# 学习路径推荐
LEARNING_PATHS = {
    "beginner": {
        "name": "初学者路径",
        "description": "从最基础的乾坤二卦开始学习",
        "cards": ["乾", "坤", "屯", "蒙", "需", "讼"],
        "focus": "基础概念和阴阳理论"
    },
    "philosophy": {
        "name": "哲学思辨路径", 
        "description": "重点学习易经的哲学思想",
        "cards": ["乾", "坤", "既济", "未济", "泰", "否"],
        "focus": "对立统一和变化规律"
    },
    "practical": {
        "name": "实用智慧路径",
        "description": "学习易经在现代生活中的应用",
        "cards": ["谦", "豫", "随", "蛊", "临", "观"],
        "focus": "人际关系和处世智慧"
    }
}

def get_card_by_name(name: str) -> Optional[EnhancedCard]:
    """根据名称获取卦牌"""
    return ENHANCED_CARDS.get(name)

def get_cards_by_difficulty(level: int) -> List[EnhancedCard]:
    """根据难度等级获取卦牌"""
    return [card for card in ENHANCED_CARDS.values() if card.difficulty_level == level]

def get_learning_path(path_name: str) -> Optional[Dict]:
    """获取学习路径"""
    return LEARNING_PATHS.get(path_name)

def get_trigram_combination_effect(upper: GuaType, lower: GuaType) -> Optional[Dict]:
    """获取卦象组合效果"""
    return TRIGRAM_COMBINATIONS.get((upper, lower))