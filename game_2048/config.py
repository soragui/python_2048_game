"""Game configuration and constants.

This module contains all configurable settings for the 2048 game.
Centralizing constants here makes it easy to tweak game behavior.
"""

# Grid size (4x4 is standard 2048)
GRID_SIZE: int = 4

# Initial number of tiles at game start
INITIAL_TILES: int = 2

# Tile values for colors and display
TILE_VALUES: list[int] = [
    2, 4, 8, 16, 32, 64, 128, 256, 512, 
    1024, 2048, 4096, 8192, 16384, 32768
]

# New tile spawn probabilities
NEW_TILE_PROBABILITIES: dict[int, float] = {
    2: 0.9,   # 90% chance to spawn a 2
    4: 0.1,   # 10% chance to spawn a 4
}

# Game directions
DIRECTION_UP: str = "up"
DIRECTION_DOWN: str = "down"
DIRECTION_LEFT: str = "left"
DIRECTION_RIGHT: str = "right"

# Valid directions list
DIRECTIONS: list[str] = [
    DIRECTION_UP, 
    DIRECTION_DOWN, 
    DIRECTION_LEFT, 
    DIRECTION_RIGHT
]

# Score multipliers for merging tiles
# When two tiles merge, you get points equal to the merged value
SCORE_MULTIPLIER: int = 1
