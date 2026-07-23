#!/usr/bin/env python3
"""
3D Ludo Game - Main Entry Point
"""

import sys
import os
import time
from typing import Dict, Any

from engine.utils import GameConfig
from engine.game import Game, GameState
import engine.assets as asset_loader
import engine.renderer as renderer_helpers

class Main:

    """
    Main application class for 3D Ludo game.
    Handles application startup, main loop, and cleanup.
    """

    def __init__(self):
        """Initialize the main application."""
        self.config = GameConfig()
        self.game: Game = None
        self.is_running = False
        self.last_frame_time = time.time()
        self.screen = None # Add screen attribute

    def run(self) -> None:
        """Run the main application."""
        print(f"Starting {self.config.get('game', {}).get('title', '3D Ludo')} v{self.config.get('game', {}).get('version', '1.0.0')}")

        try:
            import pygame
            from OpenGL.GL import GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glClear
        except ImportError:
            print("Failed to import pygame or OpenGL")
            return

        try:
            # Initialize pygame
            pygame.init()
            pygame.display.set_caption(self.config.get('game', {}).get('title', '3D Ludo'))
            graphics_config = self.config.get_graphics_config()
            width = graphics_config.get('window_width', 800)
            height = graphics_config.get('window_height', 600)
            self.screen = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)

            # Initialize OpenGL viewport and projection
            from OpenGL.GL import glViewport, glEnable, glClearColor, glClearDepth, GL_DEPTH_TEST
            from OpenGL.GLU import gluPerspective
            glViewport(0, 0, width, height)
            glEnable(GL_DEPTH_TEST)
            glClearColor(0.1, 0.1, 0.1, 1.0)  # Dark gray background
            glClearDepth(1.0)
            
            # Set up projection matrix
            from OpenGL.GL import glMatrixMode, glLoadIdentity, GL_PROJECTION, GL_MODELVIEW
            from OpenGL.GLU import gluPerspective
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45, width / height, 0.1, 100.0)
            
            # Set up modelview matrix
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            from OpenGL.GLU import gluLookAt
            gluLookAt(0, 20, 20,  # Camera position
                     0, 0, 0,     # Look at origin
                     0, 1, 0)     # Up vector

            # Initialize game
            if not self.initialize():
                print("Failed to initialize game")
                return

            # Main game loop
            self.is_running = True
            self.on_enter()

            while self.is_running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.is_running = False
                    self.game.ui_system.handle_event(event) # Handle UI events

                self.update()
                self.render()
                pygame.display.flip() # Update the full display Surface to the screen

            self.on_exit()

        except Exception as e:
            print(f"Error in main loop: {e}")
            import traceback
            traceback.print_exc()

        finally:
            self.cleanup()
            pygame.quit() # Quit pygame

    def initialize(self) -> bool:
        """
        Initialize the game.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Load configuration
            game_config = self.config.get_gameplay_config()
            board_config = self.config.get('graphics', {}).get('board', {}) # Get board config from graphics
            dice_config = self.config.get('gameplay', {}).get('dice', {}) # Get dice config from gameplay
            sound_config = self.config.get_sound_system_config()
            animation_config = self.config.get_animation_system_config()
            ui_config = self.config.get_ui_system_config()
            game_modes_config = self.config.get_game_modes_config()
            login_config = self.config.get_login_system_config()
            microtransactions_config = self.config.get_microtransactions_config()

            # Create game instance with all configurations
            self.game = Game({
                'gameplay': game_config,
                'board': board_config,
                'pieces': {'types': ['classic', 'warrior', 'wizard', 'archer', 'king', 'queen']},
                'dice': dice_config,
                'sound': sound_config,
                'animation': animation_config,
                'ui': ui_config,
                'game_modes': game_modes_config,
                'login': login_config,
                'microtransactions': microtransactions_config,
                'require_login': game_config.get('require_login', False)
            })

            # Initialize the game
            if self.game.initialize_game():
                # Attempt to load prototype models (if present)
                try:
                    models = {}
                    for name in ('character.obj', 'board.obj'):
                        p = os.path.join('assets', 'models', name)
                        if os.path.exists(p):
                            loaded = asset_loader.try_load(p)
                            if loaded is not None:
                                mesh = None
                                if p.lower().endswith('.obj'):
                                    mesh = asset_loader.obj_to_numpy_mesh(loaded)
                                if mesh and 'positions' in mesh:
                                    upload = renderer_helpers.upload_positions_vbo(mesh['positions'])
                                    transform = {
                                        'translate': (0.0, 0.0, 0.0) if name.startswith('board') else (0.0, 0.15, 0.0),
                                        'scale': (2.0, 2.0, 2.0) if name.startswith('board') else (0.5, 0.5, 0.5),
                                        'rotate': (0.0, 0.0, 0.0)
                                    }
                                    models[name] = {'mesh': upload, 'transform': transform}
                                else:
                                    models[name] = {'mesh': loaded, 'transform': {'translate': (0.0, 0.0, 0.0), 'scale': (1.0, 1.0, 1.0)}}
                    if models:
                        print('Loaded prototype models:', list(models.keys()))
                        self.game.loaded_models = models
                except Exception as e:
                    print('Model load skipped:', e)

                print("Game initialized successfully")
                return True
            else:
                print("Failed to initialize game")
                return False

        except Exception as e:
            print(f"Error initializing game: {e}")
            import traceback
            traceback.print_exc()
            return False

    def update(self) -> None:
        """Update game state."""
        if not self.game:
            return

        # Calculate delta time
        current_time = time.time()
        delta_time = current_time - self.last_frame_time
        self.last_frame_time = current_time

        # Update game
        self.game.update(delta_time)

        # Update UI system
        self.game.ui_system.update()

        # Check if game is over
        if self.game.is_game_over():
            print("Game over!")
            self.is_running = False

    def render(self) -> None:
        """Render game."""
        if not self.game or not self.screen:
            return

        from OpenGL.GL import GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glClear

        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Render game
        self.game.render(self.screen)

    def on_enter(self) -> None:
        """Called when application enters main loop."""
        print("Application started")

    def on_exit(self) -> None:
        """Called when application exits."""
        print("Application exiting")

    def cleanup(self) -> None:
        """Cleanup resources."""
        if self.game:
            # Cleanup game systems
            self.game.animation_system.cleanup()
            self.game.sound_system.cleanup()
            self.game.ui_system.cleanup()

        print("Cleanup completed")

    def exit(self) -> None:
        """Exit the application."""
        self.is_running = False

if __name__ == '__main__':
    # Create and run main application
    app = Main()
    app.run()
