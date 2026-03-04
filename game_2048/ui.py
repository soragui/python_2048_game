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
    
    def __init__(self, value: int, row: int, col: int):
        """Initialize a tile widget.
        
        Args:
            value: Tile value (0 for empty)
            row: Grid row position
            col: Grid column position
        """
        super().__init__()
        self.value = value
        self.row = row
        self.col = col
    
    def update_value(self, value: int) -> None:
        """Update the tile's value and refresh display.
        
        Args:
            value: New tile value
        """
        self.value = value
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
        height: auto;
        max-height: 20;
        background: $surface-darken-2;
        border: solid $primary;
        padding: 1;
    }
    
    .tile-row {
        height: 4;
        width: 100%;
    }
    
    .tile-cell {
        width: 1fr;
        height: 100%;
        content-align: center middle;
        background: $surface;
        border: solid $primary-background;
        margin: 0 1;
        text-style: bold;
    }
    
    .tile-empty {
        background: $surface-darken-1;
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
        self._create_tile_grid()
    
    def _create_tile_grid(self) -> None:
        """Create the 2D array of tile widgets."""
        self.tile_widgets = []
        for row in range(GRID_SIZE):
            row_widgets = []
            for col in range(GRID_SIZE):
                tile = TileWidget(
                    value=self.game.grid.cells[row][col],
                    row=row,
                    col=col
                )
                tile.add_class("tile-cell")
                if self.game.grid.cells[row][col] == 0:
                    tile.add_class("tile-empty")
                row_widgets.append(tile)
            self.tile_widgets.append(row_widgets)
    
    def compose(self) -> ComposeResult:
        """Compose the grid layout."""
        for row in range(GRID_SIZE):
            row_container = Horizontal(classes="tile-row")
            for col in range(GRID_SIZE):
                row_container.mount(self.tile_widgets[row][col])
            yield row_container
    
    def refresh_grid(self) -> None:
        """Refresh all tile values from the game state."""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                value = self.game.grid.cells[row][col]
                tile = self.tile_widgets[row][col]
                tile.update_value(value)
                
                # Update styling based on value
                tile.remove_class("tile-empty")
                if value == 0:
                    tile.add_class("tile-empty")
        
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
    
    def compose(self) -> ComposeResult:
        """Compose score display."""
        yield Horizontal(
            Label(f"Score: {self.game.score}", id="score-label"),
            Label(f"Moves: {self.game.moves}", id="moves-label"),
            Label(f"Max: {self.game.grid.get_max_tile()}", id="max-tile-label"),
        )
    
    def update(self) -> None:
        """Update display with current game stats."""
        self.query_one("#score-label", Label).update(f"Score: {self.game.score}")
        self.query_one("#moves-label", Label).update(f"Moves: {self.game.moves}")
        self.query_one("#max-tile-label", Label).update(f"Max: {self.game.grid.get_max_tile()}")


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
        
        yield Vertical(
            Label(state_text, id="game-over-title"),
            Label(message_text, id="game-over-message"),
            Label(f"Final Score: {self.game.score}", id="game-over-score"),
            Button("Play Again (Enter)", id="restart-btn", variant="primary"),
            id="game-over-container"
        )
    
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


class GameScreen(Static):
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
