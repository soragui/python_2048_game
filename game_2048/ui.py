"""Textual TUI components for the 2048 game.

This module defines all visual components:
- TileWidget: Individual tile display
- GridWidget: The 4x4 game board
- ScoreWidget: Score and stats display
- GameScreen: Main game screen
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Label, Button, Footer, Header
from textual.binding import Binding
from textual.screen import ModalScreen

from .game import Game, GameState
from .config import GRID_SIZE, TILE_VALUES
from .utils import get_tile_style


class TileWidget(Static):
    """A single tile widget displaying a number.
    
    The tile's appearance (color, style) changes based on its value.
    """
    
    DEFAULT_CSS = """
    TileWidget {
        width: 1fr;
        height: 100%;
        content-align: center middle;
        background: $surface;
        border: solid $primary-background;
        margin: 0 1;
        text-style: bold;
    }
    
    TileWidget.tile-empty {
        background: $surface-darken-1;
        color: $text-muted;
    }
    """
    
    def __init__(self, value: int, row: int, col: int):
        """Initialize a tile widget.
        
        Args:
            value: Tile value (0 for empty)
            row: Grid row position
            col: Grid column position
        """
        super().__init__(id=f"tile-{row}-{col}")
        self.value = value
        self.row = row
        self.col = col
        self._update_classes()
    
    def _update_classes(self) -> None:
        """Update CSS classes based on value."""
        self.remove_class("tile-empty")
        if self.value == 0:
            self.add_class("tile-empty")
    
    def update_value(self, value: int) -> None:
        """Update the tile's value and refresh display.
        
        Args:
            value: New tile value
        """
        self.value = value
        self._update_classes()
        self.refresh()
    
    def render(self) -> str:
        """Render the tile content.
        
        Returns:
            String to display (empty string for 0)
        """
        return str(self.value) if self.value != 0 else ""


class GridWidget(Static):
    """The 4x4 game grid widget.
    
    Displays all tiles in a grid layout with proper styling.
    """
    
    DEFAULT_CSS = """
    GridWidget {
        width: 100%;
        height: 18;
        background: $surface-darken-2;
        border: solid $primary;
        padding: 1;
    }
    
    .tile-row {
        height: 4;
        width: 100%;
    }
    """
    
    def __init__(self, game: Game):
        """Initialize the grid widget.
        
        Args:
            game: Game instance to display
        """
        super().__init__()
        self.game = game
        self.tile_widgets: list[list[TileWidget]] = []
    
    def compose(self) -> ComposeResult:
        """Compose the grid layout."""
        self.tile_widgets = []
        for row in range(GRID_SIZE):
            row_widgets = []
            for col in range(GRID_SIZE):
                tile = TileWidget(
                    value=self.game.grid.cells[row][col],
                    row=row,
                    col=col
                )
                row_widgets.append(tile)
            self.tile_widgets.append(row_widgets)
            yield Horizontal(*row_widgets, classes="tile-row")
    
    def refresh_grid(self) -> None:
        """Refresh all tile values from the game state."""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                value = self.game.grid.cells[row][col]
                tile = self.tile_widgets[row][col]
                tile.update_value(value)
        self.refresh()


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
    }
    
    #moves-label {
        color: $text-muted;
    }
    
    #max-tile-label {
        color: $warning;
    }
    """
    
    def __init__(self, game: Game):
        """Initialize score widget.
        
        Args:
            game: Game instance
        """
        super().__init__()
        self.game = game
        self.score_label: Label | None = None
        self.moves_label: Label | None = None
        self.max_label: Label | None = None
    
    def compose(self) -> ComposeResult:
        """Compose score display."""
        self.score_label = Label(f"Score: {self.game.score}", id="score-label")
        self.moves_label = Label(f"Moves: {self.game.moves}", id="moves-label")
        self.max_label = Label(f"Max: {self.game.grid.get_max_tile()}", id="max-tile-label")
        yield Horizontal(self.score_label, self.moves_label, self.max_label)
    
    def update(self) -> None:
        """Update display with current game stats."""
        if self.score_label:
            self.score_label.update(f"Score: {self.game.score}")
        if self.moves_label:
            self.moves_label.update(f"Moves: {self.game.moves}")
        if self.max_label:
            self.max_label.update(f"Max: {self.game.grid.get_max_tile()}")


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
    
    #game-over-container {
        width: 50;
        height: auto;
        background: $surface;
        border: solid $error;
        padding: 2 4;
    }
    
    #game-over-title {
        text-align: center;
        text-style: bold;
        color: $error;
        padding: 1 0;
    }
    
    #game-over-message {
        text-align: center;
        padding: 1 0;
    }
    
    #game-over-score {
        text-align: center;
        text-style: bold;
        padding: 1 0;
    }
    
    #restart-btn {
        width: 100%;
        margin: 1 0;
    }
    """
    
    def __init__(self, game: Game):
        """Initialize game over modal.
        
        Args:
            game: Game instance
        """
        super().__init__()
        self.game = game
    
    def compose(self) -> ComposeResult:
        """Compose modal content."""
        state_text = "🎉 You Win!" if self.game.state == GameState.WON else "💀 Game Over"
        message_text = "You reached 2048!" if self.game.state == GameState.WON else "No more moves possible!"
        
        with Vertical(id="game-over-container"):
            yield Label(state_text, id="game-over-title")
            yield Label(message_text, id="game-over-message")
            yield Label(f"Final Score: {self.game.score}", id="game-over-score")
            yield Button("Play Again (Enter)", id="restart-btn", variant="primary")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "restart-btn":
            self.dismiss(True)  # Signal to restart
    
    def action_restart(self) -> None:
        """Restart the game."""
        self.dismiss(True)
    
    def action_quit(self) -> None:
        """Close the modal without restarting."""
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
        color: $text;
    }
    
    #controls-hint {
        text-align: center;
        color: $text-muted;
        padding: 0 0 1 0;
    }
    """
    
    def __init__(self, game: Game):
        """Initialize game screen.
        
        Args:
            game: Game instance
        """
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
            self.score_widget.update()
        if self.grid_widget:
            self.grid_widget.refresh_grid()
