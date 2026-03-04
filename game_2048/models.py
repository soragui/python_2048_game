"""Data models for the 2048 game.

This module defines the core data structures:
- Tile: Represents a single tile with a value
- Grid: Represents the 4x4 game board
"""

from dataclasses import dataclass, field
from typing import Optional
from copy import deepcopy

from .config import GRID_SIZE, INITIAL_TILES, NEW_TILE_PROBABILITIES


@dataclass
class Tile:
    """A single tile on the game board.
    
    Attributes:
        value: The tile's numeric value (2, 4, 8, etc.)
        row: Row position (0 to GRID_SIZE-1)
        col: Column position (0 to GRID_SIZE-1)
        merged: Whether this tile was created by merging (for animation)
        new: Whether this tile is newly spawned (for animation)
    """
    value: int
    row: int
    col: int
    merged: bool = False
    new: bool = False
    
    def reset_flags(self) -> None:
        """Reset animation flags after rendering."""
        self.merged = False
        self.new = False


class Grid:
    """The 4x4 game board.
    
    The grid stores tile values in a 2D list. Empty cells are represented
    by 0. This class handles all board operations like spawning tiles,
    checking for available moves, and serializing state.
    
    Example:
        grid = Grid()
        grid.spawn_tile()
        print(grid)
    """
    
    def __init__(self):
        """Initialize an empty grid."""
        self.cells: list[list[int]] = self._create_empty_grid()
    
    def _create_empty_grid(self) -> list[list[int]]:
        """Create a new empty GRID_SIZE x GRID_SIZE grid."""
        return [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    def clear(self) -> None:
        """Reset the grid to empty state."""
        self.cells = self._create_empty_grid()
    
    def __getitem__(self, position: tuple[int, int]) -> int:
        """Get tile value at (row, col).
        
        Args:
            position: Tuple of (row, col)
            
        Returns:
            Tile value (0 if empty)
        """
        row, col = position
        return self.cells[row][col]
    
    def __setitem__(self, position: tuple[int, int], value: int) -> None:
        """Set tile value at (row, col).
        
        Args:
            position: Tuple of (row, col)
            value: Tile value (0 for empty)
        """
        row, col = position
        self.cells[row][col] = value
    
    def __str__(self) -> str:
        """String representation for debugging."""
        rows = []
        for row in self.cells:
            rows.append(" | ".join(f"{cell:4}" if cell else "   0" for cell in row))
        return "\n" + "\n".join(rows) + "\n"
    
    def get_empty_cells(self) -> list[tuple[int, int]]:
        """Get list of all empty cell positions.
        
        Returns:
            List of (row, col) tuples for empty cells
        """
        empty = []
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.cells[row][col] == 0:
                    empty.append((row, col))
        return empty
    
    def has_empty_cells(self) -> bool:
        """Check if there are any empty cells."""
        return len(self.get_empty_cells()) > 0
    
    def spawn_tile(self) -> Optional[tuple[int, int]]:
        """Spawn a new tile (2 or 4) in a random empty cell.
        
        Returns:
            Position (row, col) of spawned tile, or None if no empty cells
        """
        import random
        
        empty_cells = self.get_empty_cells()
        if not empty_cells:
            return None
        
        # Pick random empty cell
        row, col = random.choice(empty_cells)
        
        # 90% chance for 2, 10% chance for 4
        value = 2 if random.random() < NEW_TILE_PROBABILITIES[2] else 4
        self.cells[row][col] = value
        
        return (row, col)
    
    def is_full(self) -> bool:
        """Check if the grid is completely full."""
        return not self.has_empty_cells()
    
    def get_max_tile(self) -> int:
        """Get the highest tile value on the board."""
        return max(max(row) for row in self.cells)
    
    def count_tiles(self) -> int:
        """Count number of non-empty tiles."""
        return sum(1 for row in self.cells for cell in row if cell != 0)
    
    def copy(self) -> 'Grid':
        """Create a deep copy of this grid."""
        new_grid = Grid()
        new_grid.cells = deepcopy(self.cells)
        return new_grid
    
    def to_dict(self) -> dict:
        """Serialize grid to dictionary."""
        return {
            "cells": self.cells,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Grid':
        """Create grid from dictionary."""
        grid = cls()
        grid.cells = data["cells"]
        return grid
