"""
UI system for 3D Ludo (migrated into engine.systems).

This is a copy of `core/ui_system.py` placed under `engine/systems` to
serve as the migration target. It keeps the same public API.
"""
try:
    import pygame
except Exception:
    # Minimal pygame fallback for headless/testing environments
    class _DummyPygame:
        @staticmethod
        def quit():
            pass

    pygame = _DummyPygame()
import time
from typing import List, Dict, Any, Optional, Tuple, Callable
from enum import Enum
from dataclasses import dataclass
class UIElementType(Enum):
    BUTTON = "button"
    LABEL = "label"
    TEXT_INPUT = "text_input"
    SLIDER = "slider"
    CHECKBOX = "checkbox"
    RADIO_BUTTON = "radio_button"
    PANEL = "panel"
    PROGRESS_BAR = "progress_bar"
    DROPDOWN = "dropdown"
    TAB = "tab"
    SCROLL_PANEL = "scroll_panel"
    IMAGE = "image"
    VIDEO = "video"
    CANVAS = "canvas"
class ButtonState(Enum):
    NORMAL = "normal"
    HOVER = "hover"
    PRESSED = "pressed"
    DISABLED = "disabled"
    FOCUS = "focus"
@dataclass
class Button:
    """UI button element."""

    id: str
    position: Tuple[int, int]
    size: Tuple[int, int]
    text: str
    font_size: int = 24
    color_normal: Tuple[float, float, float] = (0.8, 0.8, 0.8)
    color_hover: Tuple[float, float, float] = (0.9, 0.9, 0.9)
    color_pressed: Tuple[float, float, float] = (0.7, 0.7, 0.7)
    color_disabled: Tuple[float, float, float] = (0.5, 0.5, 0.5)
    color_text: Tuple[float, float, float] = (0, 0, 0)
    icon: Optional[str] = None
    action: Optional[Callable[[], None]] = None
    tooltip: Optional[str] = None
    is_visible: bool = True
    is_enabled: bool = True
    state: ButtonState = ButtonState.NORMAL
    animation_duration: float = 0.2
    last_click_time: float = 0
class Label:
    """UI label element."""

    def __init__(self, id: str, position: Tuple[int, int], text: str,
                 font_size: int = 20, color: Tuple[float, float, float] = (0, 0, 0),
                 is_bold: bool = False, is_italic: bool = False,
                 is_visible: bool = True):
        self.id = id
        self.position = position
        self.text = text
        self.font_size = font_size
        self.color = color
        self.is_bold = is_bold
        self.is_italic = is_italic
        self.is_visible = is_visible

    def update_text(self, new_text: str) -> None:
        """Update label text."""
        self.text = new_text
class TextInput:
    """UI text input element."""

    def __init__(self, id: str, position: Tuple[int, int], size: Tuple[int, int],
                 placeholder: str = "", max_length: int = 50, is_password: bool = False,
                 is_visible: bool = True):
        self.id = id
        self.position = position
        self.size = size
        self.text = ""
        self.placeholder = placeholder
        self.max_length = max_length
        self.is_password = is_password
        self.is_visible = is_visible
        self.is_focused = False
        self.caret_position = len(self.text)
        self.caret_blink_time = 0
        self.caret_blink_interval = 0.5

    def add_character(self, char: str) -> None:
        """Add a character to input."""
        if len(self.text) < self.max_length:
            self.text = self.text[:self.caret_position] + char + self.text[self.caret_position:]
            self.caret_position += 1

    def remove_character(self) -> None:
        """Remove character at cursor position."""
        if self.caret_position > 0:
            self.text = self.text[:self.caret_position - 1] + self.text[self.caret_position:]
            self.caret_position -= 1

    def move_cursor(self, left: bool) -> None:
        """Move cursor."""
        if left:
            self.caret_position = max(0, self.caret_position - 1)
        else:
            self.caret_position = min(len(self.text), self.caret_position + 1)
