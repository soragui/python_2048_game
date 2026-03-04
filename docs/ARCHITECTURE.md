# 🏗️ 2048 游戏架构文档

> 详细解释项目的模块设计、数据流和扩展方式

---

## 📋 目录

1. [整体架构图](#1-整体架构图)
2. [模块详解](#2-模块详解)
3. [数据流分析](#3-数据流分析)
4. [核心算法解析](#4-核心算法解析)
5. [扩展指南](#5-扩展指南)

---

## 1. 整体架构图

### 1.1 模块依赖关系

```
┌─────────────────────────────────────────────────────────────────┐
│                         app.py                                   │
│                    (应用入口/控制器)                              │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      ui.py                               │   │
│  │                  (用户界面层)                             │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │GameScreen│  │GridWidget│  │ScoreWidget│              │   │
│  │  └──────────┘  └──────────┘  └──────────┘              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      game.py                             │   │
│  │                  (游戏逻辑层)                             │   │
│  │                    class Game                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     models.py                            │   │
│  │                  (数据模型层)                             │   │
│  │               class Grid, class Tile                     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
         ↓                        ↓
   ┌──────────┐            ┌──────────┐
   │ config.py│            │ utils.py │
   │ (配置常量)│            │ (工具函数)│
   └──────────┘            └──────────┘
```

### 1.2 分层设计思想

| 层级 | 模块 | 职责 | 可独立测试 |
|------|------|------|-----------|
| **表示层** | `app.py`, `ui.py` | 处理用户输入、渲染界面 | ❌ 需要 UI |
| **业务层** | `game.py` | 游戏规则、移动、合并逻辑 | ✅ 纯逻辑 |
| **数据层** | `models.py` | 数据存储、序列化 | ✅ 纯数据 |
| **支撑层** | `config.py`, `utils.py` | 常量、工具函数 | ✅ 纯函数 |

**为什么这样分层？**

1. **可测试性** - 游戏逻辑可以脱离 UI 单独测试
2. **可替换性** - 可以轻松替换 UI（比如改成 Web 界面）
3. **可维护性** - 每个模块职责清晰，修改不影响其他模块

---

## 2. 模块详解

### 2.1 config.py - 配置中心

```python
# 所有可调整的游戏参数都在这里
GRID_SIZE: int = 4              # 4x4 网格
INITIAL_TILES: int = 2          # 初始生成 2 个方块
NEW_TILE_PROBABILITIES = {2: 0.9, 4: 0.1}  # 新方块概率
```

**设计原则：**
- 所有"魔法数字"都提取为常量
- 修改游戏行为只需改这里，不用深入代码
- 方便做游戏变体（比如 5x5 网格、不同生成概率）

### 2.2 models.py - 数据模型

#### Grid 类

```python
class Grid:
    """4x4 游戏棋盘。"""
    
    def __init__(self):
        self.cells: list[list[int]] = [[0,0,0,0], ...]  # 二维列表
    
    def __getitem__(self, position) -> int:  # grid[(row, col)] 访问
    def __setitem__(self, position, value)   # grid[(row, col)] = value
    def get_empty_cells(self) -> list[tuple] # 获取空位
    def spawn_tile(self) -> Optional[tuple]  # 生成新方块
```

**关键设计决策：**

| 决策 | 原因 |
|------|------|
| 用 `list[list[int]]` 存储 | 简单、直观、易序列化 |
| 0 表示空格 | 避免 `None` 判断，计算方便 |
| 实现 `__getitem__` | 支持 `grid[(r,c)]` 简洁语法 |
| 提供 `copy()` 方法 | 用于 AI 模拟（不修改原状态）|

### 2.3 game.py - 游戏核心

#### 移动算法详解

```python
def _slide_and_merge(self, line, ascending):
    """核心算法：滑动并合并一行。"""
    
    # 步骤 1: 移除零（空格）
    non_zero = [x for x in line if x != 0]
    
    # 步骤 2: 合并相邻相同值
    merged = []
    for i in range(len(non_zero)):
        if i+1 < len(non_zero) and non_zero[i] == non_zero[i+1]:
            merged.append(non_zero[i] * 2)  # 合并
            merge_score += non_zero[i] * 2
            skip_next = True
        else:
            merged.append(non_zero[i])
    
    # 步骤 3: 补齐零
    merged.extend([0] * (len(line) - len(merged)))
    
    return merged, merge_score
```

**算法可视化：**

```
原始：    [2, 0, 2, 0]
去零：    [2, 2]
合并：    [4]
补齐：    [4, 0, 0, 0]  ✓

原始：    [2, 2, 2, 2]
去零：    [2, 2, 2, 2]
合并：    [4, 4]        (第一对合并，第二对合并)
补齐：    [4, 4, 0, 0]  ✓

原始：    [2, 2, 4, 0]
去零：    [2, 2, 4]
合并：    [4, 4]        (2+2=4, 4 保持不变)
补齐：    [4, 4, 0, 0]  ✓
```

#### GameState 枚举

```python
class GameState(Enum):
    PLAYING = auto()    # 游戏中
    WON = auto()        # 达到 2048
    GAME_OVER = auto()  # 无步可走
```

**状态转换：**

```
                    ┌─────────────┐
                    │   PLAYING   │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ↓            ↓            ↓
         达到 2048    继续游戏    无步可走
              ↓            ↓            ↓
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │   WON    │  │ PLAYING  │  │GAME_OVER │
        └──────────┘  └──────────┘  └──────────┘
```

### 2.4 ui.py - 用户界面

#### 组件层次结构

```
GameScreen (主屏幕)
├── Label (标题 "🎮 2048")
├── Label (操作提示)
├── ScoreWidget (分数显示)
│   ├── Label (Score)
│   ├── Label (Moves)
│   └── Label (Max Tile)
└── GridWidget (游戏棋盘)
    ├── Horizontal (row 0)
    │   ├── TileWidget
    │   ├── TileWidget
    │   └── ...
    ├── Horizontal (row 1)
    └── ...
```

#### Textual 组件生命周期

```python
class GridWidget(Static):
    def __init__(self, game):
        # 1. 初始化（创建时调用一次）
        self.game = game
        self._create_tile_grid()
    
    def compose(self) -> ComposeResult:
        # 2. 组合子组件（渲染时调用）
        for row in range(4):
            yield Horizontal(...)
    
    def refresh_grid(self):
        # 3. 更新数据（游戏状态变化时调用）
        for tile_widget in self.tile_widgets:
            tile_widget.update_value(new_value)
```

### 2.5 app.py - 应用入口

#### 事件处理流程

```
用户按键
    ↓
Textual 事件系统
    ↓
Binding 匹配 (BINDINGS 列表)
    ↓
action_xxx() 方法
    ↓
self.game.move(direction)
    ↓
游戏状态更新
    ↓
self.refresh_display()
    ↓
UI 重新渲染
```

#### 键盘绑定

```python
BINDINGS = [
    # 方向键
    Binding("up", "move_up", "Up", show=False),
    Binding("down", "move_down", "Down", show=False),
    # ...
    
    # WASD
    Binding("w", "move_up", "W", show=False),
    # ...
    
    # 控制
    Binding("r", "restart", "Restart"),
    Binding("q", "quit", "Quit"),
]
```

**为什么同时支持方向键和 WASD？**
- 方向键：直观，传统游戏控制
- WASD：程序员习惯，某些终端方向键不工作

---

## 3. 数据流分析

### 3.1 完整游戏循环

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 游戏初始化                                                 │
│    Game.__init__() → Grid() → spawn initial tiles          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. 等待用户输入                                               │
│    Textual 事件循环监听键盘                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. 处理移动                                                   │
│    action_move_left() → game.move("left")                  │
│         ↓                                                    │
│    Game._move_left() → _move_row() → _slide_and_merge()   │
│         ↓                                                    │
│    更新 grid.cells, 计算分数                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. 生成新方块                                                 │
│    game.grid.spawn_tile()  (90% 生成 2, 10% 生成 4)          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. 检查游戏状态                                               │
│    Game._update_game_state()                                │
│         - 检查是否达到 2048 (赢)                              │
│         - 检查是否无步可走 (输)                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. 刷新 UI                                                   │
│    GameScreen.update_display()                              │
│         - ScoreWidget.update()                              │
│         - GridWidget.refresh_grid()                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    回到步骤 2 继续循环
```

### 3.2 状态同步

```
┌──────────────┐         ┌──────────────┐
│  Game 状态    │         │   UI 状态     │
│  (grid.cells)│         │ (TileWidget) │
└──────┬───────┘         └──────┬───────┘
       │                        │
       │  game.move()           │
       │  修改数据              │
       ↓                        │
┌──────────────┐                │
│  新状态       │                │
└──────┬───────┘                │
       │                        │
       │  refresh_display()     │
       │  (读取 Game 状态)        │
       └───────────────────────→│
                                │  update_value()
                                ↓
                       ┌──────────────┐
                       │  UI 更新完成  │
                       └──────────────┘
```

**关键点：**
- UI 不直接修改游戏数据
- 所有修改通过 `Game` 类的方法
- UI 只是游戏状态的"投影"

---

## 4. 核心算法解析

### 4.1 滑动合并算法

这是 2048 游戏的核心，让我们详细分析：

```python
def _slide_and_merge(line: list[int], ascending: bool):
    # 示例：向右移动 [2, 0, 2, 4]
    
    # 1. 去零
    non_zero = [2, 2, 4]  # 移除所有 0
    
    # 2. 如果向右/下，反转（从移动方向开始处理）
    if not ascending:  # 向右
        non_zero = [4, 2, 2]  # 反转
    
    # 3. 合并
    merged = []
    i = 0
    while i < len(non_zero):
        if i+1 < len(non_zero) and non_zero[i] == non_zero[i+1]:
            merged.append(non_zero[i] * 2)  # [4, 4]
            i += 2  # 跳过下一个
        else:
            merged.append(non_zero[i])
            i += 1
    
    # 4. 补齐
    merged.extend([0] * (4 - len(merged)))  # [4, 4, 0, 0]
    
    # 5. 如果向右/下，再反转回来
    if not ascending:
        merged = [0, 0, 4, 4]  # 反转回来
    
    return merged
```

### 4.2 游戏结束检测

```python
def _can_merge(self) -> bool:
    """检查是否有可合并的相邻方块。"""
    
    # 检查水平相邻
    for row in range(4):
        for col in range(3):  # 注意是 3 不是 4
            if grid[row][col] == grid[row][col+1]:
                return True  # 找到可合并的
    
    # 检查垂直相邻
    for col in range(4):
        for row in range(3):
            if grid[row][col] == grid[row+1][col]:
                return True
    
    return False  # 没有任何可合并的
```

**为什么游戏结束条件是 `is_full() and not _can_merge()`？**

- 只要有空格，就可以移动
- 即使满了，如果有相邻相同值，也可以合并
- 只有既满又无法合并时，才真正游戏结束

---

## 5. 扩展指南

### 5.1 修改网格大小

```python
# config.py
GRID_SIZE: int = 5  # 改成 5x5

# models.py 不需要修改（使用 GRID_SIZE 常量）
# game.py 不需要修改（使用 GRID_SIZE 常量）
# ui.py 可能需要调整 CSS 大小
```

### 5.2 添加新方块类型

```python
# config.py
NEW_TILE_PROBABILITIES = {
    2: 0.8,   # 80% 生成 2
    4: 0.15,  # 15% 生成 4
    8: 0.05,  # 5% 生成 8（疯狂模式！）
}
```

### 5.3 添加道具系统

```python
# game.py
class Game:
    def use_boost(self):
        """使用道具：临时允许一次额外移动。"""
        pass
    
    def use_undo(self):
        """使用道具：撤销上一步。"""
        self._history.pop()
        self.grid = self._history[-1].copy()
```

### 5.4 添加 AI 自动玩

```python
# ai.py
class AIPlayer:
    def __init__(self, game: Game):
        self.game = game
    
    def get_best_move(self) -> str:
        """使用期望最大化算法找到最佳移动。"""
        best_score = -1
        best_move = None
        
        for direction in DIRECTIONS:
            # 模拟移动
            test_game = self.game.copy()
            test_game.move(direction)
            score = self._evaluate(test_game)
            
            if score > best_score:
                best_score = score
                best_move = direction
        
        return best_move
```

### 5.5 添加动画

```python
# ui.py
class TileWidget(Static):
    def slide_to(self, new_row: int, new_col: int):
        """平滑移动到新位置。"""
        self.animate(
            "offset",
            Offset(self.col * TILE_SIZE, self.row * TILE_SIZE),
            duration=0.1
        )
```

---

## 📝 总结

### 架构亮点

1. **清晰分层** - UI、逻辑、数据完全分离
2. **配置驱动** - 所有可调参数集中在 config.py
3. **类型安全** - 全程类型注解
4. **文档完善** - 每个类、函数都有 docstring

### 学习收获

| 主题 | 学到的内容 |
|------|-----------|
| 模块化 | 如何组织多文件项目 |
| 算法 | 滑动合并的核心逻辑 |
| 状态机 | 游戏状态管理 |
| TUI | Textual 框架使用 |
| 设计模式 | 分离关注点、单一职责 |

### 下一步

- [ ] 实现 undo 功能
- [ ] 添加高分持久化
- [ ] 编写单元测试
- [ ] 添加动画效果

---

_理解架构后，修改和扩展就变得简单了！_ 🐧
