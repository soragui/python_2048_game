# 第 3 章 数据模型设计

> "数据结构是程序的灵魂" —— 好的数据设计让逻辑更清晰

---

## 📋 本章内容

- [数据模型的重要性](#数据模型的重要性)
- [dataclass详解](#dataclass 详解)
- [Grid 类的设计](#grid-类的设计)
- [数据持久化](#数据持久化)
- [实践任务](#实践任务)

---

## 💡 数据模型的重要性

### 什么是数据模型？

> 数据模型是对现实世界事物的抽象表示。

**2048 中的数据模型：**

```
现实世界              →              代码表示

游戏棋盘             →              Grid 类
┌────┬────┬────┬────┐               - cells: 4x4 二维列表
│ 2  │    │ 4  │    │               - 每个位置存储数字
├────┼────┼────┼────┤
│    │ 8  │    │    │
├────┼────┼────┼────┤
│ 4  │    │ 2  │    │
├────┼────┼────┼────┤
│    │    │    │ 4  │
└────┴────┴────┴────┘

单个方块             →              Tile 类
- 数值：2048         →              - value: int
- 位置：(3, 3)       →              - row: int, col: int
- 状态：新生成        →              - new: bool
```

### 为什么数据模型很重要？

```
❌ 糟糕的数据设计：
game_data = [[2,0,4,0], [0,8,0,0], ...]  # 纯列表
# 问题：
# - 不知道每个数字代表什么
# - 难以添加新属性（如方块颜色）
# - 容易出错（行列搞反）

✅ 好的数据设计：
class Grid:
    cells: list[list[int]]
    
    def __getitem__(self, pos) -> int:
        return self.cells[row][col]

grid = Grid()
value = grid[(2, 3)]  # 清晰！
```

**好处：**
1. ✅ **自文档化** - 代码自己说明意图
2. ✅ **类型安全** - IDE 可以检查错误
3. ✅ **易扩展** - 添加新属性不影响现有代码
4. ✅ **易维护** - 修改数据结构集中在一处

---

## 📦 dataclass 详解

### 什么是 dataclass？

> dataclass 是 Python 3.7+ 的装饰器，自动生成样板代码。

### 传统写法 vs dataclass

```python
# ❌ 传统写法（繁琐）
class Tile:
    def __init__(self, value, row, col, merged=False, new=False):
        self.value = value
        self.row = row
        self.col = col
        self.merged = merged
        self.new = new
    
    def __repr__(self):
        return f"Tile(value={self.value}, row={self.row}, col={self.col})"
    
    def __eq__(self, other):
        if not isinstance(other, Tile):
            return False
        return (self.value, self.row, self.col) == \
               (other.value, other.row, other.col)

# ✅ dataclass 写法（简洁）
from dataclasses import dataclass

@dataclass
class Tile:
    value: int
    row: int
    col: int
    merged: bool = False
    new: bool = False
```

**自动生成的代码：**
- `__init__()` - 构造函数
- `__repr__()` - 字符串表示
- `__eq__()` - 相等比较
- 其他实用方法

### 代码对比

```python
# 传统写法：50+ 行
class Tile:
    def __init__(self, value, row, col, merged=False, new=False):
        self.value = value
        self.row = row
        self.col = col
        self.merged = merged
        self.new = new
    
    def __repr__(self):
        return f"Tile(value={self.value}, ...)"
    
    def __eq__(self, other):
        ...
    
    def __hash__(self):
        ...

# dataclass：5 行！
@dataclass
class Tile:
    value: int
    row: int
    col: int
    merged: bool = False
    new: bool = False
```

### dataclass 高级特性

#### 1. 默认值

```python
@dataclass
class Tile:
    value: int
    row: int = 0  # 默认值
    col: int = 0
    merged: bool = False
```

#### 2. 字段类型

```python
from typing import Optional, List

@dataclass
class Game:
    grid: Grid
    score: int = 0
    history: List[Grid] = None  # 可变默认值要小心！
    winner: Optional[str] = None
```

#### 3. 后初始化处理

```python
@dataclass
class Tile:
    value: int
    row: int
    col: int
    created_at: str = ""
    
    def __post_init__(self):
        """初始化后自动调用。"""
        if not self.created_at:
            from datetime import datetime
            self.created_at = datetime.now().isoformat()
```

#### 4. 转换为字典

```python
from dataclasses import asdict

tile = Tile(value=2048, row=3, col=3)
data = asdict(tile)
# {'value': 2048, 'row': 3, 'col': 3, ...}

# 用于 JSON 序列化
import json
json_str = json.dumps(data)
```

---

## 📊 Grid 类的设计

### 完整代码

```python
# models.py
from dataclasses import dataclass
from typing import Optional
from copy import deepcopy
from .config import GRID_SIZE

class Grid:
    """4x4 游戏棋盘。"""
    
    def __init__(self):
        """初始化空棋盘。"""
        self.cells: list[list[int]] = self._create_empty_grid()
    
    def _create_empty_grid(self) -> list[list[int]]:
        """创建空的 GRID_SIZE x GRID_SIZE 网格。"""
        return [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    def clear(self) -> None:
        """重置棋盘。"""
        self.cells = self._create_empty_grid()
    
    def __getitem__(self, position: tuple[int, int]) -> int:
        """获取指定位置的值。"""
        row, col = position
        return self.cells[row][col]
    
    def __setitem__(self, position: tuple[int, int], value: int) -> None:
        """设置指定位置的值。"""
        row, col = position
        self.cells[row][col] = value
    
    def get_empty_cells(self) -> list[tuple[int, int]]:
        """获取所有空位置。"""
        empty = []
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.cells[row][col] == 0:
                    empty.append((row, col))
        return empty
    
    def spawn_tile(self) -> Optional[tuple[int, int]]:
        """在随机空位置生成新方块。"""
        import random
        
        empty_cells = self.get_empty_cells()
        if not empty_cells:
            return None
        
        row, col = random.choice(empty_cells)
        value = 2 if random.random() < 0.9 else 4
        self.cells[row][col] = value
        
        return (row, col)
    
    def is_full(self) -> bool:
        """检查棋盘是否已满。"""
        return not self.has_empty_cells()
    
    def get_max_tile(self) -> int:
        """获取最大方块值。"""
        return max(max(row) for row in self.cells)
    
    def copy(self) -> 'Grid':
        """创建深拷贝。"""
        new_grid = Grid()
        new_grid.cells = deepcopy(self.cells)
        return new_grid
```

### 设计决策详解

#### 决策 1：用二维列表存储

```python
self.cells: list[list[int]] = [
    [0, 2, 0, 4],
    [0, 0, 8, 0],
    [2, 0, 0, 2],
    [0, 0, 0, 4]
]
```

**为什么？**
- ✅ 直观：`cells[row][col]` 对应棋盘位置
- ✅ 高效：列表访问是 O(1)
- ✅ 易序列化：可直接转 JSON

**替代方案：**
```python
# 方案 2：一维列表
cells = [0, 2, 0, 4, 0, 0, 8, 0, ...]  # 16 个元素
# 问题：需要计算索引 cells[row * 4 + col]

# 方案 3：字典
cells = {(0, 1): 2, (0, 3): 4, ...}
# 问题：遍历不方便，内存开销大
```

#### 决策 2：0 表示空格

```python
if self.cells[row][col] == 0:  # 空格
    ...
```

**为什么？**
- ✅ 简单：不需要 `None` 判断
- ✅ 计算方便：0 参与运算不影响结果
- ✅ 节省内存：整数比 `None` 对象小

**替代方案：**
```python
# 方案 2：用 None 表示空格
cells = [[None, 2, None, 4], ...]
# 问题：每次访问都要检查 None

# 方案 3：用 -1 表示空格
# 问题：不直观，容易混淆
```

#### 决策 3：实现 `__getitem__` 和 `__setitem__`

```python
# 支持这种语法
value = grid[(2, 3)]  # 调用 __getitem__
grid[(2, 3)] = 8      # 调用 __setitem__
```

**为什么？**
- ✅ Pythonic：符合 Python 习惯
- ✅ 简洁：比 `grid.get_cell(2, 3)` 更短
- ✅ 安全：可以添加边界检查

#### 决策 4：提供 `copy()` 方法

```python
def copy(self) -> 'Grid':
    """创建深拷贝。"""
    new_grid = Grid()
    new_grid.cells = deepcopy(self.cells)
    return new_grid
```

**为什么需要拷贝？**
- AI 算法需要模拟移动（不改变真实状态）
- undo 功能需要保存历史状态
- 测试时需要独立的状态副本

---

## 💾 数据持久化

### 为什么要持久化？

```
用户玩游戏
    ↓
关闭终端
    ↓
下次打开 → 游戏进度丢失 😢

如果有持久化：
关闭终端 → 保存到文件
下次打开 → 从文件加载 → 继续游戏 😊
```

### 序列化方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| JSON | 人类可读，跨语言 | 不支持复杂类型 | 配置文件，简单数据 |
| Pickle | 支持任意 Python 对象 | 不安全，Python 专用 | 临时缓存 |
| SQLite | 支持查询，事务 | 重量级 | 复杂数据，多用户 |
| YAML | 人类可读，支持注释 | 解析慢 | 配置文件 |

**2048 的选择：JSON**
- 数据结构简单（嵌套列表）
- 需要人类可读（调试方便）
- 跨平台兼容

### 序列化实现

```python
import json
from pathlib import Path
from dataclasses import asdict

class Grid:
    # ... 其他方法 ...
    
    def to_dict(self) -> dict:
        """序列化为字典。"""
        return {
            "cells": self.cells,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Grid':
        """从字典反序列化。"""
        grid = cls()
        grid.cells = data["cells"]
        return grid

# 保存
grid = Grid()
data = grid.to_dict()
Path("save.json").write_text(json.dumps(data))

# 加载
data = json.loads(Path("save.json").read_text())
grid = Grid.from_dict(data)
```

### 完整游戏保存

```python
class Game:
    def save(self, path: str) -> None:
        """保存游戏到文件。"""
        data = {
            "grid": self.grid.to_dict(),
            "score": self.score,
            "moves": self.moves,
            "state": self.state.name,
        }
        Path(path).write_text(json.dumps(data, indent=2))
    
    @classmethod
    def load(cls, path: str) -> 'Game':
        """从文件加载游戏。"""
        data = json.loads(Path(path).read_text())
        game = cls()
        game.grid = Grid.from_dict(data["grid"])
        game.score = data["score"]
        game.moves = data["moves"]
        game.state = GameState[data["state"]]
        return game
```

---

## 🔍 代码走读

### 示例 1：生成新方块

```python
def spawn_tile(self) -> Optional[tuple[int, int]]:
    """在随机空位置生成新方块。"""
    import random
    
    # 步骤 1：获取所有空位置
    empty_cells = self.get_empty_cells()
    
    # 步骤 2：检查是否有空位
    if not empty_cells:
        return None  # 没有空位，返回 None
    
    # 步骤 3：随机选择一个空位
    row, col = random.choice(empty_cells)
    
    # 步骤 4：决定生成的值（90% 是 2，10% 是 4）
    value = 2 if random.random() < 0.9 else 4
    
    # 步骤 5：设置值并返回位置
    self.cells[row][col] = value
    return (row, col)
```

**调用示例：**
```python
grid = Grid()
pos = grid.spawn_tile()
if pos:
    print(f"Spawned tile at {pos}")
```

### 示例 2：检查游戏结束

```python
def is_game_over(self) -> bool:
    """检查游戏是否结束。"""
    # 条件 1：还有空位 → 没结束
    if self.has_empty_cells():
        return False
    
    # 条件 2：有可合并的相邻方块 → 没结束
    if self.can_merge():
        return False
    
    # 既没空位又不能合并 → 结束
    return True

def can_merge(self) -> bool:
    """检查是否有可合并的相邻方块。"""
    # 检查水平方向
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE - 1):
            if self.cells[row][col] == self.cells[row][col + 1]:
                return True
    
    # 检查垂直方向
    for col in range(GRID_SIZE):
        for row in range(GRID_SIZE - 1):
            if self.cells[row][col] == self.cells[row + 1][col]:
                return True
    
    return False
```

**逻辑图解：**
```
游戏结束？
    │
    ├─ 有空位？─ 是 ─→ 未结束
    │      否
    │      ↓
    ├─ 可合并？─ 是 ─→ 未结束
    │      否
    │      ↓
    └──────→ 游戏结束
```

---

## 🛠️ 实践任务

### 任务 1：添加历史记录

```python
# 在 Game 类中添加
class Game:
    def __init__(self):
        self.history: list[Grid] = []
    
    def move(self, direction: str) -> bool:
        # 移动前保存当前状态
        self.history.append(self.grid.copy())
        
        # ... 移动逻辑 ...
    
    def undo(self) -> bool:
        """撤销上一步。"""
        if not self.history:
            return False
        self.grid = self.history.pop()
        return True
```

### 任务 2：实现棋盘打印

```python
def print_grid(self) -> None:
    """打印棋盘到控制台（调试用）。"""
    print("+----" * GRID_SIZE + "+")
    for row in self.cells:
        line = "|"
        for cell in row:
            if cell == 0:
                line += "    |"
            else:
                line += f"{cell:4}|"
        print(line)
        print("+----" * len(row) + "+")

# 测试
grid = Grid()
grid.spawn_tile()
grid.print_grid()
```

### 任务 3：添加边界检查

```python
def __getitem__(self, position: tuple[int, int]) -> int:
    """获取指定位置的值（带边界检查）。"""
    row, col = position
    if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
        raise IndexError(f"Position ({row}, {col}) out of bounds")
    return self.cells[row][col]
```

### 任务 4：性能测试

```python
import time

# 测试 Grid 操作性能
grid = Grid()
start = time.time()
for _ in range(10000):
    grid.spawn_tile()
    grid.get_empty_cells()
    grid.is_full()
end = time.time()
print(f"10000 次操作耗时：{end - start:.3f}秒")
```

---

## ❓ 常见问题

### Q1: 为什么不用 NumPy 数组？

**A:** NumPy 适合数值计算，但 2048 的数据结构简单，用标准列表就够了。而且列表更易序列化。

### Q2: dataclass 和普通类有什么区别？

**A:** dataclass 自动生成 `__init__`、`__repr__` 等方法，减少样板代码。普通类需要手写这些方法。

### Q3: 如何调试数据模型？

**A:** 
```python
# 1. 打印对象
print(grid)  # 需要实现 __str__

# 2. 使用 repr
repr(grid)   # dataclass 自动生成

# 3. 转为字典查看
from dataclasses import asdict
print(asdict(tile))
```

---

## 📚 延伸阅读

- [dataclasses 官方文档](https://docs.python.org/3/library/dataclasses.html)
- [Python 数据模型](https://docs.python.org/3/reference/datamodel.html)
- [序列化最佳实践](https://realpython.com/python-json/)

---

**下一章：** [第 4 章 游戏核心逻辑](04_game_logic.md)

🐧 _好的数据设计是成功的一半！_
