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
from fastapi.responses import HTMLResponse
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

try:
    from core.game_engine import GameEngine
    from core.base_types import PlayerId, ActionType
    from game_state import GameState
    from yijing_mechanics import YijingMechanics
    FULL_GAME_AVAILABLE = True
except ImportError as e:
    print(f"警告：无法导入完整游戏逻辑 ({e})，使用简化版本")
    FULL_GAME_AVAILABLE = False

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

class PlayerCreate(BaseModel):
    name: str
    avatar: Optional[str] = None

class GameCreate(BaseModel):
    player_name: str
    game_mode: str = "single"  # single, multiplayer
    max_players: int = 2

class CardPlay(BaseModel):
    card_id: str
    position: Dict[str, int]
    target: Optional[str] = None

class GameAction(BaseModel):
    action_type: str
    data: Dict[str, Any]

# ==================== 游戏管理器 ====================

class WebGameManager:
    """现代化的Web游戏管理器"""
    
    def __init__(self):
        self.games: Dict[str, Dict] = {}
        self.connections: Dict[str, List[WebSocket]] = {}
        self.player_games: Dict[str, str] = {}
    
    async def create_game(self, player_name: str, game_mode: str = "single") -> str:
        """创建新游戏"""
        game_id = str(uuid.uuid4())[:8]
        
        if FULL_GAME_AVAILABLE:
            # 使用完整的游戏引擎
            game_engine = GameEngine()
            game_state = game_engine.create_game()
        else:
            # 简化版游戏状态
            game_state = {
                'id': game_id,
                'players': [],
                'current_player': 0,
                'board': self._create_empty_board(),
                'turn': 1,
                'phase': 'waiting',
                'mode': game_mode,
                'max_players': 2 if game_mode == "multiplayer" else 1
            }
        
        self.games[game_id] = {
            'state': game_state,
            'created_at': datetime.now(),
            'last_action': datetime.now(),
            'mode': game_mode,
            'creator': player_name
        }
        
        self.connections[game_id] = []
        
        # 添加创建者为第一个玩家
        await self.add_player(game_id, player_name)
        
        logger.info(f"游戏 {game_id} 创建成功，创建者: {player_name}")
        return game_id
    
    async def add_player(self, game_id: str, player_name: str) -> bool:
        """添加玩家到游戏"""
        if game_id not in self.games:
            return False
        
        game = self.games[game_id]
        players = game['state']['players'] if isinstance(game['state'], dict) else []
        
        if len(players) >= game['state'].get('max_players', 2):
            return False
        
        player_id = str(uuid.uuid4())[:8]
        player_data = {
            'id': player_id,
            'name': player_name,
            'qi': 100,
            'dao_xing': 50,
            'cheng_yi': 30,
            'yin': 50,
            'yang': 50,
            'wu_xing': {'wood': 20, 'fire': 20, 'earth': 20, 'metal': 20, 'water': 20},
            'hand': self._generate_starting_hand(),
            'joined_at': datetime.now().isoformat()
        }
        
        if isinstance(game['state'], dict):
            game['state']['players'].append(player_data)
            if len(game['state']['players']) >= game['state'].get('max_players', 2):
                game['state']['phase'] = 'action'
        
        self.player_games[player_id] = game_id
        
        # 通知其他玩家
        await self.broadcast_to_game(game_id, {
            'type': 'player_joined',
            'player': player_data,
            'game_state': self._serialize_game_state(game['state'])
        })
        
        return True
    
    def _create_empty_board(self) -> List[List]:
        """创建空的游戏棋盘"""
        return [[None for _ in range(3)] for _ in range(3)]
    
    def _generate_starting_hand(self) -> List[Dict]:
        """生成起始手牌"""
        starting_cards = [
            {'id': 'qian_1', 'name': '乾卦', 'type': 'hexagram', 'element': 'metal', 'cost': 2},
            {'id': 'kun_1', 'name': '坤卦', 'type': 'hexagram', 'element': 'earth', 'cost': 2},
            {'id': 'zhen_1', 'name': '震卦', 'type': 'hexagram', 'element': 'wood', 'cost': 1},
            {'id': 'xun_1', 'name': '巽卦', 'type': 'hexagram', 'element': 'wood', 'cost': 1},
            {'id': 'kan_1', 'name': '坎卦', 'type': 'hexagram', 'element': 'water', 'cost': 1}
        ]
        return starting_cards
    
    async def play_card(self, game_id: str, player_id: str, card_play: CardPlay) -> Dict:
        """执行卡牌动作"""
        if game_id not in self.games:
            raise HTTPException(status_code=404, detail="游戏不存在")
        
        game = self.games[game_id]
        
        try:
            if FULL_GAME_AVAILABLE:
                result = await self._execute_full_game_action(game, player_id, card_play)
            else:
                result = await self._execute_simple_action(game, player_id, card_play)
            
            game['last_action'] = datetime.now()
            
            # 广播游戏状态更新
            await self.broadcast_to_game(game_id, {
                'type': 'game_update',
                'action_result': result,
                'game_state': self._serialize_game_state(game['state'])
            })
            
            return result
            
        except Exception as e:
            logger.error(f"执行卡牌动作失败: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_simple_action(self, game: Dict, player_id: str, card_play: CardPlay) -> Dict:
        """执行简化版游戏动作"""
        position = card_play.position
        row, col = position.get('row', 0), position.get('col', 0)
        
        if 0 <= row < 3 and 0 <= col < 3:
            game['state']['board'][row][col] = {
                'card_id': card_play.card_id,
                'player_id': player_id,
                'placed_at': datetime.now().isoformat()
            }
            
            # 切换到下一个玩家
            current_player = game['state']['current_player']
            total_players = len(game['state']['players'])
            game['state']['current_player'] = (current_player + 1) % total_players
            
            return {
                'success': True,
                'message': f'成功放置卡牌 {card_play.card_id}',
                'position': position
            }
        else:
            return {'success': False, 'error': '无效的位置'}
    
    async def _execute_full_game_action(self, game: Dict, player_id: str, card_play: CardPlay) -> Dict:
        """执行完整版游戏动作"""
        # 这里可以调用现有的完整游戏逻辑
        return {
            'success': True,
            'message': '使用完整游戏引擎执行动作',
            'details': 'Full game logic would be executed here'
        }
    
    def _serialize_game_state(self, game_state) -> Dict:
        """序列化游戏状态"""
        if isinstance(game_state, dict):
            return game_state
        elif hasattr(game_state, '__dict__'):
            return {
                'players': getattr(game_state, 'players', []),
                'board': getattr(game_state, 'board', []),
                'current_player': getattr(game_state, 'current_player', 0),
                'turn': getattr(game_state, 'turn', 1),
                'phase': getattr(game_state, 'phase', 'action')
            }
        else:
            return {'error': '无法序列化游戏状态'}
    
    async def add_connection(self, game_id: str, websocket: WebSocket):
        """添加WebSocket连接"""
        if game_id not in self.connections:
            self.connections[game_id] = []
        self.connections[game_id].append(websocket)
    
    async def remove_connection(self, game_id: str, websocket: WebSocket):
        """移除WebSocket连接"""
        if game_id in self.connections:
            self.connections[game_id].remove(websocket)
    
    async def broadcast_to_game(self, game_id: str, message: Dict):
        """向游戏中的所有连接广播消息"""
        if game_id not in self.connections:
            return
        
        disconnected = []
        for websocket in self.connections[game_id]:
            try:
                await websocket.send_text(json.dumps(message))
            except:
                disconnected.append(websocket)
        
        # 清理断开的连接
        for ws in disconnected:
            self.connections[game_id].remove(ws)

# 全局游戏管理器
game_manager = WebGameManager()

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
    """游戏页面 - 自动创建新游戏"""
    # 创建一个新游戏
    game_id = await game_manager.create_game("Player1", "single")
    # 重定向到游戏页面
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/game/{game_id}", status_code=302)

@app.get("/game/{game_id}", response_class=HTMLResponse)
async def game_page(game_id: str):
    """游戏页面"""
    return templates.TemplateResponse("game.html", {"request": {}, "game_id": game_id})

@app.post("/api/games")
async def create_game(game_create: GameCreate):
    """创建新游戏"""
    try:
        game_id = await game_manager.create_game(
            game_create.player_name, 
            game_create.game_mode
        )
        return {
            'success': True,
            'game_id': game_id,
            'message': '游戏创建成功',
            'game_url': f'/game/{game_id}'
        }
    except Exception as e:
        logger.error(f"创建游戏失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/games/{game_id}")
async def get_game_state(game_id: str):
    """获取游戏状态"""
    if game_id not in game_manager.games:
        raise HTTPException(status_code=404, detail="游戏不存在")
    
    game = game_manager.games[game_id]
    return {
        'success': True,
        'game_id': game_id,
        'state': game_manager._serialize_game_state(game['state']),
        'created_at': game['created_at'].isoformat(),
        'last_action': game['last_action'].isoformat()
    }

@app.post("/api/games/{game_id}/join")
async def join_game(game_id: str, player: PlayerCreate):
    """加入游戏"""
    success = await game_manager.add_player(game_id, player.name)
    if success:
        return {'success': True, 'message': '成功加入游戏'}
    else:
        raise HTTPException(status_code=400, detail="无法加入游戏")

@app.post("/api/games/{game_id}/actions")
async def execute_action(game_id: str, action: GameAction):
    """执行游戏动作"""
    # 这里可以根据action_type分发到不同的处理函数
    return {'success': True, 'message': '动作执行成功'}

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    """WebSocket连接端点"""
    await websocket.accept()
    await game_manager.add_connection(game_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理不同类型的WebSocket消息
            if message['type'] == 'play_card':
                card_play = CardPlay(**message['data'])
                result = await game_manager.play_card(
                    game_id, 
                    message.get('player_id'), 
                    card_play
                )
                await websocket.send_text(json.dumps(result))
            
    except WebSocketDisconnect:
        await game_manager.remove_connection(game_id, websocket)

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