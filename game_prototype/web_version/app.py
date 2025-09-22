"""
天机变 Web版本 - FastAPI后端
现代化的Python Web应用，支持实时多人对战

技术栈：
- FastAPI: 高性能Web框架
- WebSocket: 实时通信
- SQLAlchemy: 数据库ORM
- Redis: 缓存和会话管理

作者: 天机变开发团队
版本: 2.0.0
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
import uuid
import asyncio
import logging
from datetime import datetime
import sys
import os

# 导入现有游戏逻辑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_prototype.core.game_engine import GameEngine, GameEngineConfig
from game_prototype.core.implementations import SimpleEventBus, SimpleConfigManager, SimpleGameFactory
from game_prototype.core.test_action import TestAction
from game_prototype.core.base_types import ActionType
from game_prototype.models import GameState, Player as PlayerData
from game_prototype.game_state import Player

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="天机变 Web版",
    description="融合易经哲学的策略卡牌游戏",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ==================== 数据模型 ====================

class GameAction(BaseModel):
    action_type: str
    data: Dict[str, Any]

class PlayerCreate(BaseModel):
    name: str

# ==================== 全局变量 ====================

# 存储游戏引擎实例
game_engines: Dict[str, GameEngine] = {}
# 存储每个游戏的WebSocket连接
connections: Dict[str, List[WebSocket]] = {}

# ==================== 辅助函数 ====================

def get_game_engine(game_id: str) -> GameEngine:
    """获取指定ID的游戏引擎，如果不存在则抛出HTTPException"""
    engine = game_engines.get(game_id)
    if not engine:
        raise HTTPException(status_code=404, detail="Game not found")
    return engine

async def broadcast_to_game(game_id: str, message: Dict):
    """向指定游戏的所有玩家广播消息"""
    if game_id in connections:
        disconnected_clients = []
        for connection in connections[game_id]:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                disconnected_clients.append(connection)
        # 清理断开的连接
        for client in disconnected_clients:
            connections[game_id].remove(client)

def _serialize_game_state(game_state: GameState) -> Dict:
    """将游戏状态对象序列化为字典"""
    # 使用Pydantic的model_dump方法，它会递归地将模型转为字典
    return game_state.model_dump(mode='json')

# ==================== API路由 ====================

@app.get("/", response_class=HTMLResponse)
async def index():
    """主页"""
    return templates.TemplateResponse("index.html", {"request": {}})

@app.get("/test", response_class=HTMLResponse)
async def test_page():
    """Vue.js测试页面"""
    return templates.TemplateResponse("test.html", {"request": {}})

@app.get("/debug", response_class=HTMLResponse)
async def debug_page():
    """调试页面"""
    return templates.TemplateResponse("debug.html", {"request": {}})

@app.get("/test-features", response_class=HTMLResponse)
async def test_features_page():
    """功能测试页面"""
    return templates.TemplateResponse("test_features.html", {"request": {}})

@app.get("/rules", response_class=HTMLResponse)
async def rules_page():
    """游戏规则页面"""
    return templates.TemplateResponse("rules.html", {"request": {}})

@app.get("/game", response_class=HTMLResponse)
async def game_redirect():
    """
    Redirects to a new game. This is a convenience endpoint for single-player testing.
    A proper application would have a lobby system.
    """
    # This is a temporary solution for single-player testing.
    # In a real app, you'd have a lobby, game creation UI, etc.
    player_name = f"Player_{str(uuid.uuid4())[:4]}"
    game_id = str(uuid.uuid4())[:8]

    engine = GameEngine(
        config_manager=SimpleConfigManager(),
        event_bus=SimpleEventBus(),
        game_factory=SimpleGameFactory(),
        engine_config=GameEngineConfig(debug_mode=True)
    )
    engine.initialize()

    player_id = str(uuid.uuid4())[:8]
    player = Player(id=player_id, name=player_name)
    engine.start_game([player])

    game_engines[game_id] = engine
    connections[game_id] = []

    from fastapi.responses import RedirectResponse
    # We need to pass the player_id to the client. We'll use a query parameter for this.
    response = RedirectResponse(url=f"/game/{game_id}?player_id={player_id}")
    return response

@app.get("/game/{game_id}", response_class=HTMLResponse)
async def game_page(game_id: str, request: Request):
    """游戏页面"""
    return templates.TemplateResponse("game.html", {"request": {}, "game_id": game_id})

@app.get("/api/cards")
async def get_all_cards():
    """获取所有卡牌数据"""
    cards_file_path = os.path.join("static", "data", "cards.json")
    if not os.path.exists(cards_file_path):
        raise HTTPException(status_code=404, detail="Card data file not found.")
    return FileResponse(cards_file_path)

@app.post("/api/games", status_code=201)
async def create_game(player_create: PlayerCreate, request: Request):
    """创建一个新的游戏会话"""
    game_id = str(uuid.uuid4())[:8]

    engine = GameEngine(
        config_manager=SimpleConfigManager(),
        event_bus=SimpleEventBus(),
        game_factory=SimpleGameFactory(),
        engine_config=GameEngineConfig(debug_mode=True)
    )
    engine.initialize()

    player_id = str(uuid.uuid4())[:8]
    player = Player(id=player_id, name=player_create.name)

    engine.start_game([player])

    game_engines[game_id] = engine
    connections[game_id] = []

    logger.info(f"New game created with ID: {game_id} by player {player_create.name}")
    
    return {
        "game_id": game_id,
        "player_id": player_id,
        "game_state": _serialize_game_state(engine.get_game_state())
    }

@app.post("/api/games/{game_id}/join")
async def join_game(game_id: str, player_create: PlayerCreate):
    """玩家加入一个已有的游戏"""
    engine = get_game_engine(game_id)

    if len(engine.current_session.players) >= engine.config.max_players:
        raise HTTPException(status_code=400, detail="Game is full")

    player_id = str(uuid.uuid4())[:8]
    player = Player(id=player_id, name=player_create.name)

    engine.current_session.add_player(player)

    # 更新游戏状态以包含新玩家
    game_state = engine.get_game_state()
    game_state.players[player.id] = player # Manually add player to state

    await broadcast_to_game(game_id, {
        "type": "player_joined",
        "player": player.model_dump(),
        "game_state": _serialize_game_state(game_state)
    })

    return {"player_id": player_id, "game_id": game_id}

@app.get("/api/games/{game_id}")
async def get_game_state(game_id: str):
    """获取指定游戏的当前状态"""
    engine = get_game_engine(game_id)
    return _serialize_game_state(engine.get_game_state())

@app.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    """WebSocket连接点，用于实时游戏通信"""
    engine = get_game_engine(game_id)
    player = engine.current_session.get_player(player_id)

    if not player:
        await websocket.close(code=4001, reason="Player not found")
        return

    await websocket.accept()
    if game_id not in connections:
        connections[game_id] = []
    connections[game_id].append(websocket)

    # Announce player join and send initial state
    await broadcast_to_game(game_id, {
        "type": "player_joined",
        "player": player.model_dump(),
    })

    await websocket.send_text(json.dumps(
        {"type": "game_state", "game_state": _serialize_game_state(engine.get_game_state())}
    ))

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            action_type_str = message.get("action_type")
            action_data = message.get("data", {})

            # Handle non-game-engine actions like chat
            if action_type_str and action_type_str.lower() == 'chat':
                chat_message = action_data.get("message", "")
                if chat_message:
                    logger.info(f"Player {player.name} sent chat: {chat_message}")
                    chat_payload = {
                        "type": "chat_message",
                        "data": {
                            "id": str(uuid.uuid4()),
                            "player": player.name,
                            "text": chat_message,
                            "timestamp": datetime.utcnow().isoformat() + "Z" # Add Z for UTC
                        }
                    }
                    await broadcast_to_game(game_id, chat_payload)
                continue # Skip engine processing for chat
            
            try:
                # Ensure action_type_str is not None before upper()
                if not action_type_str:
                    logger.warning("Received message without action_type")
                    continue
                action_type = ActionType[action_type_str.upper()]
                action = TestAction(player_id, action_type, action_data)

                result = engine.process_player_action(player_id, action)
                logger.info(f"Action result: {result}")

                # Add a log entry for the action
                game_state = engine.get_game_state()
                log_entry = {
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "player_name": player.name,
                    "action": action_type_str,
                    "data": action_data,
                    "result": result.message if result else "No result"
                }
                game_state.logs.append(log_entry)

            except (KeyError, AttributeError):
                logger.error(f"Invalid action type received: {action_type_str}")
                continue

            # 广播更新后的游戏状态
            await broadcast_to_game(game_id, {
                "type": "game_update",
                "game_state": _serialize_game_state(engine.get_game_state())
            })

    except WebSocketDisconnect:
        connections[game_id].remove(websocket)
        # 可选择广播玩家离开的消息
        await broadcast_to_game(game_id, {
            "type": "player_left",
            "player_id": player_id
        })

# ==================== 启动配置 ====================

if __name__ == "__main__":
    import uvicorn
    
    # 确保目录存在
    os.makedirs('web_version/templates', exist_ok=True)
    os.makedirs('web_version/static', exist_ok=True)
    
    print("🚀 天机变 Web版本 2.0 启动中...")
    print("⚡ 基于FastAPI + WebSocket")
    print("🎮 支持实时多人对战")
    print("📱 完美支持手机/平板/电脑")
    print("🌐 访问地址: http://localhost:9000")
    print("📚 API文档: http://localhost:9000/api/docs")
    
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=9000,
        reload=True,
        log_level="info"
    )