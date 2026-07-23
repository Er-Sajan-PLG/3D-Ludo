"""
Game board/arena system for 3D Ludo.
This module handles the board geometry, positions, and arena setup.
"""

import math
from typing import List, Dict, Any, Tuple, Optional, TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass
# pyrefly: ignore [missing-import]
try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
except ImportError:
    # Dummy OpenGL constants and functions for headless/no-OpenGL testing
    GL_TEXTURE_2D = 0
    GL_QUADS = 0
    GL_POINTS = 0
    GL_LINE_LOOP = 0
    GL_COLOR_BUFFER_BIT = 0
    GL_DEPTH_BUFFER_BIT = 0
    def glEnable(x): pass
    def glBegin(x): pass
    def glEnd(): pass
    def glColor3f(r,g,b): pass
    def glColor4f(r,g,b,a): pass
    def glVertex3f(x,y,z): pass
    def glLineWidth(w): pass
    def glPointSize(s): pass
if TYPE_CHECKING:
    from .pieces import Pieces

class BoardType(Enum):
    CLASSIC = "classic"
    CIRCULAR = "circular"
    HEXAGONAL = "hexagonal"
    TRIANGULAR = "triangular"
class PositionType(Enum):
    START = "start"
    SAFE_ZONE = "safe_zone"
    NORMAL = "normal"
    SPECIAL = "special"
    EXIT = "exit"
