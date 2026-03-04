"""Utility functions for the 2048 game.

This module contains helper functions for:
- Tile styling (colors based on value)
- Input validation
- Display formatting
"""

from typing import Optional


def get_tile_style(value: int) -> dict[str, str]:
    """Get styling information for a tile based on its value.
    
    Returns colors and styles that match the official 2048 game.
    
    Args:
        value: Tile value (2, 4, 8, ..., 2048, etc.)
        
    Returns:
        Dictionary with style properties:
        - bg: Background color name
        - fg: Foreground (text) color name
        - style: Text style (bold, etc.)
    
    Example:
        style = get_tile_style(2048)
        # {'bg': 'yellow', 'fg': 'white', 'style': 'bold'}
    """
    # Color scheme inspired by the original 2048 game
    styles = {
        0: {"bg": "gray20", "fg": "gray50", "style": ""},
        2: {"bg": "gray60", "fg": "gray10", "style": "bold"},
        4: {"bg": "gray55", "fg": "gray10", "style": "bold"},
        8: {"bg": "orange3", "fg": "white", "style": "bold"},
        16: {"bg": "dark_orange3", "fg": "white", "style": "bold"},
        32: {"bg": "orange1", "fg": "white", "style": "bold"},
        64: {"bg": "orange_red1", "fg": "white", "style": "bold"},
        128: {"bg": "yellow1", "fg": "gray10", "style": "bold"},
        256: {"bg": "yellow1", "fg": "gray10", "style": "bold"},
        512: {"bg": "gold1", "fg": "gray10", "style": "bold"},
        1024: {"bg": "gold1", "fg": "gray10", "style": "bold"},
        2048: {"bg": "gold3", "fg": "gray10", "style": "bold"},
    }
    
    # For values higher than 2048, use the 2048 style
    if value in styles:
        return styles[value]
    elif value > 2048:
        return styles[2048]
    else:
        # Fallback for unexpected values
        return styles[2]


def format_number(value: int) -> str:
    """Format large numbers for display.
    
    Args:
        value: Number to format
        
    Returns:
        Formatted string (e.g., "1.5k" for 1500)
    """
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}m"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}k"
    else:
        return str(value)


def validate_direction(direction: str) -> bool:
    """Validate a movement direction string.
    
    Args:
        direction: Direction string to validate
        
    Returns:
        True if valid direction
    """
    valid = {"up", "down", "left", "right", "u", "d", "l", "r"}
    return direction.lower() in valid


def normalize_direction(direction: str) -> str:
    """Normalize direction string to full name.
    
    Args:
        direction: Direction string (can be abbreviated)
        
    Returns:
        Normalized direction string
        
    Raises:
        ValueError: If direction is invalid
    """
    mapping = {
        "up": "up", "u": "up",
        "down": "down", "d": "down",
        "left": "left", "l": "left",
        "right": "right", "r": "right",
    }
    
    normalized = mapping.get(direction.lower())
    if not normalized:
        raise ValueError(f"Invalid direction: {direction}")
    
    return normalized


def print_grid(cells: list[list[int]]) -> None:
    """Print a grid to console (for debugging).
    
    Args:
        cells: 2D list of tile values
    """
    print("+----" * len(cells[0]) + "+")
    for row in cells:
        line = "|"
        for cell in row:
            if cell == 0:
                line += "    |"
            else:
                line += f"{cell:4}|"
        print(line)
        print("+----" * len(row) + "+")


def clear_screen() -> None:
    """Clear the terminal screen."""
    import os
    # Windows
    if os.name == "nt":
        os.system("cls")
    # Unix/Linux/Mac
    else:
        os.system("clear")


def get_tile_color_name(value: int) -> str:
    """Get a human-readable color name for a tile value.
    
    Useful for logging or accessibility.
    
    Args:
        value: Tile value
        
    Returns:
        Color name string
    """
    color_map = {
        2: "light gray",
        4: "gray",
        8: "orange",
        16: "dark orange",
        32: "bright orange",
        64: "red-orange",
        128: "yellow",
        256: "bright yellow",
        512: "gold",
        1024: "bright gold",
        2048: "legendary gold",
    }
    
    if value in color_map:
        return color_map[value]
    elif value > 2048:
        return "legendary gold"
    else:
        return "empty"
