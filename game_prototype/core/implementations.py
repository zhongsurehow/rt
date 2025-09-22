from .interfaces import IEventBus, IConfigManager, IGameFactory, IPlayer, IGameState, IGameAction
from .base_types import GameEvent, PlayerId, ActionType, PlayerType, SystemType
from typing import Dict, List, Any, Callable, Optional
from ..game_state import Player, GameState

class SimpleEventBus(IEventBus):
    def subscribe(self, event_type: str, handler: Callable[[GameEvent], None], priority: int = 0) -> str:
        # No-op
        return ""
    def unsubscribe(self, subscription_id: str) -> bool:
        # No-op
        return True
    def publish(self, event: GameEvent) -> None:
        # No-op
        pass
    async def publish_async(self, event: GameEvent) -> None:
        # No-op
        pass
    def get_subscribers(self, event_type: str) -> List[str]:
        return []
    def clear_subscribers(self, event_type: Optional[str] = None) -> None:
        pass

class SimpleConfigManager(IConfigManager):
    def load_config(self, config_path: str) -> bool:
        return True
    def save_config(self, config_path: str) -> bool:
        return True
    def get_config(self, key: str, default: Any = None) -> Any:
        return default
    def set_config(self, key: str, value: Any) -> bool:
        return True
    def validate_config(self) -> List[str]:
        return []
    def get_all_configs(self) -> Dict[str, Any]:
        return {}
    def reset_to_defaults(self) -> None:
        pass
    def watch_config(self, key: str, callback: Callable[[str, Any, Any], None]) -> str:
        return ""
    def unwatch_config(self, watcher_id: str) -> bool:
        return True

class SimpleGameFactory(IGameFactory):
    def create_player(self, player_type: PlayerType, **kwargs: Any) -> IPlayer:
        return Player(**kwargs)
    def create_game_state(self, **kwargs: Any) -> IGameState:
        return GameState(**kwargs)
    def create_action(self, action_type: ActionType, **kwargs: Any) -> IGameAction:
        # This will need to be expanded
        return None
    def create_system(self, system_type: SystemType, **kwargs: Any):
        return None
    def create_event_bus(self, **kwargs: Any) -> IEventBus:
        return SimpleEventBus()
    def create_config_manager(self, **kwargs: Any) -> IConfigManager:
        return SimpleConfigManager()
    def register_creator(self, object_type: str, creator: Callable[..., Any]) -> None:
        pass
    def get_available_types(self, category: str) -> List[str]:
        return []
