from typing import Dict, Any
from .interfaces import IGameAction, IGameState
from .base_types import PlayerId, ActionType, ActionResult, ResourceType

class TestAction(IGameAction):
    def __init__(self, player_id: PlayerId, action_type: ActionType, data: Dict[str, Any]):
        self._player_id = player_id
        self._action_type = action_type
        self.data = data

    @property
    def action_type(self) -> ActionType:
        return self._action_type

    @property
    def player_id(self) -> PlayerId:
        return self._player_id

    @property
    def cost(self) -> Dict[ResourceType, int]:
        return {}

    @property
    def description(self) -> str:
        return f"Test action of type {self.action_type}"

    def can_execute(self, player_id: PlayerId, game_state: IGameState) -> bool:
        return True

    def execute(self, player_id: PlayerId, game_state: IGameState) -> ActionResult:
        return ActionResult(success=True, message=f"Executed {self.action_type}")

    def validate(self, player_id: PlayerId, game_state: IGameState) -> bool:
        return True

    def get_preview(self, player_id: PlayerId, game_state: IGameState) -> Dict[str, Any]:
        return {}