class UISystem:
    """
    UI system for 3D Ludo.
    Handles user interface, game menus, and display elements.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the UI system with configuration.

        Args:
            config: UI system configuration dictionary
        """
        self.config = config
        self.is_enabled = config.get('enabled', True)
        self.font_size_multiplier = config.get('font_size_multiplier', 1.0)
        self.animation_speed = config.get('animation_speed', 1.0)
        self.theme = config.get('theme', 'light')

        # Screen dimensions
        self.screen_width = config.get('screen_width', 1920)
        self.screen_height = config.get('screen_height', 1080)

        # UI elements
        self.buttons: Dict[str, Button] = {}
        self.labels: Dict[str, Label] = {}
        self.text_inputs: Dict[str, TextInput] = {}
        self.panels: Dict[str, Dict[str, Any]] = {}

        # Current screen
        self.current_screen = 'main_menu'
        self.screen_stack: List[str] = ['main_menu']

        # UI state
        self.is_pause_menu_open = False
        self.is_settings_menu_open = False
        self.is_game_over_menu_open = False
        self.selected_button: Optional[str] = None

        # Input state
        self.mouse_position = (0, 0)
        self.mouse_buttons = {'left': False, 'right': False}
        self.keyboard_keys: Dict[str, bool] = {}

        # Audio feedback
        self.sound_enabled = config.get('sound_enabled', True)

        # Initialize UI
        self._initialize_ui()

    def _initialize_ui(self) -> None:
        """Initialize UI elements."""
        # Create main menu buttons
        self._create_main_menu()

        # Create game UI elements
        self._create_game_ui()

        # Create settings menu
        self._create_settings_menu()

        # Create game over menu
        self._create_game_over_menu()

    def _create_main_menu(self) -> None:
        """Create main menu UI elements."""
        # New Game button
        new_game_button = Button(
            id='new_game',
            position=(self.screen_width // 2 - 150, self.screen_height // 2 - 50),
            size=(300, 60),
            text='New Game',
            action=self.start_new_game,
            tooltip='Start a new game'
        )
        self.buttons['new_game'] = new_game_button

        # Load Game button
        load_game_button = Button(
            id='load_game',
            position=(self.screen_width // 2 - 150, self.screen_height // 2 + 20),
            size=(300, 60),
            text='Load Game',
            action=self.load_game,
            tooltip='Load a saved game'
        )
        self.buttons['load_game'] = load_game_button

        # Settings button
        settings_button = Button(
            id='settings',
            position=(self.screen_width // 2 - 150, self.screen_height // 2 + 90),
            size=(300, 60),
            text='Settings',
            action=self.open_settings,
            tooltip='Open settings menu'
        )
        self.buttons['settings'] = settings_button

        # Exit button
        exit_button = Button(
            id='exit',
            position=(self.screen_width // 2 - 150, self.screen_height // 2 + 160),
            size=(300, 60),
            text='Exit',
            action=self.exit_game,
            tooltip='Exit the game'
        )
        self.buttons['exit'] = exit_button

        # Title label
        title_label = Label(
            id='title',
            position=(self.screen_width // 2 - 200, self.screen_height // 2 - 120),
            text='3D Ludo',
            font_size=48,
            color=(0.2, 0.2, 0.8)
        )
        self.labels['title'] = title_label

    def _create_game_ui(self) -> None:
        """Create in-game UI elements."""
        # Score display panels
        for i in range(4):  # Assuming 4 players
            panel_id = f'player_{i}_score'
            self.panels[panel_id] = {
                'position': (50, 50 + i * 80),
                'size': (200, 60),
                'color': self._get_player_color(i),
                'title': f'Player {i + 1}'
            }

        # Current turn indicator
        self.labels['current_turn'] = Label(
            id='current_turn',
            position=(self.screen_width - 300, 50),
            text='Player 1 Turn',
            font_size=24,
            color=(0, 0.5, 0)
        )

        # Dice result display
        self.labels['dice_result'] = Label(
            id='dice_result',
            position=(self.screen_width // 2 - 100, self.screen_height - 100),
            text='Roll: -',
            font_size=32,
            color=(0.5, 0, 0)
        )

        # Selected piece indicator
        self.labels['selected_piece'] = Label(
            id='selected_piece',
            position=(self.screen_width - 300, self.screen_height - 200),
            text='Select a piece',
            font_size=20,
            color=(0, 0, 0.5)
        )

        # Roll button
        roll_button = Button(
            id='roll_dice',
            position=(self.screen_width // 2 - 100, self.screen_height - 150),
            size=(200, 60),
            text='Roll Dice',
            action=self.roll_dice,
            tooltip='Roll dice to move'
        )
        self.buttons['roll_dice'] = roll_button

    def _create_settings_menu(self) -> None:
        """Create settings menu UI elements."""
        # Resolution dropdown
        resolution_dropdown = self._create_dropdown(
            id='resolution',
            position=(200, 150),
            size=(300, 40),
            label='Resolution:',
            options=['1920x1080', '1600x900', '1280x720', '1024x576']
        )
        self.panels['resolution_dropdown'] = resolution_dropdown

        # Volume slider
        volume_slider = self._create_slider(
            id='volume',
            position=(200, 250),
            size=(300, 40),
            label='Volume:',
            min_value=0.0,
            max_value=1.0,
            default_value=0.7
        )
        self.panels['volume_slider'] = volume_slider

        # Music volume slider
        music_volume_slider = self._create_slider(
            id='music_volume',
            position=(200, 350),
            size=(300, 40),
            label='Music Volume:',
            min_value=0.0,
            max_value=1.0,
            default_value=0.5
        )
        self.panels['music_volume_slider'] = music_volume_slider

        # Sound effects slider
        sfx_slider = self._create_slider(
            id='sfx_volume',
            position=(200, 450),
            size=(300, 40),
            label='Sound Effects Volume:',
            min_value=0.0,
            max_value=1.0,
            default_value=0.8
        )
        self.panels['sfx_slider'] = sfx_slider

        # Apply settings button
        apply_button = Button(
            id='apply_settings',
            position=(self.screen_width // 2 - 150, self.screen_height - 100),
            size=(300, 60),
            text='Apply Settings',
            action=self.apply_settings,
            tooltip='Apply current settings'
        )
        self.buttons['apply_settings'] = apply_button

        # Cancel button
        cancel_button = Button(
            id='cancel_settings',
            position=(self.screen_width // 2 - 150, self.screen_height - 200),
            size=(300, 60),
            text='Cancel',
            action=self.close_settings,
            tooltip='Cancel settings'
        )
        self.buttons['cancel_settings'] = cancel_button

        # Settings title
        settings_title = Label(
            id='settings_title',
            position=(self.screen_width // 2 - 200, 50),
            text='Settings',
            font_size=36,
            color=(0.2, 0.2, 0.2)
        )
        self.labels['settings_title'] = settings_title

    def _create_game_over_menu(self) -> None:
        """Create game over menu UI elements."""
        # Game over title
        game_over_title = Label(
            id='game_over_title',
            position=(self.screen_width // 2 - 150, 100),
            text='Game Over',
            font_size=48,
            color=(0.8, 0, 0)
        )
        self.labels['game_over_title'] = game_over_title

        # Winner label
        winner_label = Label(
            id='winner_label',
            position=(self.screen_width // 2 - 150, 200),
            text='Player 1 Wins!',
            font_size=32,
            color=(0, 0.5, 0)
        )
        self.labels['winner_label'] = winner_label

        # Play again button
        play_again_button = Button(
            id='play_again',
            position=(self.screen_width // 2 - 150, 350),
            size=(300, 60),
            text='Play Again',
            action=self.play_again,
            tooltip='Start a new game'
        )
        self.buttons['play_again'] = play_again_button

    # --- Minimal action handlers and helpers (kept simple for tests) ---
    def start_new_game(self) -> None:
        self.current_screen = 'game'

    def load_game(self) -> None:
        self.current_screen = 'game'

    def open_settings(self) -> None:
        self.is_settings_menu_open = True

    def exit_game(self) -> None:
        self.current_screen = 'exit'

    def roll_dice(self) -> int:
        import random
        return random.randint(1, 6)

    def apply_settings(self) -> None:
        # Apply basic settings from panels if present
        if 'volume' in self.panels:
            self.sound_enabled = self.panels.get('volume', {}).get('default_value', 0.7) > 0

    def close_settings(self) -> None:
        self.is_settings_menu_open = False

    def play_again(self) -> None:
        self.current_screen = 'main_menu'

    def _create_dropdown(self, id: str, position, size, label: str, options: list):
        return {'id': id, 'position': position, 'size': size, 'label': label, 'options': options, 'selected': options[0] if options else None}

    def _create_slider(self, id: str, position, size, label: str, min_value: float, max_value: float, default_value: float):
        return {'id': id, 'position': position, 'size': size, 'label': label, 'min': min_value, 'max': max_value, 'default_value': default_value}

    def _get_player_color(self, i: int):
        colors = [
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
            (1.0, 1.0, 0.0),
        ]
        return colors[i % len(colors)]

    def handle_event(self, event: Any) -> None:
        """Handle input events for UI interactions."""
        if not self.is_enabled:
            return

        event_type = getattr(event, 'type', None)
        if event_type is None:
            return

        # Example: respond to mouse clicks by invoking button actions
        if event_type == getattr(pygame, 'MOUSEBUTTONDOWN', None):
            mouse_pos = getattr(event, 'pos', None)
            if mouse_pos:
                for button in self.buttons.values():
                    x, y = button.position
                    w, h = button.size
                    if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                        if button.action and callable(button.action):
                            button.action()
                            break

    def update(self) -> None:
        """Update UI state."""
        if not self.is_enabled:
            return

        # Placeholder for UI state updates, animations, or transitions.
        return

    def render(self, screen) -> None:
        """Render UI components to the screen."""
        if not self.is_enabled:
            return

        # UI rendering is handled by the engine frontend or fallback renderer.
        return

    def render_turn_info(self, screen, current_player, game_state: Dict[str, Any]) -> None:
        """Render turn information on screen."""
        if not self.is_enabled:
            return

        # Placeholder: in a real implementation, this would draw labels.
        return

    def render_score(self, screen, players) -> None:
        """Render player scores on screen."""
        if not self.is_enabled:
            return

        return

    def cleanup(self) -> None:
        """Cleanup UI resources."""
        self.buttons.clear()
        self.labels.clear()
        self.text_inputs.clear()
        self.panels.clear()
        self.screen_stack.clear()
        self.current_screen = 'main_menu'
        self.selected_button = None
        self.is_pause_menu_open = False
        self.is_settings_menu_open = False
        self.is_game_over_menu_open = False
        self.mouse_position = (0, 0)
        self.mouse_buttons = {'left': False, 'right': False}
        self.keyboard_keys.clear()

