# 第 4 章 游戏核心逻辑

> "逻辑是游戏的心脏" —— 理解 2048 的核心算法

---

## 📋 本章内容

- [游戏逻辑概述](#游戏逻辑概述)
- [核心算法：滑动合并](#核心算法滑动合并)
- [游戏状态管理](#游戏状态管理)
- [胜负判定](#胜负判定)
- [代码走读](#代码走读)
- [实践任务](#实践任务)

---

## 🎮 游戏逻辑概述

### Game 类职责

```python
class Game:
    """游戏控制器。"""
    
    def __init__(self):
        self.grid = Grid()      # 棋盘
        self.score = 0          # 分数
        self.moves = 0          # 移动次数
        self.state = PLAYING    # 游戏状态
    
    def move(self, direction)   # 移动方块
    def reset(self)             # 重新开始
    def get_stats(self)         # 获取统计信息
```

**核心职责：**
1. 处理用户移动输入
2. 执行滑动合并算法
3. 管理游戏状态（进行中/胜利/失败）
4. 计算分数

### 移动流程

```
用户按下 ← 键
    ↓
Game.move("left")
    ↓
┌─────────────────────────────┐
│ 1. 检查是否可移动            │
│ 2. 执行滑动合并              │
│ 3. 计算本次得分              │
│ 4. 生成新方块                │
│ 5. 更新游戏状态              │
└─────────────────────────────┘
    ↓
返回是否成功移动
```

---

## 🔧 核心算法：滑动合并

### 算法详解

这是 2048 最核心的算法，让我们逐步拆解：

```python
def _slide_and_merge(self, line: list[int], ascending: bool):
    """
    滑动并合并一行。
    
    参数：
        line: 一行数据，如 [2, 0, 2, 4]
        ascending: True=向左/上，False=向右/下
    
    返回：
        (new_line, merge_score)
    """
    
    # 步骤 1：移除零（空格）
    non_zero = [x for x in line if x != 0]
    # [2, 0, 2, 4] → [2, 2, 4]
    
    # 步骤 2：根据方向决定是否反转
    if not ascending:  # 向右/下移动
        non_zero = non_zero[::-1]
    # 向右：[2, 2, 4] → [4, 2, 2]
    
    # 步骤 3：合并相邻相同值
    merged = []
    merge_score = 0
    skip_next = False
    
    for i in range(len(non_zero)):
        if skip_next:
            skip_next = False
            continue
        
        # 检查是否能和下一个合并
        if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
            # 合并！
            new_value = non_zero[i] * 2
            merged.append(new_value)
            merge_score += new_value  # 得分 = 合并后的值
            skip_next = True  # 跳过下一个（已合并）
        else:
            merged.append(non_zero[i])
    
    # 步骤 4：补齐零
    merged.extend([0] * (len(line) - len(merged)))
    # [4, 4] → [4, 4, 0, 0]
    
    # 步骤 5：如果向右/下，再反转回来
    if not ascending:
        merged = merged[::-1]
    # 向右：[4, 4, 0, 0] → [0, 0, 4, 4]
    
    return merged, merge_score
```

### 算法可视化

#### 示例 1：向左滑动

```
原始：  [2, 0, 2, 4]

步骤 1（去零）：[2, 2, 4]

步骤 2（ascending=True，不反转）：[2, 2, 4]

步骤 3（合并）：
  i=0: 2 == 2 → 合并为 4，skip_next=True
  i=1: 跳过
  i=2: 4 无相邻 → 保持 4
  结果：[4, 4]

步骤 4（补齐）：[4, 4, 0, 0]

步骤 5（不反转）：[4, 4, 0, 0]

最终：  [4, 4, 0, 0]  得分：4
```

#### 示例 2：向右滑动

```
原始：  [2, 2, 4, 0]

步骤 1（去零）：[2, 2, 4]

步骤 2（ascending=False，反转）：[4, 2, 2]

步骤 3（合并）：
  i=0: 4 ≠ 2 → 保持 4
  i=1: 2 == 2 → 合并为 4，skip_next=True
  i=2: 跳过
  结果：[4, 4]

步骤 4（补齐）：[4, 4, 0, 0]

步骤 5（反转回来）：[0, 0, 4, 4]

最终：  [0, 0, 4, 4]  得分：4
```

#### 示例 3：连续合并

```
原始：  [2, 2, 2, 2]

步骤 1（去零）：[2, 2, 2, 2]

步骤 3（合并）：
  i=0: 2 == 2 → 合并为 4，skip_next=True
  i=1: 跳过
  i=2: 2 == 2 → 合并为 4，skip_next=True
  i=3: 跳过
  结果：[4, 4]

最终：  [4, 4, 0, 0]  得分：8

⚠️ 注意：一次移动中，每个方块只能合并一次！
```

### 为什么算法要反转？

**问题：** 为什么向右滑动要先反转，处理完再反转回来？

**答案：** 统一处理逻辑！

```python
# ❌ 不反转的写法（需要两套逻辑）
def slide_left(line):
    # 从左到右处理
    for i in range(len(line)):
        if line[i] == line[i+1]:
            ...

def slide_right(line):
    # 从右到左处理（容易出错）
    for i in range(len(line)-1, -1, -1):
        if line[i] == line[i-1]:
            ...

# ✅ 反转的写法（复用同一逻辑）
def slide(line, ascending):
    if not ascending:
        line = line[::-1]  # 反转
    # 统一的从左到右处理
    result = merge(line)
    if not ascending:
        result = result[::-1]  # 反转回来
    return result
```

---

## 🎯 游戏状态管理

### 状态枚举

```python
from enum import Enum, auto

class GameState(Enum):
    """游戏状态。"""
    PLAYING = auto()    # 游戏中
    WON = auto()        # 胜利（达到 2048）
    GAME_OVER = auto()  # 失败（无步可走）
```

### 状态转换

```
                ┌─────────────┐
                │   PLAYING   │
                │   (游戏中)   │
                └──────┬──────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
      达到 2048    继续游戏    无步可走
          │            │            │
          ↓            ↓            ↓
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │   WON    │  │ PLAYING  │  │GAME_OVER │
    │  (胜利)   │  │  (继续)   │  │  (失败)   │
    └──────────┘  └──────────┘  └──────────┘
```

### 状态更新逻辑

```python
def _update_game_state(self) -> None:
    """检查并更新游戏状态。"""
    
    # 检查胜利条件
    if not self._won and self.grid.get_max_tile() >= self.WINNING_VALUE:
        self._won = True
        self.state = GameState.WON
    
    # 检查失败条件
    if self.grid.is_full() and not self._can_merge():
        self.state = GameState.GAME_OVER

def _can_merge(self) -> bool:
    """检查是否有可合并的相邻方块。"""
    # 检查水平方向
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE - 1):
            if self.grid.cells[row][col] == self.grid.cells[row][col + 1]:
                return True
    
    # 检查垂直方向
    for col in range(GRID_SIZE):
        for row in range(GRID_SIZE - 1):
            if self.grid.cells[row][col] == self.grid.cells[row + 1][col]:
                return True
    
    return False
```

### 为什么胜利后还能继续玩？

```python
# 在 Game 类中
def __init__(self):
    self._won = False  # 内部标记

def _update_game_state(self):
    if not self._won and self.grid.get_max_tile() >= 2048:
        self._won = True
        self.state = GameState.WON
    # 注意：这里不阻止玩家继续移动！

def move(self, direction):
    if self.state == GameState.GAME_OVER:
        return False  # 失败后不能移动
    # 但胜利后可以继续！
```

**设计考虑：**
- 玩家达到 2048 后可能想挑战更高分
- 胜利状态只是提示，不是强制结束
- 只有 GAME_OVER 才真正停止游戏

---

## 🏆 胜负判定

### 胜利条件

```python
WINNING_VALUE = 2048

def check_win(self) -> bool:
    """检查是否胜利。"""
    return self.grid.get_max_tile() >= self.WINNING_VALUE

def get_max_tile(self) -> int:
    """获取棋盘上最大的方块值。"""
    return max(max(row) for row in self.cells)
```

**实现细节：**
- 遍历整个棋盘找最大值
- 时间复杂度：O(n²)，n=GRID_SIZE
- 对于 4x4 棋盘只需 16 次比较

### 失败条件

```python
def is_game_over(self) -> bool:
    """检查游戏是否结束。"""
    # 条件 1：棋盘未满 → 还能移动
    if self.grid.has_empty_cells():
        return False
    
    # 条件 2：有可合并的 → 还能移动
    if self._can_merge():
        return False
    
    # 既满又不能合并 → 真的结束了
    return True
```

**失败条件图解：**

```
┌─────────────────────────────────────┐
│         游戏结束判定流程             │
├─────────────────────────────────────┤
│                                     │
│   有空单元格？                       │
│       │                             │
│       ├─ 是 ─────────→ 未结束       │
│       │ 否                          │
│       ↓                             │
│   有相邻相同值？                     │
│       │                             │
│       ├─ 是 ─────────→ 未结束       │
│       │ 否                          │
│       ↓                             │
│   → 游戏结束 (GAME_OVER)            │
│                                     │
└─────────────────────────────────────┘
```

### 边界情况测试

```python
# 情况 1：棋盘未满
[2, 0, 4, 0]
[0, 8, 0, 0]
[0, 0, 2, 0]
[0, 0, 0, 4]
→ 有空格，未结束 ✓

# 情况 2：棋盘满但可合并
[2, 4, 8, 16]
[4, 8, 16, 32]
[8, 16, 32, 64]
[16, 32, 64, 128]
→ 有相邻相同值（如第一列的 2,4,8,16），未结束 ✓

# 情况 3：棋盘满且不可合并
[2, 4, 2, 4]
[4, 2, 4, 2]
[2, 4, 2, 4]
[4, 2, 4, 2]
→ 无空格且无相邻相同，游戏结束 ✓
```

---

## 📖 代码走读

### 完整的 move() 方法

```python
def move(self, direction: str) -> bool:
    """
    向指定方向移动所有方块。
    
    参数：
        direction: "up", "down", "left", "right"
    
    返回：
        True 如果有方块移动，False 否则
    """
    # 步骤 1：验证方向
    if direction not in DIRECTIONS:
        raise ValueError(f"Invalid direction: {direction}")
    
    # 步骤 2：检查游戏是否结束
    if self.state == GameState.GAME_OVER:
        return False
    
    # 步骤 3：选择对应的移动函数
    move_func = {
        DIRECTION_UP: self._move_up,
        DIRECTION_DOWN: self._move_down,
        DIRECTION_LEFT: self._move_left,
        DIRECTION_RIGHT: self._move_right,
    }[direction]
    
    # 步骤 4：执行移动
    moved, merge_score = move_func()
    
    # 步骤 5：如果有移动，更新状态
    if moved:
        self.moves += 1
        self.score += merge_score
        self.grid.spawn_tile()  # 生成新方块
        self._update_game_state()  # 检查胜负
    
    return moved
```

### 行移动的实现

```python
def _move_left(self) -> tuple[bool, int]:
    """向左移动所有行。"""
    return self._move_row(ascending=True)

def _move_right(self) -> tuple[bool, int]:
    """向右移动所有行。"""
    return self._move_row(ascending=False)

def _move_row(self, ascending: bool) -> tuple[bool, int]:
    """
    水平移动所有行。
    
    返回：
        (是否移动，合并得分)
    """
    total_moved = False
    total_merge_score = 0
    
    for row in range(GRID_SIZE):
        # 提取当前行
        line = [self.grid.cells[row][col] for col in range(GRID_SIZE)]
        
        # 滑动合并
        new_line, merge_score = self._slide_and_merge(line, ascending)
        total_merge_score += merge_score
        
        # 检查是否有变化
        for col, value in enumerate(new_line):
            if self.grid.cells[row][col] != value:
                total_moved = True
            self.grid.cells[row][col] = value
    
    return total_moved, total_merge_score
```

### 列移动的实现

```python
def _move_up(self) -> tuple[bool, int]:
    """向上移动所有列。"""
    return self._move_column(ascending=True)

def _move_down(self) -> tuple[bool, int]:
    """向下移动所有列。"""
    return self._move_column(ascending=False)

def _move_column(self, ascending: bool) -> tuple[bool, int]:
    """
    垂直移动所有列。
    
    原理：提取列 → 滑动合并 → 写回
    """
    total_moved = False
    total_merge_score = 0
    
    for col in range(GRID_SIZE):
        # 提取当前列
        line = [self.grid.cells[row][col] for row in range(GRID_SIZE)]
        
        # 滑动合并
        new_line, merge_score = self._slide_and_merge(line, ascending)
        total_merge_score += merge_score
        
        # 写回
        for row, value in enumerate(new_line):
            if self.grid.cells[row][col] != value:
                total_moved = True
            self.grid.cells[row][col] = value
    
    return total_moved, total_merge_score
```

**观察：** 行移动和列移动的代码几乎一样！

**优化思路：** 可以统一为一个方法，通过参数决定遍历方式。

---

## 🧪 测试你的理解

### 练习题 1：手动模拟

给定初始状态：
```
[2, 0, 2, 0]
[0, 0, 0, 0]
[0, 0, 0, 0]
[0, 0, 0, 4]
```

向左滑动后是什么状态？得分多少？

<details>
<summary>点击查看答案</summary>

```
[4, 0, 0, 0]   ← 第一行 2+2=4
[0, 0, 0, 0]
[0, 0, 0, 0]
[4, 0, 0, 0]   ← 最后一行不变

得分：4
```
</details>

### 练习题 2：边界情况

```
[2, 2, 2, 2]
```

向右滑动后是什么状态？

<details>
<summary>点击查看答案</summary>

```
[0, 0, 4, 4]

解释：
- 最右边的两个 2 合并为 4
- 最左边的两个 2 合并为 4
- 每个方块一次移动只能合并一次
```
</details>

### 练习题 3：游戏结束判定

以下状态游戏是否结束？

```
[16, 8, 4, 2]
[8, 4, 2, 16]
[4, 2, 16, 8]
[2, 16, 8, 4]
```

<details>
<summary>点击查看答案</summary>

**是，游戏结束。**

- 棋盘已满（无空格）
- 没有相邻相同值（无法合并）
</details>

---

## 🛠️ 实践任务

### 任务 1：添加移动音效

```python
# 在 Game 类中
def move(self, direction: str) -> bool:
    moved = self.game.move(direction)
    
    if moved:
        # TODO: 播放音效
        play_sound("move.mp3")
        
        if self.merge_score > 0:
            play_sound("merge.mp3")
```

### 任务 2：实现连击系统

```python
class Game:
    def __init__(self):
        self.combo = 0  # 连击数
        self.max_combo = 0
    
    def move(self, direction: str) -> bool:
        moved = self._do_move(direction)
        
        if moved and self.merge_score > 0:
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            # 连击加分
            self.score += self.merge_score * (1 + self.combo * 0.1)
        else:
            self.combo = 0
        
        return moved
```

### 任务 3：添加移动历史

```python
class Game:
    def __init__(self):
        self.move_history: list[str] = []
    
    def move(self, direction: str) -> bool:
        moved = self._do_move(direction)
        
        if moved:
            self.move_history.append(direction)
            print(f"Move {len(self.move_history)}: {direction}")
        
        return moved
    
    def get_move_sequence(self) -> str:
        """获取移动序列（用于复盘）。"""
        return " → ".join(self.move_history)
```

### 任务 4：性能分析

```python
import cProfile

# 分析 move() 性能
game = Game()
cProfile.run('game.move("left")')

# 输出示例：
#          100 function calls in 0.001 seconds
#   Ordered by: cumulative time
#
#   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#        1    0.000    0.000    0.001    0.001 game.py:50(move)
#        1    0.000    0.000    0.000    0.000 game.py:80(_move_left)
#        ...
```

---

## ❓ 常见问题

### Q1: 为什么返回值是 `(moved, score)` 元组？

**A:** 调用者需要知道：
1. 移动是否成功（决定是否生成新方块）
2. 得了多少分（用于更新 UI）

用元组返回多个值比修改外部状态更清晰。

### Q2: 为什么不直接在 move() 里生成新方块？

**A:** 职责分离！
- `move()` 负责移动逻辑
- 生成新方块是副作用
- 这样便于测试（可以测试移动但不生成方块）

### Q3: 如何调试滑动合并算法？

**A:** 添加详细日志：
```python
def _slide_and_merge(self, line, ascending):
    print(f"Input: {line}, ascending={ascending}")
    
    non_zero = [x for x in line if x != 0]
    print(f"After remove zeros: {non_zero}")
    
    # ... 每一步都打印
    
    print(f"Result: {merged}, score: {merge_score}")
    return merged, merge_score
```

---

## 📚 延伸阅读

- [算法设计技巧](https://realpython.com/sorting-algorithms-python/)
- [状态机模式](https://python-patterns.guide/gang-of-four/state-pattern/)
- [单元测试游戏逻辑](https://realpython.com/python-testing/)

---

**下一章：** [第 5 章 用户界面开发](05_ui.md)

🐧 _理解算法，才能优化它！_
