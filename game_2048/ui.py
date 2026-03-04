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
    
    def __init__(self, game: Game):
        super().__init__()
        self.game = game
    
    def render(self) -> str:
        """Render the grid as text."""
        cells = self.game.grid.cells
        
        # Build grid display
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
        
        return "\n".join(lines)
    
    def refresh_display(self) -> None:
        """Refresh the grid display."""
        self.refresh()


class ScoreDisplay(Static):
    """Display score and stats."""
    
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
        padding: 1 2;
    }
    
    #game-title {
        text-align: center;
        text-style: bold;
        padding: 1 0;
    }
    
    #controls-hint {
        text-align: center;
        color: $text-muted;
        padding: 0 0 1 0;
    }
    
    GridDisplay {
        background: $surface-darken-2;
        border: solid $primary;
        padding: 1;
        margin: 1 0;
        width: 100%;
        height: 12;
    }
    
    ScoreDisplay {
        background: $primary-background;
        padding: 1 2;
        margin: 1 0;
        text-style: bold;
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
