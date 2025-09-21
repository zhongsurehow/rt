# 天机变游戏 Web版本 2.0

基于FastAPI + Vue.js + WebSocket的现代化Web游戏平台

## 🚀 特性

- ⚡ **高性能**: 基于FastAPI异步框架
- 🎮 **实时对战**: WebSocket支持多人实时游戏
- 📱 **响应式设计**: 完美支持手机/平板/电脑
- 🎨 **现代UI**: Vue.js 3 + Tailwind CSS
- 🔄 **代码复用**: 90%复用现有游戏逻辑
- 🐳 **容器化**: 支持Docker部署

## 🛠️ 技术栈

### 后端
- **FastAPI**: 现代Python Web框架
- **WebSocket**: 实时通信
- **SQLite/PostgreSQL**: 数据存储
- **Redis**: 缓存和会话管理

### 前端
- **Vue.js 3**: 渐进式JavaScript框架
- **TypeScript**: 类型安全
- **Tailwind CSS**: 实用优先的CSS框架
- **Socket.IO**: WebSocket客户端

## 📦 安装和运行

### 本地开发

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **启动服务器**
```bash
python app.py
```

3. **访问游戏**
- 游戏地址: http://localhost:9000
- API文档: http://localhost:9000/api/docs

### Docker部署

1. **构建镜像**
```bash
docker build -t tianjibian-web .
```

2. **运行容器**
```bash
docker run -p 9000:9000 tianjibian-web
```

### Docker Compose部署

```bash
# 启动完整服务栈
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 🎮 游戏功能

### 核心功能
- ✅ 单人游戏模式
- ✅ 多人实时对战
- ✅ 64卦系统
- ✅ 五行相生相克
- ✅ 阴阳平衡机制
- ✅ 实时聊天

### 界面功能
- ✅ 游戏大厅
- ✅ 房间创建/加入
- ✅ 实时游戏界面
- ✅ 玩家状态显示
- ✅ 游戏历史记录

## 🔧 配置

### 环境变量
```bash
# 数据库配置
DATABASE_URL=sqlite:///./tianjibian.db

# Redis配置
REDIS_URL=redis://localhost:6379

# 服务器配置
HOST=127.0.0.1
PORT=9000
DEBUG=false
```

### 生产环境配置
```bash
# 使用PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/tianjibian

# 使用外部Redis
REDIS_URL=redis://redis-server:6379

# 安全配置
SECRET_KEY=your-secret-key
CORS_ORIGINS=["https://yourdomain.com"]
```

## 📊 性能优化

### 已实现优化
- 异步处理所有I/O操作
- Redis缓存游戏状态
- WebSocket连接池管理
- 静态资源CDN支持
- 数据库连接池

### 监控指标
- 并发连接数
- 响应时间
- 内存使用率
- 数据库查询性能

## 🔒 安全特性

- CORS跨域保护
- WebSocket连接验证
- 输入数据验证
- SQL注入防护
- XSS攻击防护

## 🚀 部署指南

### 云服务器部署

1. **准备服务器**
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

2. **部署应用**
```bash
# 克隆代码
git clone <repository-url>
cd tianjibian-web

# 启动服务
docker-compose up -d
```

3. **配置域名**
```bash
# 配置Nginx
sudo nano /etc/nginx/sites-available/tianjibian

# 申请SSL证书
sudo certbot --nginx -d yourdomain.com
```

### 扩容方案
- 负载均衡: Nginx + 多个应用实例
- 数据库集群: PostgreSQL主从复制
- 缓存集群: Redis Cluster
- CDN加速: 静态资源分发

## 📈 监控和日志

### 日志配置
```python
# 日志级别
LOG_LEVEL=INFO

# 日志文件
LOG_FILE=/app/logs/tianjibian.log
```

### 监控工具
- Prometheus: 指标收集
- Grafana: 可视化监控
- ELK Stack: 日志分析

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License

## 🆘 故障排除

### 常见问题

**Q: 端口被占用**
```bash
# 查看端口占用
netstat -tulpn | grep :9000

# 杀死进程
sudo kill -9 <PID>
```

**Q: WebSocket连接失败**
- 检查防火墙设置
- 确认WebSocket支持
- 查看浏览器控制台错误

**Q: 游戏逻辑错误**
- 检查核心模块导入
- 确认游戏规则文件
- 查看服务器日志

### 联系支持
- 邮箱: support@tianjibian.com
- 文档: https://docs.tianjibian.com
- 社区: https://community.tianjibian.com