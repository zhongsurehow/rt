"""
新架构模块
独立的新架构实现，避免与现有系统冲突
"""

__version__ = "1.0.0"
__author__ = "天机变开发团队"

# 导出主要组件
from .effect_engine import EffectEngine
from .event_bus import EventBus, emit, on, GameEvents
from .strategy_patterns import get_strategy_manager
from .architecture_adapter import get_architecture_adapter, initialize_new_architecture

__all__ = [
    'EffectEngine',
    'EventBus', 
    'emit',
    'on', 
    'GameEvents',
    'get_strategy_manager',
    'get_architecture_adapter',
    'initialize_new_architecture'
]