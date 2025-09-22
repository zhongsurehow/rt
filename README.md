# 天机变·周天纪 - 易经主题策略游戏

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

> 融合中华易学智慧的多人策略游戏，在娱乐中传承传统文化

## 🚀 快速开始

### 立即体验 (Web 版本)
```bash
# 1. 进入Web应用目录
cd game_prototype/web_version

# 2. 安装依赖 (如果尚未安装)
pip install -r requirements.txt

# 3. 运行Web服务器
uvicorn app:app --reload --port 9000
```
然后，在浏览器中打开 `http://localhost:9000` 即可开始游戏。

### 新手指南
- 📖 [15分钟快速入门](QUICK_START.md) - 快速上手游戏
- 📚 [完整游戏规则](GAME_RULES.md) - 详细规则说明
- 🎯 [易经知识指南](YIJING_GUIDE.md) - 了解易经文化
- 🎮 [游戏原型说明](game_prototype/README.md) - 详细功能介绍

## 🎯 项目特色

### 💎 文化价值
- **易经主题** - 游戏的核心机制与卡牌设计均源于《易经》的八卦和哲理。
- **九宫格棋盘** - 采用后天八卦布局，符合传统易学理念。
- **文化传承** - 旨在通过现代游戏的方式，让更多人了解中华传统文化。

### 🎮 游戏特色
- **实时多人对战** - 基于WebSockets，支持2-4人实时在线对战。
- **核心战斗循环** - 已实现包括生命值、资源、卡牌效果、胜负判断在内的完整游戏循环。
- **互动教学系统** - 内置引导式教学，帮助新玩家快速上手。
- **策略卡牌玩法** - 围绕“气”资源管理和卡牌效果组合，构建基础策略深度。

### 🔧 技术亮点
- **FastAPI 后端** - 高性能的现代化Python Web框架。
- **Vue.js 前端** - 响应式的单页面应用，提供流畅的用户体验。
- **Pydantic 模型** - 统一和强类型的数据模型，确保了代码的健壮性。
- **模块化引擎** - 游戏核心逻辑采用模块化设计，易于扩展。

## 📁 项目结构

```
📁 项目根目录/
├── 📖 QUICK_START.md         # 15分钟快速入门
├── 📚 GAME_RULES.md          # 完整游戏规则
├── 🔧 DEVELOPMENT_GUIDE.md   # 开发者指南
└── 🎮 game_prototype/        # 游戏核心代码
    ├── core/                 # 核心引擎、接口和基础类型
    │   ├── game_engine.py
    │   └── interfaces.py
    ├── web_version/          # FastAPI Web应用
    │   ├── app.py            # 后端主程序
    │   ├── static/           # 静态文件 (CSS, JS, JSON数据)
    │   └── templates/        # 前端HTML模板 (Vue.js)
    ├── models.py             # Pydantic数据模型
    └── game_state.py         # 游戏状态类实现
```

## 🎮 游戏演示

项目已重构为Web应用。请按照 **[快速开始](#-快速开始)** 部分的指引运行服务器，然后在浏览器中体验游戏。所有旧的命令行演示脚本均已移除。

## 📖 核心玩法

### 🎯 游戏目标
通过打出卡牌、运用策略，将所有对手的 **生命值 (Health)** 降至0。

### ⚡ 基础概念
| 属性 | 说明 | 用途 |
|------|------|------|
| **生命值** | 玩家的生存能力 | 降至0则被淘汰 |
| **气** | 核心资源 | 用于支付打出卡牌的消耗 |
| **道行/诚意** | 玩家修为 | (在后续高级玩法中启用) |
| **阴/阳** | 能量倾向 | 影响特定卡牌的效果 |

### 🏆 胜利条件
- **击败对手**: 将任一对手的生命值降为0或更低，即可获胜（在多人游戏中为最后幸存者）。

> 💡 **新手建议**：先尝试传统胜利路径，熟悉游戏后再挑战其他路径

## 🔧 开发者信息

### 📋 系统要求
- **Python**: 3.11+
- **依赖**: FastAPI, Uvicorn, Python-Multipart, Jinja2 (详见 `requirements.txt`)
- **平台**: Windows/Linux/macOS

### 🛠️ 开发工具
- **IDE**: 推荐 VS Code 或 PyCharm
- **测试**: 内置单元测试框架
- **文档**: Markdown 格式

### 📚 详细文档
- 🔧 [开发者指南](DEVELOPMENT_GUIDE.md) - 完整开发文档
- 📖 [游戏规则](GAME_RULES.md) - 详细规则说明
- 🎯 [易经指南](YIJING_GUIDE.md) - 文化背景知识
- 📊 [审核报告](COMPREHENSIVE_REVIEW_REPORT.md) - 系统分析报告

## 🤝 参与贡献

### 🐛 问题反馈
- 使用 GitHub Issues 报告问题
- 提供详细的复现步骤
- 包含错误信息和环境信息

### 💡 功能建议
- 提交 Feature Request
- 说明功能的必要性和实现思路
- 考虑与易经文化的结合度

### 🔀 代码贡献
1. Fork 项目仓库
2. 创建功能分支
3. 编写代码和测试
4. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

感谢所有为中华传统文化传承和现代游戏设计做出贡献的开发者和学者。

---

> *"易有太极，是生两仪，两仪生四象，四象生八卦。"* - 《易经·系辞上》

**🌟 如果这个项目对你有帮助，请给我们一个 Star！**