# 天机变游戏 Docker 配置
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3-tk \
    xvfb \
    x11-utils \
    && rm -rf /var/lib/apt/lists/*

# 复制游戏文件
COPY . /app/

# 设置环境变量
ENV DISPLAY=:99
ENV PYTHONPATH=/app

# 创建启动脚本
RUN echo '#!/bin/bash\n\
# 启动虚拟显示\n\
Xvfb :99 -screen 0 1024x768x24 &\n\
sleep 2\n\
# 启动游戏\n\
python simple_gui_game.py' > /app/start.sh && \
    chmod +x /app/start.sh

# 暴露端口（如果需要）
EXPOSE 8000

# 启动命令
CMD ["/app/start.sh"]