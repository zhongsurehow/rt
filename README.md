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
- **64卦完整体系** - 包含所有64卦及其爻辞
- **阴阳平衡机制** - 体现太极思想的游戏设计
- **五行相生相克** - 展现自然循环规律
- **天地人三才** - 传统哲学的现代演绎

### 🎮 游戏创新
- **多人对战支持** - 支持2-8人同时游戏
- **多元胜利路径** - 道行、分数、特殊成就等多种胜利方式
- **智慧教育系统** - 游戏中自然学习易经智慧
- **策略深度** - 丰富的战术选择和组合效应
- **平衡性测试** - 自动化平衡性测试和优化建议

### 🔧 技术亮点
- **模块化架构** - 清晰的代码组织和配置管理
- **增强系统** - 智慧、教学、成就、联盟等多个子系统
- **自动化测试** - 完整的测试套件和平衡性分析
- **配置管理** - 统一的游戏配置和参数调优

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
在易经八卦棋盘上通过策略布局，率先达到任一胜利条件

### ⚡ 基础概念
| 属性 | 说明 | 用途 |
|------|------|------|
| 气 | 行动力 | 打牌、移动、冥想 |
| 道行 | 修为等级 | 主要胜利条件 |
| 阴阳 | 平衡状态 | 影响奖励和能力 |
| 五行 | 元素亲和 | 特殊效果和胜利路径 |

### 🏆 胜利条件（达成任一即可）
1. **🎖️ 传统胜利** - 道行达到100点
2. **☯️ 阴阳大师** - 保持高度平衡5回合
3. **🌟 五行宗师** - 掌握所有五行元素
4. **🔄 变化之道** - 完成多次变卦转换

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