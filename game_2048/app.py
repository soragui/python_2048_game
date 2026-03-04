"""Main application entry point for the 2048 game.

This module ties together all components:
- Game logic
- TUI interface
- Event handling
"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.binding import Binding
from textual import events

from .game import Game, GameState
from .ui import GameScreen, GameOverModal
from .config import DIRECTIONS


class Game2048App(App):
    """The main 2048 game application.
    
    This is the entry point for the Textual application.
    It manages the game instance and handles user input.
    
    Usage:
        app = Game2048App()
        app.run()
    """
    
    # Application title
    TITLE = "2048"
    SUB_TITLE = "Terminal Edition"
    
    # CSS styles for the application
    CSS = """
    Screen {
        background: $surface;
    }
    
    #game-container {
        width: 100%;
        max-width: 60;
        height: 100%;
        align: center top;
    }
    """
    
    # Keyboard bindings - shown in footer
    BINDINGS = [
        # Movement keys (arrow keys and WASD)
        Binding("up", "move_up", "↑", show=True),
        Binding("down", "move_down", "↓", show=True),
        Binding("left", "move_left", "←", show=True),
        Binding("right", "move_right", "→", show=True),
        Binding("w", "move_up", "W", show=True),
        Binding("a", "move_left", "A", show=True),
        Binding("s", "move_down", "S", show=True),
        Binding("d", "move_right", "D", show=True),
        
        # Game controls
        Binding("r", "restart", "Restart"),
        Binding("q", "quit", "Quit"),
    ]
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.game = Game()
        self.game_screen: GameScreen | None = None
    
    def compose(self) -> ComposeResult:
        """Compose the application UI.
        
        This method is called once when the app starts.
        It creates all the widgets that make up the interface.
        """
        yield Header()
        yield GameScreen(self.game)
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when the app is mounted (ready to display).
        
        Use this for any initialization that needs the UI to be ready.
        """
        self.game_screen = self.query_one(GameScreen)
        self.refresh_display()
    
    def refresh_display(self) -> None:
        """Refresh all UI elements with current game state."""
        if self.game_screen:
            self.game_screen.update_display()
    
    def action_move_up(self) -> None:
        """Handle up movement."""
        self._attempt_move("up")
    
    def action_move_down(self) -> None:
        """Handle down movement."""
        self._attempt_move("down")
    
    def action_move_left(self) -> None:
        """Handle left movement."""
        self._attempt_move("left")
    
    def action_move_right(self) -> None:
        """Handle right movement."""
        self._attempt_move("right")
    
    def _attempt_move(self, direction: str) -> None:
        """Attempt to move tiles in the specified direction.
        
        Args:
            direction: Movement direction
        """
        if self.game.state == GameState.GAME_OVER:
            return
        
        moved = self.game.move(direction)
        
        if moved:
            self.refresh_display()
            
            # Check if game ended after this move
            if self.game.state in (GameState.WON, GameState.GAME_OVER):
                self._show_game_over()
        else:
            # Invalid move - give visual feedback
            self.bell()  # Play error sound
    
    def action_restart(self) -> None:
        """Restart the game."""
        self.game.reset()
        self.refresh_display()
        self.notify("Game restarted!", title="🔄")
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
    
    def action_show_help(self) -> None:
        """Show help information."""
        help_text = """
        [bold]How to Play:[/bold]
        • Use Arrow Keys or WASD to move tiles
        • Tiles with the same number merge when they collide
        • Reach the 2048 tile to win!
        
        [bold]Controls:[/bold]
        • ↑↓←→ or WASD: Move tiles
        • R: Restart game
        • Q: Quit
        • ?: Show this help
        """
        self.notify(help_text, title="📖 Help", timeout=10)
    
    def _show_game_over(self) -> None:
        """Show the game over modal."""
        def callback(restart: bool) -> None:
            """Handle modal dismissal.
            
            Args:
                restart: True if player wants to restart
            """
            if restart:
                self.game.reset()
                self.refresh_display()
        
        self.push_screen(GameOverModal(self.game), callback)
    
    def on_key(self, event: events.Key) -> None:
        """Handle key press events.
        
        This is a fallback for any keys not handled by bindings.
        
        Args:
            event: Key event
        """
        # Prevent default handling for game keys
        if event.key in ["up", "down", "left", "right", "w", "a", "s", "d"]:
            event.prevent_default()


def run_game() -> None:
    """Run the 2048 game application.
    
    This is the main entry point called from CLI.
    """
    app = Game2048App()
    app.run()


if __name__ == "__main__":
    run_game()
