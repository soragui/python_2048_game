# 🎮 2048 - Terminal Edition

A classic 2048 puzzle game built for the terminal using Python and Textual.

## Features

- 🖥️ **Beautiful TUI** - Clean, responsive terminal interface
- 🎯 **Classic Gameplay** - Original 2048 rules and mechanics
- ⌨️ **Multiple Controls** - Arrow keys or WASD
- 📊 **Stats Tracking** - Score, moves, and max tile
- 🔄 **Easy Restart** - Quick game reset anytime
- 📦 **Modular Design** - Clean, extensible code structure

## Installation

```bash
# Navigate to project directory
cd ~/Work/open_learn/python/game_2048

# Install dependencies
uv sync

# Install the CLI command
uv pip install -e .
```

## Usage

### Launch the Game

```bash
# Using uv run
uv run game-2048

# Or after installing
game-2048
```

### Controls

| Key | Action |
|-----|--------|
| `↑` `↓` `←` `→` | Move tiles (arrow keys) |
| `W` `A` `S` `D` | Move tiles (alternative) |
| `R` | Restart game |
| `Q` | Quit game |
| `?` | Show help |

### How to Play

1. **Goal**: Combine tiles to reach **2048**!
2. **Move**: Use arrow keys or WASD to slide all tiles
3. **Merge**: When two tiles with the same number collide, they merge into one
4. **Spawn**: After each move, a new tile (2 or 4) appears
5. **Win**: Create a tile with value 2048
6. **Lose**: When the grid is full and no merges are possible

## Project Structure

```
game_2048/
├── pyproject.toml        # Project configuration
├── README.md             # This file
├── docs/
│   └── ARCHITECTURE.md   # Architecture documentation
└── game_2048/
    ├── __init__.py       # Package init
    ├── app.py            # Main application entry
    ├── game.py           # Core game logic
    ├── models.py         # Data models (Grid, Tile)
    ├── ui.py             # Textual UI components
    ├── config.py         # Configuration constants
    └── utils.py          # Utility functions
```

## Module Overview

| Module | Purpose |
|--------|---------|
| `app.py` | Application entry point, event handling |
| `game.py` | Game mechanics (movement, merging, scoring) |
| `models.py` | Data structures (Grid, Tile) |
| `ui.py` | Textual widgets and screens |
| `config.py` | Game constants and settings |
| `utils.py` | Helper functions |

## Learning Topics

This project demonstrates:

- **Modular Architecture** - Separation of concerns
- **Game Loop** - State management and updates
- **Event-Driven UI** - Textual bindings and handlers
- **Data Modeling** - Clean data structures
- **Algorithm Design** - Slide and merge logic

## Code Quality

- ✅ Type hints throughout
- ✅ Docstrings for all classes and functions
- ✅ Single responsibility per module
- ✅ Configurable constants
- ✅ Easy to extend

## Extending the Game

Here are some ideas for modifications:

### Easy
- [ ] Change grid size (edit `GRID_SIZE` in config.py)
- [ ] Adjust tile spawn probabilities
- [ ] Add color themes

### Medium
- [ ] Add undo functionality
- [ ] Implement high score persistence
- [ ] Add animations for tile movement

### Advanced
- [ ] Multiplayer mode (hotseat)
- [ ] Custom game modes (hexagonal grid, etc.)
- [ ] AI auto-play bot

## Development

```bash
# Run in development mode
uv run game-2048

# Run tests (when added)
uv run pytest
```

## Troubleshooting

**Game not starting?**
```bash
# Ensure dependencies are installed
uv sync
```

**Terminal too small?**
- Resize your terminal window
- Textual needs minimum space for the grid

**Controls not working?**
- Make sure terminal has focus
- Try WASD instead of arrow keys (or vice versa)

## License

MIT License - Feel free to modify and share!

---

Built with 🐧 using [Textual](https://textual.textualize.io/)