class Board:
    """
    3D game board/arena system.
    Handles board geometry, position mapping, and arena setup.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the board with configuration.

        Args:
            config: Board configuration dictionary
        """
        self.config = config
        self.board_type = BoardType(config.get('type', 'classic'))
        self.size = config.get('size', {'width': 20, 'height': 20, 'depth': 0})
        self.cell_size = config.get('cell_size', 1.0)
        self.path_width = config.get('path_width', 0.5)

        # Position mapping
        self.positions: Dict[int, Dict[str, Any]] = {}
        self.safe_zones: Dict[int, List[int]] = {}
        self.exit_positions: Dict[int, int] = {}

        # 3D rendering
        self.vertices: List[Tuple[float, float, float]] = []
        self.colors: List[Tuple[float, float, float, float]] = []
        self.indices: List[int] = []

        # Initialize board
        self.initialize_board()

    def initialize_board(self) -> None:
        """Initialize the board layout and positions."""
        if self.board_type == BoardType.CLASSIC:
            self._setup_classic_board()
        elif self.board_type == BoardType.CIRCULAR:
            self._setup_circular_board()
        elif self.board_type == BoardType.HEXAGONAL:
            self._setup_hexagonal_board()
        elif self.board_type == BoardType.TRIANGULAR:
            self._setup_triangular_board()

    def _setup_classic_board(self) -> None:
        """Setup a classic 4-track ludo board."""
        # Classic Ludo board: 4 tracks, each with 52 positions
        tracks = 4
        positions_per_track = 52
        start_positions = [0, 13, 26, 39]  # Each track's starting position

        position_id = 0
        for track in range(tracks):
            # Calculate track path
            track_positions = self._calculate_track_path(track, positions_per_track)

            for i, pos_info in enumerate(track_positions):
                pos_id = position_id + i
                self.positions[pos_id] = {
                    'position_id': pos_id,
                    'track': track,
                    'position_in_track': i,
                    'type': self._get_position_type(pos_id, track, pos_info['safe'], pos_info['special_effect']),
                    'coordinates': pos_info['coordinates'],
                    'safe': pos_info['safe'],
                    'special_effect': pos_info['special_effect']
                }

                # Track safe zones
                if pos_info['safe']:
                    if track not in self.safe_zones:
                        self.safe_zones[track] = []
                    self.safe_zones[track].append(pos_id)

                # Track exit positions
                if pos_id in [start_positions[0], start_positions[1], start_positions[2], start_positions[3]]:
                    self.exit_positions[track] = pos_id

            position_id += positions_per_track

        # Setup 3D rendering data
        self._setup_rendering_data()

    def _setup_circular_board(self) -> None:
        """Setup a circular board (arena)."""
        # Circular board with radial paths
        num_segments = 8
        positions_per_segment = 20
        radius = self.size['width'] / 2

        position_id = 0
        for segment in range(num_segments):
            segment_angle = (segment * 2 * math.pi) / num_segments
            segment_positions = self._calculate_circular_segment(segment, segment_angle, positions_per_segment)

            for i, pos_info in enumerate(segment_positions):
                pos_id = position_id + i
                self.positions[pos_id] = {
                    'position_id': pos_id,
                    'segment': segment,
                    'position_in_segment': i,
                    'type': self._get_circular_position_type(pos_id, segment, pos_info['special_effect']),
                    'coordinates': pos_info['coordinates'],
                    'safe': pos_info['safe'],
                    'special_effect': pos_info['special_effect']
                }

                if pos_info['safe']:
                    if segment not in self.safe_zones:
                        self.safe_zones[segment] = []
                    self.safe_zones[segment].append(pos_id)

            position_id += positions_per_segment

        self._setup_rendering_data()

    def _setup_hexagonal_board(self) -> None:
        """Setup a hexagonal board."""
        # Hexagonal board with 6-sided paths
        num_sides = 6
        positions_per_side = 24
        side_length = self.size['width'] / (num_sides * 2)

        position_id = 0
        for side in range(num_sides):
            side_angle = (side * 2 * math.pi) / num_sides
            side_positions = self._calculate_hexagonal_side(side, side_angle, positions_per_side)

            for i, pos_info in enumerate(side_positions):
                pos_id = position_id + i
                self.positions[pos_id] = {
                    'position_id': pos_id,
                    'side': side,
                    'position_in_side': i,
                    'type': self._get_hexagonal_position_type(pos_id, side, pos_info['special_effect']),
                    'coordinates': pos_info['coordinates'],
                    'safe': pos_info['safe'],
                    'special_effect': pos_info['special_effect']
                }

                if pos_info['safe']:
                    if side not in self.safe_zones:
                        self.safe_zones[side] = []
                    self.safe_zones[side].append(pos_id)

            position_id += positions_per_side

        self._setup_rendering_data()

    def _setup_triangular_board(self) -> None:
        """Setup a triangular board."""
        # Triangular board with 3 paths
        num_paths = 3
        positions_per_path = 36
        triangle_size = self.size['width']

        position_id = 0
        for path in range(num_paths):
            path_angle = (path * 2 * math.pi) / num_paths
            path_positions = self._calculate_triangular_path(path, path_angle, positions_per_path)

            for i, pos_info in enumerate(path_positions):
                pos_id = position_id + i
                self.positions[pos_id] = {
                    'position_id': pos_id,
                    'path': path,
                    'position_in_path': i,
                    'type': self._get_triangular_position_type(pos_id, path, pos_info['special_effect']),
                    'coordinates': pos_info['coordinates'],
                    'safe': pos_info['safe'],
                    'special_effect': pos_info['special_effect']
                }

                if pos_info['safe']:
                    if path not in self.safe_zones:
                        self.safe_zones[path] = []
                    self.safe_zones[path].append(pos_id)

            position_id += positions_per_path

        self._setup_rendering_data()

    def _calculate_track_path(self, track: int, positions_per_track: int) -> List[Dict[str, Any]]:
        """Calculate the path for a specific track."""
        positions = []
        width = self.size['width']
        height = self.size['height']

        # Each track has 4 sides in a loop
        side_length = positions_per_track // 4

        for i in range(positions_per_track):
            side = i // side_length
            side_pos = i % side_length

            x, z = self._get_track_coordinates(track, side, side_pos, side_length, width, height)

            # Determine if this is a safe position for the track
            safe = side_pos < 6

            # Determine special effect
            special_effect = None
            if i % 13 == 0 and i != 0:  # Ladder positions
                special_effect = 'ladder'
            elif i % 13 == 6 and i != 0:  # Snake positions
                special_effect = 'snake'

            positions.append({
                'coordinates': (x, 0, z),
                'safe': safe,
                'special_effect': special_effect
            })

        return positions

    def _calculate_circular_segment(self, segment: int, segment_angle: float, positions_per_segment: int) -> List[Dict[str, Any]]:
        """Calculate positions for a circular board segment."""
        positions = []
        radius = self.size['width'] / 2

        for i in range(positions_per_segment):
            # Spiral from center outward
            distance = (i * radius) / positions_per_segment
            angle = (i * 4 * math.pi) / positions_per_segment + segment_angle

            x = distance * math.cos(angle)
            z = distance * math.sin(angle)
            y = 0

            safe = (i % 7 == 0)  # Every 7th position is safe

            special_effect = None
            if i % 10 == 0:
                special_effect = 'ladder'
            elif i % 10 == 5:
                special_effect = 'snake'

            positions.append({
                'coordinates': (x, y, z),
                'safe': safe,
                'special_effect': special_effect
            })

        return positions

    def _calculate_hexagonal_side(self, side: int, side_angle: float, positions_per_side: int) -> List[Dict[str, Any]]:
        """Calculate positions for a hexagonal board side."""
        positions = []
        side_length = self.size['width'] / 3

        for i in range(positions_per_side):
            # Go from center to edge and back
            progress = i / (positions_per_side - 1)
            distance = side_length * min(progress, 1 - progress)

            # Position along the side
            side_pos_angle = side_angle + (progress * math.pi / 3)

            x = distance * math.cos(side_pos_angle)
            z = distance * math.sin(side_pos_angle)
            y = 0

            safe = (i % 8 == 0)
            special_effect = None
            if i % 12 == 0:
                special_effect = 'ladder'
            elif i % 12 == 6:
                special_effect = 'snake'

            positions.append({
                'coordinates': (x, y, z),
                'safe': safe,
                'special_effect': special_effect
            })

        return positions

    def _calculate_triangular_path(self, path: int, path_angle: float, positions_per_path: int) -> List[Dict[str, Any]]:
        """Calculate positions for a triangular board path."""
        positions = []
        triangle_size = self.size['width']

        for i in range(positions_per_path):
            # Move along triangle sides
            side = i // (positions_per_path // 3)
            side_pos = (i % (positions_per_path // 3)) / (positions_per_path // 3)

            # Calculate position on triangle side
            side_angle_offset = (path * 2 * math.pi / 3) + (side * math.pi / 3)
            x = triangle_size * side_pos * math.cos(side_angle_offset)
            z = triangle_size * side_pos * math.sin(side_angle_offset)
            y = 0

            # Determine if position is safe (corners)
            safe = (side_pos > 0.9)  # Last 10% of each side is safe

            special_effect = None
            if i % 15 == 0 and i != 0:
                special_effect = 'ladder'
            elif i % 15 == 7 and i != 0:
                special_effect = 'snake'

            positions.append({
                'coordinates': (x, y, z),
                'safe': safe,
                'special_effect': special_effect
            })

        return positions

    def _get_track_coordinates(self, track: int, side: int, position: int, side_length: int, width: float, height: float) -> Tuple[float, float]:
        """Get 2D coordinates for a track position."""
        track_width = width / 4
        track_offset = track * track_width

        # Calculate position within the track
        if side == 0:  # Top side
            x = track_offset + (position * track_width / side_length)
            z = height
        elif side == 1:  # Right side
            x = width
            z = height - (position * height / side_length)
        elif side == 2:  # Bottom side
            x = track_offset + (position * track_width / side_length)
            z = 0
        else:  # Left side
            x = 0
            z = (position * height / side_length)

        return x, z

    def _get_position_type(self, position_id: int, track: int, safe: bool = False, special_effect: Optional[str] = None) -> str:
        """Get position type for a classic board position."""
        if special_effect in ('ladder', 'snake'):
            return special_effect
        if position_id in [0, 13, 26, 39]:  # Start positions
            return PositionType.START.value
        if safe:
            return PositionType.SAFE_ZONE.value
        return PositionType.NORMAL.value

    def _get_circular_position_type(self, position_id: int, segment: int, special_effect: Optional[str] = None) -> str:
        """Get position type for a circular board position."""
        if special_effect in ('ladder', 'snake'):
            return special_effect
        if position_id == 0:  # Center position
            return PositionType.START.value
        if position_id in self.safe_zones.get(segment, []):
            return PositionType.SAFE_ZONE.value
        return PositionType.NORMAL.value

    def _get_hexagonal_position_type(self, position_id: int, side: int, special_effect: Optional[str] = None) -> str:
        """Get position type for a hexagonal board position."""
        if special_effect in ('ladder', 'snake'):
            return special_effect
        if position_id == 0:  # Start position
            return PositionType.START.value
        if position_id in self.safe_zones.get(side, []):
            return PositionType.SAFE_ZONE.value
        return PositionType.NORMAL.value

    def _get_triangular_position_type(self, position_id: int, path: int, special_effect: Optional[str] = None) -> str:
        """Get position type for a triangular board position."""
        if special_effect in ('ladder', 'snake'):
            return special_effect
        if position_id == 0:  # Start position
            return PositionType.START.value
        if position_id in self.safe_zones.get(path, []):
            return PositionType.SAFE_ZONE.value
        return PositionType.NORMAL.value

    def _setup_rendering_data(self) -> None:
        """Setup 3D rendering data for the board."""
        # Generate board geometry (simplified)
        width = self.size['width']
        height = self.size['height']
        depth = self.size.get('depth', 0)

        # Generate floor grid
        grid_size = 20
        grid_step = width / grid_size

        for x in range(grid_size + 1):
            for z in range(grid_size + 1):
                self.vertices.append((x * grid_step - width/2, 0, z * grid_step - width/2))
                self.colors.append((0.3, 0.3, 0.3, 1.0))  # Gray floor

        # Create simple checkerboard pattern
        for x in range(grid_size):
            for z in range(grid_size):
                if (x + z) % 2 == 0:
                    self.indices.extend([
                        x * (grid_size + 1) + z,
                        (x + 1) * (grid_size + 1) + z,
                        x * (grid_size + 1) + z + 1,
                        (x + 1) * (grid_size + 1) + z,
                        (x + 1) * (grid_size + 1) + z + 1,
                        x * (grid_size + 1) + z + 1
                    ])

    def get_position_info(self, position_id: int) -> Dict[str, Any]:
        """
        Get information about a specific position.

        Args:
            position_id: The position ID

        Returns:
            Dictionary with position information
        """
        return self.positions.get(position_id, {
            'position_id': position_id,
            'track': 0,
            'position_in_track': 0,
            'type': 'unknown',
            'coordinates': (0, 0, 0),
            'safe': False,
            'special_effect': None
        })

    def is_valid_position(self, position_id: int) -> bool:
        """
        Check if a position ID is valid.

        Args:
            position_id: The position ID to check

        Returns:
            True if position is valid, False otherwise
        """
        return position_id in self.positions

    def is_safe_position(self, position_id: int) -> bool:
        """
        Check if the given position is a safe zone.

        Args:
            position_id: The position ID to check

        Returns:
            True if the position is a safe zone, False otherwise
        """
        position_info = self.get_position_info(position_id)
        return position_info.get('type') == PositionType.SAFE_ZONE.value

    def get_safe_zone_positions(self, player_id: int) -> List[int]:
        """
        Get safe zone positions for a player.

        Args:
            player_id: Player ID (0-3 for classic board)

        Returns:
            List of safe zone position IDs
        """
        if self.board_type == BoardType.CLASSIC:
            track = player_id
            return self.safe_zones.get(track, [])
        else:
            # For other board types, return safe zones for all tracks
            return [pos for track_zones in self.safe_zones.values() for pos in track_zones]

    def get_position_coordinates(self, position_id: int) -> Tuple[float, float, float]:
        """
        Get 3D coordinates for a position.

        Args:
            position_id: The position ID

        Returns:
            Tuple of (x, y, z) coordinates
        """
        pos_info = self.get_position_info(position_id)
        return pos_info['coordinates']

    def setup_board(self, players: List, pieces: 'Pieces') -> None:
        """
        Setup the board with player pieces.

        Args:
            players: List of player objects
            pieces: Pieces object managing all pieces
        """
        # Place each player's pieces at their starting positions
        for player in players:
            player_track = player.player_id  # Player 0 uses track 0, etc.

            for piece in pieces.get_player_pieces(player.player_id):
                start_position = self.exit_positions.get(player_track, 0)
                piece.position = start_position
                piece.is_selected = False
                piece.reached_end = False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert board to dictionary for saving.

        Returns:
            Dictionary representation of board
        """
        return {
            'board_type': self.board_type.value,
            'size': self.size,
            'cell_size': self.cell_size,
            'path_width': self.path_width,
            'positions': {str(k): v for k, v in self.positions.items()},
            'safe_zones': self.safe_zones,
            'exit_positions': self.exit_positions
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load board from dictionary.

        Args:
            data: Dictionary representation of board
        """
        self.board_type = BoardType(data['board_type'])
        self.size = data['size']
        self.cell_size = data['cell_size']
        self.path_width = data['path_width']
        self.positions = {int(k): v for k, v in data['positions'].items()}
        self.safe_zones = data['safe_zones']
        self.exit_positions = data['exit_positions']

    def render(self, screen) -> None:
        """
        Render the board to the screen.

        Args:
            screen: The rendering surface
        """
        # Try OpenGL rendering first
        try:
            from OpenGL.GL import glEnable, glBegin, glEnd, glColor4f, glVertex3f, glLineWidth, glColor3f, GL_TEXTURE_2D, GL_QUADS, GL_POINTS
            
            # Enable texturing
            glEnable(GL_TEXTURE_2D)

            # Draw floor
            glBegin(GL_QUADS)
            for i in range(0, len(self.indices), 6):
                for j in range(6):
                    idx = self.indices[i + j]
                    glColor4f(*self.colors[idx])
                    glVertex3f(*self.vertices[idx])
            glEnd()

            # Draw path outlines
            glLineWidth(2.0)
            glColor3f(0.2, 0.2, 0.2)  # Dark gray paths

            # Draw track paths based on board type
            if self.board_type == BoardType.CLASSIC:
                self._render_classic_path(screen)
            elif self.board_type == BoardType.CIRCULAR:
                self._render_circular_path(screen)
            elif self.board_type == BoardType.HEXAGONAL:
                self._render_hexagonal_path(screen)
            elif self.board_type == BoardType.TRIANGULAR:
                self._render_triangular_path(screen)
        except (ImportError, Exception):
            # Fallback to 2D pygame rendering
            self._render_2d(screen)

    def _render_classic_path(self, screen) -> None:
        """Render classic board paths."""
        # This would normally use OpenGL to render path geometry
        # For simplicity, we'll just draw simple markers at each position
        try:
            import pygame
            # Draw colored rectangles for each position on the board
            cell_size = 15  # pixels per cell
            spacing = 20    # spacing between cells
            
            # Draw a visible grid pattern for the classic board
            for track in range(4):
                track_positions = [pos for pos_id, pos in self.positions.items() if pos['track'] == track]
                
                # Arrange positions in a visible pattern
                for idx, pos_info in enumerate(track_positions[:13]):  # Show first 13 positions per track
                    x, y, z = pos_info['coordinates']
                    color = self._get_position_color(pos_info)
                    # Convert OpenGL coords to screen coords (approximate)
                    screen_x = int((x + 2) * 40 + 400)
                    screen_y = int((z + 2) * 40 + 300)
                    
                    # Draw position marker - filled rectangle with border
                    rect = pygame.Rect(screen_x, screen_y, cell_size, cell_size)
                    color_int = [int(c * 255) for c in color]
                    pygame.draw.rect(screen, color_int, rect, 0)  # Filled
                    pygame.draw.rect(screen, [min(c+50, 255) for c in color_int], rect, 2)  # Border
        except Exception as e:
            print(f"Error rendering classic path: {e}")
            # Fallback to OpenGL rendering
            glPointSize(5.0)
            glBegin(GL_POINTS)

            for track in range(4):
                for pos_id, pos_info in self.positions.items():
                    if pos_info['track'] == track:
                        x, y, z = pos_info['coordinates']
                        color = self._get_position_color(pos_info)
                        glColor3f(*color)
                        glVertex3f(x, y, z)

            glEnd()

    def _render_circular_path(self, screen) -> None:
        """Render circular board paths."""
        # Draw circular rings
        glColor3f(0.1, 0.1, 0.1)
        glBegin(GL_LINE_LOOP)

        for i in range(20):
            angle = (i * 2 * math.pi) / 20
            radius = (i * self.size['width']) / 20
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            glVertex3f(x, 0, z)

        glEnd()

    def _render_hexagonal_path(self, screen) -> None:
        """Render hexagonal board paths."""
        # Draw hexagon
        glColor3f(0.1, 0.1, 0.1)
        glBegin(GL_LINE_LOOP)

        for i in range(6):
            angle = (i * 2 * math.pi) / 6
            x = self.size['width'] * math.cos(angle)
            z = self.size['width'] * math.sin(angle)
            glVertex3f(x, 0, z)

        glEnd()

    def _render_triangular_path(self, screen) -> None:
        """Render triangular board paths."""
        # Draw triangle
        glColor3f(0.1, 0.1, 0.1)
        glBegin(GL_LINE_LOOP)

        for i in range(3):
            angle = (i * 2 * math.pi) / 3
            x = self.size['width'] * math.cos(angle)
            z = self.size['width'] * math.sin(angle)
            glVertex3f(x, 0, z)

        glEnd()

    def _get_position_color(self, pos_info: Dict[str, Any]) -> Tuple[float, float, float]:
        """
        Get color for a position based on its type.

        Args:
            pos_info: Position information

        Returns:
            RGB color tuple
        """
        position_type = pos_info['type']

        if position_type == PositionType.START.value:
            return (0.5, 0.5, 0.5)  # Gray for start
        elif position_type == PositionType.SAFE_ZONE.value:
            return (0.2, 0.8, 0.2)  # Green for safe zone
        elif position_type == PositionType.NORMAL.value:
            return (0.7, 0.7, 0.7)  # Light gray for normal
        elif pos_info['special_effect'] == 'ladder':
            return (0.8, 0.2, 0.2)  # Red for ladder
        elif pos_info['special_effect'] == 'snake':
            return (0.2, 0.2, 0.8)  # Blue for snake
        else:
            return (0.7, 0.7, 0.7)  # Default light gray

    def _render_2d(self, screen) -> None:
        """Render board in 2D using pygame."""
        try:
            import pygame
            # Draw a simple grid representation of the board
            cell_size = 30
            offset_x = 50
            offset_y = 50
            
            # Draw positions as colored rectangles
            for pos_id, pos_info in self.positions.items():
                track = pos_info['track']
                index = pos_info['index']
                coords = pos_info['coordinates']
                
                # Map track and index to screen position
                x = offset_x + (index * cell_size) + (track * 15)
                y = offset_y + (track * cell_size)
                
                # Get color based on position type
                color = self._get_position_color(pos_info)
                color_int = tuple(int(c * 255) for c in color)
                
                # Draw rectangle for position
                pygame.draw.rect(screen, color_int, (x, y, cell_size - 2, cell_size - 2))
                
        except Exception as e:
            print(f"Error in 2D board rendering: {e}")