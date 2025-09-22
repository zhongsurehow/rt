from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class CardEffect(BaseModel):
    type: str
    value: int
    target: str

class Card(BaseModel):
    id: str
    name: str
    type: str
    category: Optional[str] = None
    element: str
    cost: int
    power: int
    description: str
    effect: Optional[str] = None
    link: Optional[str] = None

class Player(BaseModel):
    id: str
    name: str
    health: int = 20
    qi: int = 100
    dao: int = 50
    sincerity: int = 50
    yin: int = 50
    yang: int = 50
    elements: Dict[str, int] = Field(default_factory=dict)
    hand: List[Card] = Field(default_factory=list)
    is_bot: bool = False
    online: bool = True

class GameState(BaseModel):
    game_id: str
    players: Dict[str, Player] = Field(default_factory=dict)
    current_player_id: Optional[str] = None
    turn: int = 1
    phase: str = "setup"
    board: Dict[str, Optional[str]] = Field(default_factory=dict) # position -> card_id
    season: str = "春"
    wuxing: str = "木"
    ganzhi: str = "甲子"
    jieqi: str = "立春"
    discard_pile: List[str] = Field(default_factory=list)
    logs: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "waiting_for_players"
    winner: Optional[str] = None
