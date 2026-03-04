"""Core game logic for 2048.

This module handles all game mechanics:
- Tile movement in all directions
- Tile merging
- Score tracking
- Game state (playing, won, game over)
"""

from enum import Enum, auto
from typing import Optional

from .models import Grid
from .config import GRID_SIZE, DIRECTIONS, DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT


class GameState(Enum):
    """Current state of the game."""
    PLAYING = auto()    # Game in progress
    WON = auto()        # Player reached 2048
    GAME_OVER = auto()  # No more moves possible


class Game:
    """Main game controller.
    
    Manages game state, score, and movement logic.
    
    Example:
        game = Game()
        game.move("up")
        print(f"Score: {game.score}")
    """
    
    # Winning tile value
    WINNING_VALUE: int = 2048
    
    def __init__(self):
        """Initialize a new game."""
        self.grid = Grid()
        self.score: int = 0
        self.moves: int = 0
        self.state: GameState = GameState.PLAYING
        self._won: bool = False
        
        # Spawn initial tiles
        self._spawn_initial_tiles()
    
    def _spawn_initial_tiles(self) -> None:
        """Spawn initial tiles at game start."""
        from .config import INITIAL_TILES
        for _ in range(INITIAL_TILES):
            self.grid.spawn_tile()
    
    def reset(self) -> None:
        """Reset the game to initial state."""
        self.grid.clear()
        self.score = 0
        self.moves = 0
        self.state = GameState.PLAYING
        self._won = False
        self._spawn_initial_tiles()
    
    def move(self, direction: str) -> bool:
        """Move all tiles in the specified direction.
        
        Args:
            direction: One of "up", "down", "left", "right"
            
        Returns:
            True if any tile moved, False otherwise
        """
        if direction not in DIRECTIONS:
            raise ValueError(f"Invalid direction: {direction}")
        
        if self.state == GameState.GAME_OVER:
            return False
        
        # Get the movement function based on direction
        move_func = {
            DIRECTION_UP: self._move_up,
            DIRECTION_DOWN: self._move_down,
            DIRECTION_LEFT: self._move_left,
            DIRECTION_RIGHT: self._move_right,
        }[direction]
        
        # Execute move and track if grid changed
        moved, merge_score = move_func()
        
        if moved:
            self.moves += 1
            self.score += merge_score
            self.grid.spawn_tile()
            self._update_game_state()
        
        return moved
    
    def _move_up(self) -> tuple[bool, int]:
        """Move all tiles up.
        
        Returns:
            Tuple of (moved, merge_score)
        """
        return self._move_column(ascending=True)
    
    def _move_down(self) -> tuple[bool, int]:
        """Move all tiles down.
        
        Returns:
            Tuple of (moved, merge_score)
        """
        return self._move_column(ascending=False)
    
    def _move_left(self) -> tuple[bool, int]:
        """Move all tiles left.
        
        Returns:
            Tuple of (moved, merge_score)
        """
        return self._move_row(ascending=True)
    
    def _move_right(self) -> tuple[bool, int]:
        """Move all tiles right.
        
        Returns:
            Tuple of (moved, merge_score)
        """
        return self._move_row(ascending=False)
    
    def _move_row(self, ascending: bool) -> tuple[bool, int]:
        """Move tiles in all rows horizontally.
        
        Args:
            ascending: If True, move left; if False, move right
            
        Returns:
            Tuple of (moved, merge_score)
        """
        total_moved = False
        total_merge_score = 0
        
        for row in range(GRID_SIZE):
            # Extract row data
            line = [self.grid.cells[row][col] for col in range(GRID_SIZE)]
            
            # Slide and merge
            new_line, merge_score = self._slide_and_merge(line, ascending)
            total_merge_score += merge_score
            
            # Check if anything changed
            for col, value in enumerate(new_line):
                if self.grid.cells[row][col] != value:
                    total_moved = True
                self.grid.cells[row][col] = value
        
        return total_moved, total_merge_score
    
    def _move_column(self, ascending: bool) -> tuple[bool, int]:
        """Move tiles in all columns vertically.
        
        Args:
            ascending: If True, move up; if False, move down
            
        Returns:
            Tuple of (moved, merge_score)
        """
        total_moved = False
        total_merge_score = 0
        
        for col in range(GRID_SIZE):
            # Extract column data
            line = [self.grid.cells[row][col] for row in range(GRID_SIZE)]
            
            # Slide and merge
            new_line, merge_score = self._slide_and_merge(line, ascending)
            total_merge_score += merge_score
            
            # Check if anything changed
            for row, value in enumerate(new_line):
                if self.grid.cells[row][col] != value:
                    total_moved = True
                self.grid.cells[row][col] = value
        
        return total_moved, total_merge_score
    
    def _slide_and_merge(self, line: list[int], ascending: bool) -> tuple[list[int], int]:
        """Slide and merge a single line of tiles.
        
        This is the core 2048 mechanic:
        1. Remove zeros (empty spaces)
        2. Merge adjacent equal tiles
        3. Pad with zeros
        
        Args:
            line: List of tile values
            ascending: If True, slide to start; if False, slide to end
            
        Returns:
            Tuple of (new_line, merge_score)
        """
        # Remove zeros
        non_zero = [x for x in line if x != 0]
        
        # Reverse if moving right/down (process from the direction of movement)
        if not ascending:
            non_zero = non_zero[::-1]
        
        # Merge adjacent equal tiles
        merged = []
        merge_score = 0
        skip_next = False
        
        for i in range(len(non_zero)):
            if skip_next:
                skip_next = False
                continue
            
            # Check if we can merge with next tile
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                # Merge: double the value
                new_value = non_zero[i] * 2
                merged.append(new_value)
                merge_score += new_value
                skip_next = True  # Skip the next tile (already merged)
            else:
                merged.append(non_zero[i])
        
        # Pad with zeros to restore original length
        merged.extend([0] * (len(line) - len(merged)))
        
        # Reverse back if needed
        if not ascending:
            merged = merged[::-1]
        
        return merged, merge_score
    
    def _update_game_state(self) -> None:
        """Check and update game state (win/lose conditions)."""
        # Check win condition
        if not self._won and self.grid.get_max_tile() >= self.WINNING_VALUE:
            self._won = True
            self.state = GameState.WON
        
        # Check game over (no empty cells and no possible merges)
        if self.grid.is_full() and not self._can_merge():
            self.state = GameState.GAME_OVER
    
    def _can_merge(self) -> bool:
        """Check if any adjacent tiles can be merged.
        
        Returns:
            True if at least one merge is possible
        """
        # Check horizontal merges
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE - 1):
                if self.grid.cells[row][col] == self.grid.cells[row][col + 1]:
                    return True
        
        # Check vertical merges
        for col in range(GRID_SIZE):
            for row in range(GRID_SIZE - 1):
                if self.grid.cells[row][col] == self.grid.cells[row + 1][col]:
                    return True
        
        return False
    
    def can_move(self) -> bool:
        """Check if any move is possible.
        
        Returns:
            True if at least one direction allows movement
        """
        if self.grid.has_empty_cells():
            return True
        return self._can_merge()
    
    def get_stats(self) -> dict:
        """Get game statistics.
        
        Returns:
            Dictionary with score, moves, max tile, etc.
        """
        return {
            "score": self.score,
            "moves": self.moves,
            "max_tile": self.grid.get_max_tile(),
            "tile_count": self.grid.count_tiles(),
            "state": self.state.name,
        }
    
    def __str__(self) -> str:
        """String representation for debugging."""
        return str(self.grid)
