/**
 * 天机变游戏 WebSocket 客户端
 * 处理实时游戏通信和状态同步
 */

class GameWebSocket {
    constructor(gameId, callbacks = {}) {
        this.gameId = gameId;
        this.socket = null;
        this.callbacks = {
            onConnect: callbacks.onConnect || (() => {}),
            onDisconnect: callbacks.onDisconnect || (() => {}),
            onGameUpdate: callbacks.onGameUpdate || (() => {}),
            onGameEnd: callbacks.onGameEnd || (() => {}),
            onPlayerJoin: callbacks.onPlayerJoin || (() => {}),
            onPlayerLeave: callbacks.onPlayerLeave || (() => {}),
            onError: callbacks.onError || (() => {}),
            onMessage: callbacks.onMessage || (() => {})
        };
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.isConnected = false;
    }

    /**
     * 连接到WebSocket服务器
     */
    connect() {
        try {
            this.socket = io({
                transports: ['websocket', 'polling'],
                timeout: 5000,
                forceNew: true
            });

            this.setupEventHandlers();
            
        } catch (error) {
            console.error('WebSocket连接失败:', error);
            this.callbacks.onError({ type: 'connection_failed', message: '连接失败' });
        }
    }

    /**
     * 设置事件处理器
     */
    setupEventHandlers() {
        // 连接成功
        this.socket.on('connect', () => {
            console.log('WebSocket连接成功');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            
            // 加入游戏房间
            this.joinGame();
            
            this.callbacks.onConnect();
        });

        // 连接断开
        this.socket.on('disconnect', (reason) => {
            console.log('WebSocket连接断开:', reason);
            this.isConnected = false;
            this.callbacks.onDisconnect(reason);
            
            // 自动重连
            if (reason === 'io server disconnect') {
                // 服务器主动断开，不重连
                return;
            }
            
            this.attemptReconnect();
        });

        // 连接错误
        this.socket.on('connect_error', (error) => {
            console.error('WebSocket连接错误:', error);
            this.callbacks.onError({ type: 'connect_error', message: error.message });
            this.attemptReconnect();
        });

        // 游戏状态更新
        this.socket.on('game_update', (data) => {
            console.log('收到游戏状态更新:', data);
            this.callbacks.onGameUpdate(data);
        });

        // 游戏结束
        this.socket.on('game_ended', (data) => {
            console.log('游戏结束:', data);
            this.callbacks.onGameEnd(data);
        });

        // 玩家加入
        this.socket.on('player_joined', (data) => {
            console.log('玩家加入:', data);
            this.callbacks.onPlayerJoin(data);
        });

        // 玩家离开
        this.socket.on('player_left', (data) => {
            console.log('玩家离开:', data);
            this.callbacks.onPlayerLeave(data);
        });

        // 游戏消息
        this.socket.on('game_message', (data) => {
            console.log('收到游戏消息:', data);
            this.callbacks.onMessage(data);
        });

        // 错误消息
        this.socket.on('error', (data) => {
            console.error('收到错误消息:', data);
            this.callbacks.onError(data);
        });

        // 房间已满
        this.socket.on('room_full', (data) => {
            console.warn('房间已满:', data);
            this.callbacks.onError({ type: 'room_full', message: '游戏房间已满' });
        });

        // 游戏不存在
        this.socket.on('game_not_found', (data) => {
            console.error('游戏不存在:', data);
            this.callbacks.onError({ type: 'game_not_found', message: '游戏不存在' });
        });
    }

    /**
     * 加入游戏房间
     */
    joinGame() {
        if (!this.socket || !this.isConnected) {
            console.error('WebSocket未连接，无法加入游戏');
            return;
        }

        const playerId = this.getPlayerId();
        this.socket.emit('join_game', {
            game_id: this.gameId,
            player_id: playerId
        });
    }

    /**
     * 发送游戏动作
     */
    sendGameAction(action, data = {}) {
        if (!this.socket || !this.isConnected) {
            console.error('WebSocket未连接，无法发送动作');
            return false;
        }

        const payload = {
            game_id: this.gameId,
            player_id: this.getPlayerId(),
            action: action,
            data: data,
            timestamp: Date.now()
        };

        this.socket.emit('game_action', payload);
        return true;
    }

    /**
     * 出牌
     */
    playCard(cardId, position) {
        return this.sendGameAction('play_card', {
            card_id: cardId,
            position: position
        });
    }

    /**
     * 结束回合
     */
    endTurn() {
        return this.sendGameAction('end_turn');
    }

    /**
     * 投降
     */
    surrender() {
        return this.sendGameAction('surrender');
    }

    /**
     * 发送聊天消息
     */
    sendChatMessage(message) {
        return this.sendGameAction('chat_message', {
            message: message
        });
    }

    /**
     * 请求游戏状态
     */
    requestGameState() {
        if (!this.socket || !this.isConnected) {
            return false;
        }

        this.socket.emit('request_game_state', {
            game_id: this.gameId,
            player_id: this.getPlayerId()
        });
        return true;
    }

    /**
     * 尝试重连
     */
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('达到最大重连次数，停止重连');
            this.callbacks.onError({ 
                type: 'max_reconnect_attempts', 
                message: '连接失败，请刷新页面重试' 
            });
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
        
        console.log(`${delay}ms后尝试第${this.reconnectAttempts}次重连...`);
        
        setTimeout(() => {
            if (!this.isConnected) {
                this.connect();
            }
        }, delay);
    }

    /**
     * 获取玩家ID
     */
    getPlayerId() {
        let playerId = localStorage.getItem('player_id');
        if (!playerId) {
            playerId = 'player_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('player_id', playerId);
        }
        return playerId;
    }

    /**
     * 获取连接状态
     */
    getConnectionStatus() {
        return {
            connected: this.isConnected,
            reconnectAttempts: this.reconnectAttempts,
            socketId: this.socket ? this.socket.id : null
        };
    }

    /**
     * 断开连接
     */
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
        this.isConnected = false;
    }

    /**
     * 设置回调函数
     */
    setCallback(event, callback) {
        if (this.callbacks.hasOwnProperty(`on${event.charAt(0).toUpperCase() + event.slice(1)}`)) {
            this.callbacks[`on${event.charAt(0).toUpperCase() + event.slice(1)}`] = callback;
        }
    }

    /**
     * 发送心跳包
     */
    sendHeartbeat() {
        if (this.socket && this.isConnected) {
            this.socket.emit('heartbeat', {
                game_id: this.gameId,
                player_id: this.getPlayerId(),
                timestamp: Date.now()
            });
        }
    }

    /**
     * 启动心跳检测
     */
    startHeartbeat(interval = 30000) {
        this.heartbeatInterval = setInterval(() => {
            this.sendHeartbeat();
        }, interval);
    }

    /**
     * 停止心跳检测
     */
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }
}

// 导出类供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GameWebSocket;
} else if (typeof window !== 'undefined') {
    window.GameWebSocket = GameWebSocket;
}

/**
 * 创建WebSocket连接的便捷函数
 */
function createGameWebSocket(gameId, callbacks) {
    return new GameWebSocket(gameId, callbacks);
}

// 全局导出便捷函数
if (typeof window !== 'undefined') {
    window.createGameWebSocket = createGameWebSocket;
}