"""Textual TUI components for the 2048 game."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, Label, Footer, Header, Button
from textual.screen import ModalScreen
from textual.binding import Binding

from .game import Game, GameState
from .config import GRID_SIZE


class GridDisplay(Static):
    """Display the 4x4 game grid using rendered text."""
    
    DEFAULT_CSS = """
    GridDisplay {
        width: 42;
        height: 12;
        content-align: center top;
        align: center middle;
        background: #3a3a3a;  /* Dark gray background like original 2048 */
        border: solid #bbada0;
        padding: 1 2;
        margin: 1 0;
    }
    """
    
    # Tile colors matching original 2048 game
    TILE_COLORS = {
        0: "#cdc1b4",      # Empty cell
        2: "#eee4da",      # 2
        4: "#ede0c8",      # 4
        8: "#f2b179",      # 8
        16: "#f59563",     # 16
        32: "#f67c5f",     # 32
        64: "#f65e3b",     # 64
        128: "#edcf72",    # 128
        256: "#edcc61",    # 256
        512: "#edc850",    # 512
        1024: "#edc53f",   # 1024
        2048: "#edc22e",   # 2048
    }
    
    def __init__(self, game: Game):
        super().__init__()
        self.game = game
    
    def _get_cell_color(self, value: int) -> str:
        """Get color code for a tile value."""
        return self.TILE_COLORS.get(value, self.TILE_COLORS[2048])
    
    def render(self) -> str:
        """Render the grid with colored cells."""
        from rich.text import Text
        from rich.style import Style
        
        cells = self.game.grid.cells
        lines = []
        
        # Top border
        lines.append("┌" + "────┬" * (GRID_SIZE - 1) + "────┐")
        
        # Rows
        for row in range(GRID_SIZE):
            # Cell values
            line = "│"
            for col in range(GRID_SIZE):
                value = cells[row][col]
                if value == 0:
                    line += "    │"
                else:
                    line += f"{value:4}│"
            lines.append(line)
            
            # Row separator (except last row)
            if row < GRID_SIZE - 1:
                lines.append("├" + "────┼" * (GRID_SIZE - 1) + "────┤")
        
        # Bottom border
        lines.append("└" + "────┴" * (GRID_SIZE - 1) + "────┘")
        
        # Create rich text with colors
        result = Text()
        for line_idx, line in enumerate(lines):
            for char_idx, char in enumerate(line):
                # Determine color for this position
                if line_idx == 0 or line_idx == len(lines) - 1:
                    # Border rows - use border color
                    style = Style(color="#bbada0")
                elif line_idx % 2 == 0:
                    # Separator rows
                    style = Style(color="#bbada0")
                else:
                    # Cell rows - check if we're in a cell
                    cell_row = line_idx // 2
                    # Simple coloring: color the numbers
                    if char.isdigit():
                        cell_col = char_idx // 5
                        if cell_col < GRID_SIZE:
                            value = cells[cell_row][cell_col]
                            color = self._get_cell_color(value)
                            style = Style(color=color, bold=True)
                        else:
                            style = Style(color="#cdc1b4")
                    elif char in "│├┼┤":
                        style = Style(color="#bbada0")
                    else:
                        style = Style(color="#cdc1b4")
                
                result.append(char, style)
            
            if line_idx < len(lines) - 1:
                result.append("\n")
        
        return result
    
    def refresh_display(self) -> None:
        """Refresh the grid display."""
        self.refresh()


class ScoreDisplay(Static):
    """Display score and stats."""
    
    DEFAULT_CSS = """
    ScoreDisplay {
        width: 42;
        height: auto;
        content-align: center middle;
        background: #bbada0;  /* Match 2048 theme */
        padding: 1 2;
        margin: 1 0;
        text-style: bold;
    }
    """
    
    def __init__(self, game: Game):
        super().__init__()
        self.game = game
    
    def render(self) -> str:
        """Render score display."""
        return f"Score: {self.game.score}  |  Moves: {self.game.moves}  |  Max: {self.game.grid.get_max_tile()}"
    
    def refresh_display(self) -> None:
        """Refresh the score display."""
        self.refresh()


class GameOverModal(ModalScreen):
    """Modal dialog shown when game ends."""
    
    BINDINGS = [
        Binding("enter", "restart", "Restart"),
        Binding("escape", "quit", "Quit"),
    ]
    
    def __init__(self, game: Game):
        super().__init__()
        self.game = game
    
    def compose(self) -> ComposeResult:
        """Compose modal content."""
        if self.game.state == GameState.WON:
            title = "🎉 You Win!"
            msg = "You reached 2048!"
        else:
            title = "💀 Game Over"
            msg = "No more moves possible!"
        
        with Vertical(id="modal-container"):
            yield Label(title, id="modal-title")
            yield Label(msg)
            yield Label(f"Final Score: {self.game.score}", id="modal-score")
            yield Button("Play Again (Enter)", id="restart-btn", variant="primary")
    
    def on_button_pressed(self, event) -> None:
        if event.button.id == "restart-btn":
            self.dismiss(True)
    
    def action_restart(self) -> None:
        self.dismiss(True)
    
    def action_quit(self) -> None:
        self.dismiss(False)


class GameScreen(Vertical):
    """Main game screen."""
    
    DEFAULT_CSS = """
    GameScreen {
        width: 100%;
        height: 100%;
        align: center top;
        padding: 0 2;
    }
    
    #game-title {
        text-align: center;
        text-style: bold;
        padding: 0;
        margin: 1 0;
        width: 100%;
        height: 1;
    }
    
    #controls-hint {
        text-align: center;
        color: $text-muted;
        padding: 0;
        margin: 0 0 1 0;
        width: 100%;
        height: 1;
    }
    
    ScoreDisplay {
        width: 42;
        height: 1;
        padding: 0 2;
        margin: 1 0;
    }
    
    GridDisplay {
        margin: 0 0;
    }
    
    #modal-container {
        width: 50;
        height: auto;
        background: $surface;
        border: solid $error;
        padding: 2 4;
        align: center middle;
    }
    
    #modal-title {
        text-align: center;
        text-style: bold;
        padding: 1 0;
    }
    
    #modal-score {
        text-align: center;
        padding: 1 0;
    }
    """
    
    def __init__(self, game: Game):
        super().__init__()
        self.game = game
        self.grid_display: GridDisplay | None = None
        self.score_display: ScoreDisplay | None = None
    
    def compose(self) -> ComposeResult:
        """Compose the game screen."""
        yield Label("🎮 2048", id="game-title")
        yield Label("Arrow Keys or WASD to move | R to restart | Q to quit", id="controls-hint")
        
        self.score_display = ScoreDisplay(self.game)
        yield self.score_display
        
        self.grid_display = GridDisplay(self.game)
        yield self.grid_display
    
    def update_display(self) -> None:
        """Update all displays."""
        if self.score_display:
            self.score_display.refresh_display()
        if self.grid_display:
            self.grid_display.refresh_display()
