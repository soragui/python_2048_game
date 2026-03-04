"""Textual TUI components for the 2048 game.

This module defines all visual components:
- TileWidget: Individual tile display
- GridWidget: The 4x4 game board
- ScoreWidget: Score and stats display
- GameScreen: Main game screen
"""

from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import Static, Label, Button, Footer, Header
from textual.screen import ModalScreen
from textual.binding import Binding

from .game import Game, GameState
from .config import GRID_SIZE


class TileWidget(Static):
    """A single tile widget displaying a number."""
    
    DEFAULT_CSS = """
    TileWidget {
        background: $surface;
        border: solid $primary-background;
        content-align: center middle;
        text-style: bold;
    }
    
    TileWidget.tile-empty {
        background: $surface-darken-1;
    }
    """
    
    def __init__(self, value: int = 0):
        super().__init__()
        self.value = value
        self._update_display()
    
    def _update_display(self) -> None:
        """Update display based on value."""
        self.remove_class("tile-empty")
        if self.value == 0:
            self.add_class("tile-empty")
            self.update("")
        else:
            self.update(str(self.value))
    
    def set_value(self, value: int) -> None:
        """Set the tile value and refresh."""
        self.value = value
        self._update_display()


class GridWidget(Static):
    """The 4x4 game grid widget."""
    
    DEFAULT_CSS = """
    GridWidget {
        width: 100%;
        height: 20;
        background: $surface-darken-2;
        border: solid $primary;
        padding: 1;
        layout: grid;
        grid-size: 4 4;
        grid-gutter: 1 1;
    }
    
    .tile-cell {
        background: $surface;
        border: solid $primary-background;
        content-align: center middle;
        text-style: bold;
    }
    
    .tile-cell.empty {
        background: $surface-darken-1;
    }
    """
    
    def __init__(self, game: Game):
        super().__init__()
        self.game = game
        self.tiles: list[list[TileWidget]] = []
    
    def compose(self) -> ComposeResult:
        """Compose the 4x4 grid."""
        self.tiles = []
        
        for row in range(GRID_SIZE):
            tile_row = []
            for col in range(GRID_SIZE):
                value = self.game.grid.cells[row][col]
                tile = TileWidget(value)
                tile.add_class("tile-cell")
                if value == 0:
                    tile.add_class("empty")
                tile_row.append(tile)
                yield tile
            self.tiles.append(tile_row)
    
    def refresh_grid(self) -> None:
        """Refresh all tile values from game state."""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                value = self.game.grid.cells[row][col]
                self.tiles[row][col].set_value(value)


class ScoreWidget(Static):
    """Display current score and game stats."""
    
    DEFAULT_CSS = """
    ScoreWidget {
        width: 100%;
        height: auto;
        background: $primary-background;
        padding: 1 2;
        margin: 1 0;
    }
    
    #score-label {
        text-style: bold;
        color: $text;
        margin: 0 2 0 0;
    }
    
    #moves-label {
        color: $text-muted;
        margin: 0 2 0 0;
    }
    
    #max-label {
        color: $warning;
    }
    """
    
    def __init__(self, game: Game):
        super().__init__()
        self.game = game
    
    def compose(self) -> ComposeResult:
        """Compose score display."""
        yield Horizontal(
            Label(f"Score: {self.game.score}", id="score-label"),
            Label(f"Moves: {self.game.moves}", id="moves-label"),
            Label(f"Max: {self.game.grid.get_max_tile()}", id="max-label"),
        )
    
    def update_display(self) -> None:
        """Update display with current game stats."""
        try:
            self.query_one("#score-label", Label).update(f"Score: {self.game.score}")
            self.query_one("#moves-label", Label).update(f"Moves: {self.game.moves}")
            self.query_one("#max-label", Label).update(f"Max: {self.game.grid.get_max_tile()}")
        except Exception:
            pass  # Widgets may not be mounted yet


class GameOverModal(ModalScreen):
    """Modal dialog shown when game ends."""
    
    BINDINGS = [
        Binding("enter", "restart", "Restart"),
        Binding("escape", "quit", "Quit"),
    ]
    
    DEFAULT_CSS = """
    GameOverModal {
        align: center middle;
    }
    
    #modal-container {
        width: 50;
        height: auto;
        background: $surface;
        border: solid $error;
        padding: 2 4;
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
    
    #modal-btn {
        width: 100%;
        margin: 1 0;
    }
    """
    
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
            yield Label(msg, id="modal-message")
            yield Label(f"Final Score: {self.game.score}", id="modal-score")
            yield Button("Play Again (Enter)", id="restart-btn", variant="primary")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "restart-btn":
            self.dismiss(True)
    
    def action_restart(self) -> None:
        """Restart the game."""
        self.dismiss(True)
    
    def action_quit(self) -> None:
        """Close without restarting."""
        self.dismiss(False)


class GameScreen(Vertical):
    """Main game screen containing all game widgets."""
    
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
    """
    
    def __init__(self, game: Game):
        super().__init__()
        self.game = game
        self.grid_widget: GridWidget | None = None
        self.score_widget: ScoreWidget | None = None
    
    def compose(self) -> ComposeResult:
        """Compose the game screen."""
        yield Label("🎮 2048", id="game-title")
        yield Label("Arrow Keys or WASD to move | R to restart | Q to quit", id="controls-hint")
        
        self.score_widget = ScoreWidget(self.game)
        yield self.score_widget
        
        self.grid_widget = GridWidget(self.game)
        yield self.grid_widget
    
    def update_display(self) -> None:
        """Update all widgets with current game state."""
        if self.score_widget:
            self.score_widget.update_display()
        if self.grid_widget:
            self.grid_widget.refresh_grid()
