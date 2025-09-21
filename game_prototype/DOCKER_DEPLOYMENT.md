# 天机变游戏 Docker 部署指南

## 🐳 部署概述

本游戏支持Docker容器化部署，**代码修改量极小**，主要是配置工作。

## 📋 部署选项

### 方案1：标准Docker部署
```bash
# 构建镜像
docker build -t tianjibian-game .

# 运行容器
docker run -d --name tianjibian \
  -v $(pwd)/saves:/app/saves \
  tianjibian-game
```

### 方案2：Docker Compose部署
```bash
# 启动服务
docker-compose up -d tianjibian-game

# 查看日志
docker-compose logs -f tianjibian-game
```

### 方案3：VNC远程访问
```bash
# 启动VNC版本
docker-compose up -d tianjibian-vnc

# 通过VNC客户端连接
# 地址: localhost:5901
# 密码: 无需密码
```

## 🖥️ 显示方式

### Linux/Mac 本地显示
```bash
# 允许Docker访问X11
xhost +local:docker

# 运行容器
docker run -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  tianjibian-game
```

### Windows 显示
1. **安装VcXsrv或Xming**
2. **启动X Server**
3. **设置DISPLAY环境变量**
```bash
docker run -e DISPLAY=host.docker.internal:0.0 \
  tianjibian-game
```

### 远程VNC访问
1. **启动VNC容器**
2. **使用VNC客户端连接**
3. **推荐客户端：**
   - TightVNC Viewer
   - RealVNC Viewer
   - 浏览器VNC（noVNC）

## 📁 文件持久化

### 游戏存档
```yaml
volumes:
  - ./saves:/app/saves
```

### 配置文件
```yaml
volumes:
  - ./game_config.json:/app/game_config.json
```

### 日志文件
```yaml
volumes:
  - ./logs:/app/logs
```

## 🔧 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| DISPLAY | :99 | 显示服务器地址 |
| PYTHONPATH | /app | Python路径 |
| GAME_MODE | gui | 游戏模式 |

## 🚀 快速启动

### 一键启动脚本
```bash
#!/bin/bash
# 构建并启动
docker-compose up --build -d

# 显示访问信息
echo "游戏已启动！"
echo "VNC访问: localhost:5901"
echo "日志查看: docker-compose logs -f"
```

## 🛠️ 故障排除

### 常见问题

**1. 显示问题**
```bash
# 检查X11转发
echo $DISPLAY
xhost +local:docker
```

**2. 权限问题**
```bash
# 修复文件权限
sudo chown -R $USER:$USER saves/
```

**3. 端口冲突**
```bash
# 检查端口占用
netstat -tulpn | grep :5901
```

### 调试命令
```bash
# 进入容器调试
docker exec -it tianjibian bash

# 查看容器日志
docker logs tianjibian

# 重启服务
docker-compose restart
```

## 📊 性能优化

### 资源限制
```yaml
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
```

### 镜像优化
```dockerfile
# 多阶段构建
FROM python:3.9-slim as builder
# ... 构建阶段

FROM python:3.9-slim as runtime
# ... 运行阶段
```

## 🔒 安全考虑

### 网络安全
```yaml
networks:
  game-network:
    driver: bridge
```

### 用户权限
```dockerfile
RUN useradd -m gameuser
USER gameuser
```

## 📈 监控和日志

### 健康检查
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import tkinter; print('OK')" || exit 1
```

### 日志配置
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🎯 总结

**修改量评估：**
- ✅ **代码修改：几乎为零**
- ✅ **配置文件：3个新文件**
- ✅ **部署脚本：1个新文件**
- ✅ **总工作量：1-2小时**

**优势：**
- 🚀 快速部署
- 🔄 环境一致性
- 📦 易于分发
- 🛡️ 隔离安全

tkinter的Docker化部署是完全可行的，修改量很小，主要是配置工作！