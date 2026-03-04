# 第 2 章 项目结构与模块化

> "结构决定行为" —— 好的项目结构让开发更高效

---

## 📋 本章内容

- [项目目录总览](#项目目录总览)
- [为什么需要模块化](#为什么需要模块化)
- [模块详解](#模块详解)
- [pyproject.toml 解析](#pyprojecttoml-解析)
- [实践任务](#实践任务)

---

## 📁 项目目录总览

### 完整结构

```
game_2048/
├── .git/                    # Git 版本控制
├── .venv/                   # 虚拟环境（自动生成）
├── docs/                    # 文档目录
│   ├── TUTORIAL.md         # 教程总目录
│   ├── ARCHITECTURE.md     # 架构文档
│   ├── 01_overview.md      # 第 1 章
│   ├── 02_structure.md     # 第 2 章（本章）
│   └── ...
├── game_2048/               # 主包目录
│   ├── __init__.py         # 包标识
│   ├── app.py              # 应用入口
│   ├── config.py           # 配置常量
│   ├── game.py             # 游戏逻辑
│   ├── models.py           # 数据模型
│   ├── ui.py               # 界面组件
│   └── utils.py            # 工具函数
├── .gitignore               # Git 忽略规则
├── .python-version          # Python 版本
├── main.py                  # 备用入口
├── pyproject.toml           # 项目配置
├── README.md                # 项目说明
└── uv.lock                  # 依赖锁定
```

### 关键文件说明

| 文件/目录 | 作用 | 是否手写 |
|-----------|------|---------|
| `game_2048/` | 主代码包 | ✅ |
| `pyproject.toml` | 项目配置 | ✅ |
| `README.md` | 项目说明 | ✅ |
| `.gitignore` | Git 忽略 | ✅ |
| `.venv/` | 虚拟环境 | ❌ 自动生成 |
| `uv.lock` | 依赖锁定 | ❌ uv 生成 |

---

## 🧩 为什么需要模块化

### 问题：如果所有代码在一个文件里？

想象一下，如果 500 行代码都在 `game.py` 里：

```python
# ❌ 单文件地狱：game.py (500 行)

# 配置常量
GRID_SIZE = 4
...

# 数据类
class Tile:
    ...

class Grid:
    ...

# 游戏逻辑
class Game:
    ...

# UI 组件
class TileWidget:
    ...

class GridWidget:
    ...

# 应用入口
class GameApp:
    ...

# 工具函数
def print_grid():
    ...
```

**问题：**
1. 🔍 **难以导航** - 找一个函数要滚动很久
2. 🐛 **容易冲突** - 多人修改同一文件
3. 🧪 **难以测试** - 无法单独测试某个功能
4. 📖 **难以理解** - 新人不知道从哪里开始
5. 🔧 **难以维护** - 改一处可能影响多处

### 解决方案：模块化

```
✅ 模块化后：

config.py    → 配置常量（30 行）
models.py    → 数据模型（120 行）
game.py      → 游戏逻辑（200 行）
ui.py        → 界面组件（180 行）
app.py       → 应用入口（100 行）
utils.py     → 工具函数（80 行）
```

**好处：**
1. ✅ **易于导航** - 按功能分类，快速定位
2. ✅ **降低耦合** - 模块间依赖清晰
3. ✅ **便于测试** - 可单独测试每个模块
4. ✅ **团队协作** - 多人可并行开发不同模块
5. ✅ **代码复用** - 模块可在其他项目中使用

---

## 📦 模块详解

### 1. `__init__.py` - 包标识

```python
"""Game 2048 - A terminal-based 2048 game built with Textual."""

__version__ = "0.1.0"
```

**作用：**
- 告诉 Python 这是一个包（可导入的模块集合）
- 定义包的元信息（版本号、文档字符串）

**为什么需要它？**

```bash
# 没有 __init__.py
python -c "import game_2048"
# → ModuleNotFoundError

# 有 __init__.py
python -c "import game_2048"
# → 成功导入
```

---

### 2. `config.py` - 配置中心

```python
"""Game configuration and constants."""

# 网格大小
GRID_SIZE: int = 4

# 初始方块数
INITIAL_TILES: int = 2

# 新方块概率
NEW_TILE_PROBABILITIES: dict[int, float] = {
    2: 0.9,   # 90% 生成 2
    4: 0.1,   # 10% 生成 4
}

# 方向常量
DIRECTION_UP: str = "up"
DIRECTION_DOWN: str = "down"
DIRECTION_LEFT: str = "left"
DIRECTION_RIGHT: str = "right"
```

**设计思想：**
- 所有"魔法数字"集中管理
- 修改游戏行为只需改这里
- 其他模块通过导入使用常量

**使用示例：**

```python
# game.py
from .config import GRID_SIZE

for i in range(GRID_SIZE):  # 清晰！
    ...

# 而不是
for i in range(4):  # 4 是什么？
    ...
```

---

### 3. `models.py` - 数据模型

```python
"""Data models for the 2048 game."""

from dataclasses import dataclass

@dataclass
class Tile:
    """一个方块。"""
    value: int
    row: int
    col: int
    merged: bool = False
    new: bool = False

class Grid:
    """4x4 游戏棋盘。"""
    
    def __init__(self):
        self.cells: list[list[int]] = [...]
    
    def __getitem__(self, position) -> int:
        ...
    
    def spawn_tile(self) -> Optional[tuple[int, int]]:
        ...
```

**核心职责：**
- 定义数据结构
- 提供数据访问方法
- 处理序列化/反序列化

**为什么单独成模块？**
- 数据模型是业务逻辑的基础
- 可能被多个模块使用
- 便于独立测试

---

### 4. `game.py` - 游戏逻辑

```python
"""Core game logic for 2048."""

from enum import Enum

class GameState(Enum):
    PLAYING = auto()
    WON = auto()
    GAME_OVER = auto()

class Game:
    """游戏控制器。"""
    
    def __init__(self):
        self.grid = Grid()
        self.score = 0
        self.state = GameState.PLAYING
    
    def move(self, direction: str) -> bool:
        """移动方块。"""
        ...
    
    def _slide_and_merge(self, line, ascending):
        """核心算法：滑动合并。"""
        ...
```

**核心职责：**
- 实现游戏规则
- 处理移动和合并
- 管理游戏状态
- 计算分数

**关键特点：**
- **纯逻辑** - 不依赖 UI
- **可测试** - 可直接调用方法测试
- **无副作用** - 不修改外部状态

---

### 5. `ui.py` - 界面组件

```python
"""Textual TUI components for the 2048 game."""

from textual.app import ComposeResult
from textual.widgets import Static, Label

class TileWidget(Static):
    """单个方块组件。"""
    
    DEFAULT_CSS = """
    TileWidget {
        background: $surface;
        border: solid $primary;
    }
    """
    
    def render(self) -> str:
        return str(self.value)

class GridWidget(Static):
    """4x4 棋盘组件。"""
    
    def compose(self) -> ComposeResult:
        for row in range(GRID_SIZE):
            yield Horizontal(...)
```

**核心职责：**
- 定义界面组件
- 处理视觉渲染
- 响应用户交互

**设计原则：**
- **被动显示** - 只反映游戏状态，不修改
- **样式分离** - CSS 和逻辑分开
- **组件化** - 可复用的 UI 单元

---

### 6. `app.py` - 应用入口

```python
"""Main application entry point."""

from textual.app import App
from textual.binding import Binding

class Game2048App(App):
    """主应用。"""
    
    TITLE = "2048"
    
    BINDINGS = [
        Binding("up", "move_up", "Up"),
        Binding("r", "restart", "Restart"),
        Binding("q", "quit", "Quit"),
    ]
    
    def action_move_up(self):
        self.game.move("up")
        self.refresh_display()

def run_game():
    app = Game2048App()
    app.run()
```

**核心职责：**
- 初始化应用
- 注册事件绑定
- 协调各模块工作

**为什么单独成模块？**
- 应用入口是独立的关注点
- 便于创建不同的入口（CLI、GUI、Web）

---

### 7. `utils.py` - 工具函数

```python
"""Utility functions for the 2048 game."""

def get_tile_style(value: int) -> dict[str, str]:
    """获取方块的样式信息。"""
    styles = {
        2: {"bg": "gray60", "fg": "gray10"},
        4: {"bg": "gray55", "fg": "gray10"},
        ...
    }
    return styles.get(value, styles[2])

def format_number(value: int) -> str:
    """格式化大数字。"""
    if value >= 1000:
        return f"{value / 1000:.1f}k"
    return str(value)
```

**核心职责：**
- 提供辅助函数
- 处理格式化
- 工具类操作

**设计原则：**
- **无状态** - 函数不依赖外部状态
- **纯函数** - 相同输入总是相同输出
- **可复用** - 可在其他地方使用

---

## 📄 pyproject.toml 解析

### 完整配置

```toml
[project]
name = "game-2048"
version = "0.1.0"
description = "🎮 A terminal-based 2048 game built with Textual"
requires-python = ">=3.14"
dependencies = [
    "rich>=14.3.3",
    "textual>=8.0.2",
]

[project.scripts]
game-2048 = "game_2048.app:run_game"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 字段详解

| 字段 | 含义 | 示例值 |
|------|------|--------|
| `name` | 项目名称 | `"game-2048"` |
| `version` | 版本号（语义化版本） | `"0.1.0"` |
| `description` | 项目描述 | `"A terminal game..."` |
| `requires-python` | Python 版本要求 | `">=3.14"` |
| `dependencies` | 运行时依赖 | `["textual>=8.0.2"]` |
| `project.scripts` | 命令行入口 | `"game-2048 = ..."` |

### 命令行入口详解

```toml
[project.scripts]
game-2048 = "game_2048.app:run_game"
```

**含义：**
- 创建命令 `game-2048`
- 执行 `game_2048.app` 模块中的 `run_game` 函数

**等价于：**
```python
# 运行 game-2048 命令时
from game_2048.app import run_game
run_game()
```

---

## 🔗 模块依赖关系

### 依赖图

```
                    app.py
                      │
                      ↓
                    ui.py
                      │
                      ↓
                   game.py
                      │
                      ↓
                  models.py
                      │
         ┌────────────┴────────────┐
         ↓                         ↓
      config.py                utils.py
```

### 依赖规则

```python
# ✅ 正确：上层依赖下层
# app.py
from .game import Game
from .ui import GameScreen

# game.py
from .models import Grid

# models.py
from .config import GRID_SIZE

# ❌ 错误：下层依赖上层
# models.py 不应该导入 Game
# config.py 不应该导入任何模块
```

### 循环依赖问题

```python
# ❌ 错误：循环依赖
# game.py
from .ui import GameScreen  # Game 依赖 UI

# ui.py
from .game import Game  # UI 依赖 Game

# 结果：导入错误！

# ✅ 正确：单向依赖
# game.py - 不导入 UI
# ui.py - 导入 Game
```

---

## 🛠️ 实践任务

### 任务 1：探索项目结构

```bash
cd ~/Work/open_learn/python/game_2048

# 查看目录结构
tree -L 2 -I '.venv|__pycache__'

# 统计每个模块的代码行数
wc -l game_2048/*.py
```

### 任务 2：修改配置

```bash
# 编辑 config.py
nano game_2048/config.py

# 修改：
GRID_SIZE = 5  # 改成 5x5
NEW_TILE_PROBABILITIES = {2: 0.7, 4: 0.3}  # 增加 4 的概率

# 运行游戏观察变化
uv run game-2048
```

### 任务 3：添加调试输出

```python
# 在 game.py 的 move() 方法中添加
print(f"Moving {direction}, score: {self.score}")

# 运行游戏，观察输出
uv run game-2048
```

### 任务 4：创建新模块

```bash
# 创建动画模块
touch game_2048/animations.py

# 添加基础内容
cat > game_2048/animations.py << 'EOF'
"""Animation utilities for 2048."""

def animate_slide():
    """TODO: 实现滑动动画。"""
    pass
EOF
```

---

## ❓ 常见问题

### Q1: `__init__.py` 可以是空的吗？

**A:** 可以！空文件也能让 Python 识别为包。但建议添加文档字符串和版本号。

### Q2: 模块太多会不会太复杂？

**A:** 对于小项目可能显得多，但这是专业项目的标准结构。随着项目变大，优势会体现。

### Q3: 如何决定一个函数放在哪个模块？

**A:** 问自己：
- 这个函数操作数据吗？→ `models.py`
- 这个函数实现游戏规则吗？→ `game.py`
- 这个函数处理显示吗？→ `ui.py`
- 这个函数是通用工具吗？→ `utils.py`

---

## 📚 延伸阅读

- [Python 包和模块](https://docs.python.org/3/tutorial/modules.html)
- [pyproject.toml 规范](https://peps.python.org/pep-0621/)
- [Python 项目结构最佳实践](https://docs.python-guide.org/writing/structure/)

---

**下一章：** [第 3 章 数据模型设计](03_models.md)

🐧 _好的结构是成功的一半！_
