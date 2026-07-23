"""
Game pieces/characters system for 3D Ludo.
This module handles character models, piece properties, and piece management.
"""

import json
import math
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

# OpenGL is optional for headless or testing environments.
try:
    from OpenGL.GL import *
except ImportError:
    GL_TEXTURE_2D = 0
    GL_QUADS = 0
    def glEnable(x):
        pass
    def glBegin(x):
        pass
    def glEnd():
        pass
    def glColor3f(r, g, b):
        pass
    def glNormal3f(x, y, z):
        pass
    def glTexCoord2f(u, v):
        pass
    def glVertex3f(x, y, z):
        pass

class PieceType(Enum):
    CLASSIC = "classic"
    WARRIOR = "warrior"
    WIZARD = "wizard"
    ARCHER = "archer"
    KING = "king"
    QUEEN = "queen"
class PieceColor(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
class MovementState(Enum):
    IDLE = "idle"
    MOVING = "moving"
    WONDERING = "wondering"
    CAPTURED = "captured"
@dataclass
class CharacterStats:
    """Character statistics for pieces."""
    attack: float = 1.0
    defense: float = 1.0
    speed: float = 1.0
    luck: float = 1.0
    charisma: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'attack': self.attack,
            'defense': self.defense,
            'speed': self.speed,
            'luck': self.luck,
            'charisma': self.charisma
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharacterStats':
        return cls(
            attack=data.get('attack', 1.0),
            defense=data.get('defense', 1.0),
            speed=data.get('speed', 1.0),
            luck=data.get('luck', 1.0),
            charisma=data.get('charisma', 1.0)
        )
class Pieces:
    """
    Game pieces/characters system.
    Manages piece models, properties, and piece-related operations.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the pieces system with configuration.

        Args:
            config: Pieces configuration dictionary
        """
        self.config = config
        self.pieces: Dict[int, 'Piece'] = {}  # Key: piece_id, Value: Piece object
        self.models: Dict[PieceType, Dict[str, Any]] = {}
        self.textures: Dict[PieceColor, Any] = {}
        self.piece_types = list(PieceType)
        self.colors = list(PieceColor)

        # Initialize piece models
        self._initialize_piece_models()

    def _initialize_piece_models(self) -> None:
        """Initialize default character models."""
        # Classic piece model (simple cube)
        self.models[PieceType.CLASSIC] = {
            'vertices': [
                (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
                (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)
            ],
            'normals': [],
            'uvs': [],
            'model': None  # Would be loaded from 3D file in real implementation
        }

        # Warrior piece model
        self.models[PieceType.WARRIOR] = {
            'vertices': self._generate_warrior_mesh(),
            'normals': [],
            'uvs': [],
            'model': None
        }

        # Wizard piece model
        self.models[PieceType.WIZARD] = {
            'vertices': self._generate_wizard_mesh(),
            'normals': [],
            'uvs': [],
            'model': None
        }

        # Archer piece model
        self.models[PieceType.ARCHER] = {
            'vertices': self._generate_archer_mesh(),
            'normals': [],
            'uvs': [],
            'model': None
        }

        # King piece model
        self.models[PieceType.KING] = {
            'vertices': self._generate_king_mesh(),
            'normals': [],
            'uvs': [],
            'model': None
        }

        # Queen piece model
        self.models[PieceType.QUEEN] = {
            'vertices': self._generate_queen_mesh(),
            'normals': [],
            'uvs': [],
            'model': None
        }

        # Generate textures for each color
        for color in self.colors:
            self.textures[color] = self._generate_piece_texture(color)

    def _generate_warrior_mesh(self) -> List[Tuple[float, float, float]]:
        """Generate a simple warrior character mesh."""
        vertices = []
        # Body
        body_height = 0.8
        body_width = 0.4
        body_depth = 0.3

        # Body box
        vertices.extend([
            (-body_width/2, 0, -body_depth/2), (body_width/2, 0, -body_depth/2),
            (body_width/2, body_height, -body_depth/2), (-body_width/2, body_height, -body_depth/2),
            (-body_width/2, 0, body_depth/2), (body_width/2, 0, body_depth/2),
            (body_width/2, body_height, body_depth/2), (-body_width/2, body_height, body_depth/2)
        ])

        # Head
        head_radius = 0.3
        head_height = 0.4
        vertices.extend(self._generate_sphere_head(-body_width/2, body_height + head_height/2, 0))

        return vertices

    def _generate_wizard_mesh(self) -> List[Tuple[float, float, float]]:
        """Generate a simple wizard character mesh."""
        vertices = []
        height = 1.0
        width = 0.4
        depth = 0.3

        # Body
        vertices.extend([
            (-width/2, 0, -depth/2), (width/2, 0, -depth/2),
            (width/2, height, -depth/2), (-width/2, height, -depth/2),
            (-width/2, 0, depth/2), (width/2, 0, depth/2),
            (width/2, height, depth/2), (-width/2, height, depth/2)
        ])

        # Hat
        hat_height = 0.5
        hat_radius = 0.6
        vertices.extend(self._generate_cylinder_hat(-width/2, height + hat_height/2, 0, hat_height, hat_radius))

        return vertices

    def _generate_archer_mesh(self) -> List[Tuple[float, float, float]]:
        """Generate a simple archer character mesh."""
        vertices = []
        height = 0.9
        width = 0.35
        depth = 0.25

        # Body
        vertices.extend([
            (-width/2, 0, -depth/2), (width/2, 0, -depth/2),
            (width/2, height, -depth/2), (-width/2, height, -depth/2),
            (-width/2, 0, depth/2), (width/2, 0, depth/2),
            (width/2, height, depth/2), (-width/2, height, depth/2)
        ])

        # Bow
        bow_length = 1.0
        bow_width = 0.1
        bow_height = 0.05
        bow_y_offset = height + 0.3
        vertices.extend(self._generate_bow(-width/2, bow_y_offset, 0))

        return vertices

    def _generate_king_mesh(self) -> List[Tuple[float, float, float]]:
        """Generate a simple king character mesh."""
        vertices = []
        height = 1.2
        width = 0.4
        depth = 0.35

        # Body
        vertices.extend([
            (-width/2, 0, -depth/2), (width/2, 0, -depth/2),
            (width/2, height, -depth/2), (-width/2, height, -depth/2),
            (-width/2, 0, depth/2), (width/2, 0, depth/2),
            (width/2, height, depth/2), (-width/2, height, depth/2)
        ])

        # Crown
        crown_height = 0.6
        crown_radius = 0.5
        vertices.extend(self._generate_crown(width/2, height + crown_height/2, 0))

        return vertices

    def _generate_queen_mesh(self) -> List[Tuple[float, float, float]]:
        """Generate a simple queen character mesh."""
        vertices = []
        height = 1.1
        width = 0.38
        depth = 0.32

        # Body
        vertices.extend([
            (-width/2, 0, -depth/2), (width/2, 0, -depth/2),
            (width/2, height, -depth/2), (-width/2, height, -depth/2),
            (-width/2, 0, depth/2), (width/2, 0, depth/2),
            (width/2, height, depth/2), (-width/2, height, depth/2)
        ])

        # Parasol (for queen's protection)
        parasol_radius = 0.8
        parasol_height = 0.5
        parasol_y_offset = height + 0.2
        vertices.extend(self._generate_parasol(width/2, parasol_y_offset, 0, parasol_radius, parasol_height))

        return vertices

    def _generate_sphere_head(self, x: float, y: float, z: float) -> List[Tuple[float, float, float]]:
        """Generate a sphere for head."""
        vertices = []
        radius = 0.3
        lat_steps = 8
        lon_steps = 8

        for lat in range(lat_steps + 1):
            theta = lat * math.pi / lat_steps
            sin_theta = math.sin(theta)
            cos_theta = math.cos(theta)

            for lon in range(lon_steps + 1):
                phi = lon * 2 * math.pi / lon_steps
                sin_phi = math.sin(phi)
                cos_phi = math.cos(phi)

                x_pos = x + radius * sin_theta * cos_phi
                y_pos = y + radius * cos_theta
                z_pos = z + radius * sin_theta * sin_phi

                vertices.append((x_pos, y_pos, z_pos))

        return vertices

    def _generate_cylinder_hat(self, x: float, y: float, z: float, height: float, radius: float) -> List[Tuple[float, float, float]]:
        """Generate a cylinder for wizard hat."""
        vertices = []
        steps = 8

        for i in range(steps + 1):
            angle = i * 2 * math.pi / steps
            x_pos = x + radius * math.cos(angle)
            z_pos = z + radius * math.sin(angle)
            vertices.append((x_pos, y, z_pos))

        return vertices

    def _generate_bow(self, x: float, y: float, z: float) -> List[Tuple[float, float, float]]:
        """Generate a bow for archer."""
        vertices = []
        bow_length = 0.8
        bow_thickness = 0.1
        bow_radius = 0.05

        # Left side of bow
        for i in range(10):
            t = i / 9
            x_pos = x + -bow_length * t
            z_pos = z + -bow_thickness * t
            y_pos = y + t * 0.2
            vertices.append((x_pos, y_pos, z_pos))

        # Right side of bow
        for i in range(10):
            t = i / 9
            x_pos = x + bow_length * t
            z_pos = z + -bow_thickness * t
            y_pos = y + t * 0.2
            vertices.append((x_pos, y_pos, z_pos))

        return vertices

    def _generate_crown(self, x: float, y: float, z: float) -> List[Tuple[float, float, float]]:
        """Generate a crown for king."""
        vertices = []
        num_points = 8
        base_radius = 0.6
        top_radius = 0.3

        for i in range(num_points):
            angle = i * 2 * math.pi / num_points
            t = i / num_points

            base_x = x + base_radius * math.cos(angle)
            base_z = z + base_radius * math.sin(angle)
            vertices.append((base_x, y, base_z))

            top_x = x + top_radius * math.cos(angle + math.pi / num_points)
            top_z = z + top_radius * math.sin(angle + math.pi / num_points)
            vertices.append((top_x, y + 0.4, top_z))

        return vertices

    def _generate_parasol(self, x: float, y: float, z: float, radius: float, height: float) -> List[Tuple[float, float, float]]:
        """Generate a parasol for queen."""
        vertices = []
        num_segments = 8
        height_segments = 4

        for seg in range(height_segments):
            seg_y = seg * height / height_segments
            seg_radius = radius * (1 - seg / height_segments)

            for i in range(num_segments):
                angle = i * 2 * math.pi / num_segments
                x_pos = x + seg_radius * math.cos(angle)
                z_pos = z + seg_radius * math.sin(angle)
                vertices.append((x_pos, y + seg_y, z_pos))

        return vertices

    def _generate_piece_texture(self, color: PieceColor) -> Any:
        """Generate a texture for a piece color."""
        # In a real implementation, this would create an OpenGL texture
        # For now, we'll just return a color representation
        texture_data = {
            'color': color.value,
            'pattern': None,  # Could be 'solid', 'striped', 'polka_dot', etc.
            'shininess': 32
        }
        return texture_data

    def create_piece(self, piece_id: int, piece_type: PieceType, color: PieceColor, player_id: int, stats: Optional[CharacterStats] = None) -> 'Piece':
        """
        Create a new game piece.

        Args:
            piece_id: Unique ID for the piece
            piece_type: Type of piece (character)
            color: Color of the piece
            player_id: ID of the player who owns this piece
            stats: Optional character statistics

        Returns:
            Created Piece object
        """
        if stats is None:
            stats = CharacterStats()

        piece = Piece(
            piece_id=piece_id,
            piece_type=piece_type,
            color=color,
            player_id=player_id,
            stats=stats,
            model=self.models[piece_type],
            texture=self.textures[color]
        )

        self.pieces[piece_id] = piece
        return piece

    def get_piece(self, piece_id: int) -> Optional['Piece']:
        """
        Get a piece by ID.

        Args:
            piece_id: ID of the piece to retrieve

        Returns:
            Piece object if found, None otherwise
        """
    def get_piece_by_id(self, piece_id: int) -> Optional['Piece']:
        """
        Get a piece by ID.

        Args:
            piece_id: ID of the piece to retrieve

        Returns:
            Piece object if found, None otherwise
        """
        return self.pieces.get(piece_id)

    def get_all_pieces(self) -> List['Piece']:
        """
        Get all pieces.

        Returns:
            List of all Piece objects
        """
        return list(self.pieces.values())

    def get_player_pieces(self, player_id: int) -> List['Piece']:
        """
        Get pieces belonging to a specific player.

        Args:
            player_id: ID of the player

        Returns:
            List of Piece objects belonging to the player
        """
        return [piece for piece in self.pieces.values() if piece.player_id == player_id]

    def get_opponent_pieces(self, player_id: int) -> List['Piece']:
        """
        Get pieces belonging to opponents of a player.

        Args:
            player_id: ID of the player

        Returns:
            List of Piece objects belonging to opponents
        """
        return [piece for piece in self.pieces.values() if piece.player_id != player_id]

    def capture_piece(self, piece: 'Piece') -> None:
        """
        Capture a piece (remove from play).

        Args:
            piece: The piece to capture
        """
        if piece.piece_id in self.pieces:
            piece.state = MovementState.CAPTURED
            # In a real implementation, this would also remove the piece from rendering

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert pieces system to dictionary for saving.

        Returns:
            Dictionary representation of pieces
        """
        return {
            'pieces': {str(piece_id): piece.to_dict() for piece_id, piece in self.pieces.items()}
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load pieces system from dictionary.

        Args:
            data: Dictionary representation of pieces
        """
        self.pieces.clear()

        for piece_id_str, piece_data in data['pieces'].items():
            piece_id = int(piece_id_str)
            piece = Piece.from_dict(piece_data)
            self.pieces[piece_id] = piece

    def render(self, screen) -> None:
        """
        Render all pieces to the screen.

        Args:
            screen: The rendering surface
        """
        for piece in self.pieces.values():
            if piece.state != MovementState.CAPTURED:
                self._render_piece(piece, screen)

    def _render_piece(self, piece: 'Piece', screen) -> None:
        """
        Render a single piece.

        Args:
            piece: The piece to render
            screen: The rendering surface
        """
        # Enable texturing
        glEnable(GL_TEXTURE_2D)

        # Use appropriate texture
        texture_id = self.textures[piece.color]

        # Draw the piece model
        self._draw_model(piece.model, screen)

        # Update piece animation
        piece.update_animation()

    def _draw_model(self, model: Dict[str, Any], screen) -> None:
        """
        Draw a 3D model.

        Args:
            model: Model data dictionary
            screen: The rendering surface
        """
        if model['model']:
            # Use pre-loaded 3D model
            model['model'].render()
        else:
            # Generate simple geometry from vertices
            glBegin(GL_QUADS)

            # Generate normals and UVs if not present
            if not model['normals']:
                # Generate simple normals (up)
                for _ in model['vertices']:
                    model['normals'].append((0, 1, 0))

            if not model['uvs']:
                # Generate simple UVs
                for _ in model['vertices']:
                    model['uvs'].append((0.5, 0.5))

            for i in range(0, len(model['vertices']), 4):
                if i + 3 < len(model['vertices']):
                    # Draw quad
                    for j in range(4):
                        idx = i + j
                        if idx < len(model['vertices']):
                            glNormal3f(*model['normals'][idx] if idx < len(model['normals']) else (0, 1, 0))
                            glTexCoord2f(*model['uvs'][idx] if idx < len(model['uvs']) else (0.5, 0.5))
                            glVertex3f(*model['vertices'][idx])

            glEnd()

    def update(self, delta_time: float) -> None:
        """
        Update all pieces based on elapsed time.

        Args:
            delta_time: Time elapsed since last update
        """
        for piece in self.pieces.values():
            piece.update(delta_time)
class Piece:
    """
    Individual game piece/character.
    Represents a single game piece with all its properties and behaviors.
    """

    def __init__(self, piece_id: int, piece_type: PieceType, color: PieceColor, player_id: int,
                 stats: CharacterStats, model: Dict[str, Any], texture: Dict[str, Any]):
        """
        Initialize a game piece.

        Args:
            piece_id: Unique ID for the piece
            piece_type: Type of piece (character)
            color: Color of the piece
            player_id: ID of the player who owns this piece
            stats: Character statistics
            model: 3D model data
            texture: Texture data
        """
        self.piece_id = piece_id
        self.piece_type = piece_type
        self.color = color
        self.player_id = player_id
        self.stats = stats
        self.model = model
        self.texture = texture

        # Position and movement
        self.position = 0  # Board position index
        self.target_position: Optional[int] = None
        self.is_selected = False
        self.is_moving = False
        self.state = MovementState.IDLE
        self.reached_end = False
        self.animation_progress = 0.0
        self.animation_speed = 1.0

        # Movement properties
        self.base_speed = 1.0
        self.luck_modifier = 0.0
        self.bonus_moves = 0
        self.captures_made = 0

        # Status effects
        self.status_effects: Dict[str, float] = {}
        self.is_protected = False

        # Animation
        self.animation_frame = 0
        self.animation_timer = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert piece to dictionary for saving.

        Returns:
            Dictionary representation of piece
        """
        return {
            'piece_id': self.piece_id,
            'piece_type': self.piece_type.value,
            'color': self.color.value,
            'player_id': self.player_id,
            'stats': self.stats.to_dict(),
            'position': self.position,
            'is_selected': self.is_selected,
            'is_moving': self.is_moving,
            'state': self.state.value,
            'reached_end': self.reached_end,
            'animation_progress': self.animation_progress,
            'base_speed': self.base_speed,
            'luck_modifier': self.luck_modifier,
            'bonus_moves': self.bonus_moves,
            'captures_made': self.captures_made,
            'status_effects': self.status_effects,
            'is_protected': self.is_protected,
            'animation_frame': self.animation_frame,
            'animation_timer': self.animation_timer
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Piece':
        """
        Create a piece from dictionary.

        Args:
            data: Dictionary representation of piece

        Returns:
            Created Piece object
        """
        piece = cls(
            piece_id=data['piece_id'],
            piece_type=PieceType(data['piece_type']),
            color=PieceColor(data['color']),
            player_id=data['player_id'],
            stats=CharacterStats.from_dict(data['stats']),
            model={},  # Would need to be restored from shared models
            texture={}  # Would need to be restored from shared textures
        )

        # Copy all other attributes
        piece.position = data['position']
        piece.is_selected = data['is_selected']
        piece.is_moving = data['is_moving']
        piece.state = MovementState(data['state'])
        piece.reached_end = data['reached_end']
        piece.animation_progress = data['animation_progress']
        piece.base_speed = data['base_speed']
        piece.luck_modifier = data['luck_modifier']
        piece.bonus_moves = data['bonus_moves']
        piece.captures_made = data['captures_made']
        piece.status_effects = data['status_effects']
        piece.is_protected = data['is_protected']
        piece.animation_frame = data['animation_frame']
        piece.animation_timer = data['animation_timer']

        return piece

    def can_move(self) -> bool:
        """
        Check if the piece can move.

        Returns:
            True if piece can move, False otherwise
        """
        return self.state == MovementState.IDLE and not self.is_moving and not self.reached_end

    def select(self) -> bool:
        """
        Select this piece.

        Returns:
            True if selected successfully, False otherwise
        """
        if self.can_move() and self.player_id == 0:  # Currently only player 0 can select for demo
            self.is_selected = True
            return True
        return False

    def deselect(self) -> None:
        """Deselect this piece."""
        self.is_selected = False

    def calculate_target_position(self, dice_roll: int) -> Optional[int]:
        """
        Calculate the target position based on dice roll.

        Args:
            dice_roll: Number rolled on dice (1-6)

        Returns:
            Target position index if valid, None otherwise
        """
        if not self.can_move():
            return None

        # Apply status effects
        effective_roll = dice_roll
        for effect, duration in self.status_effects.items():
            if effect == 'slowed':
                effective_roll = int(dice_roll * 0.5)
            elif effect == 'lucky':
                effective_roll = dice_roll + 2

        # Calculate new position
        target = self.position + effective_roll

        # Check if target exceeds board size
        # For now, we'll use a simple board size
        max_position = 60  # Classic Ludo board has 60 positions per track

        if target > max_position:
            # Can't move, stay in place
            return None

        # Check for special positions (safe zones, ladders, etc.)
        # This would be handled by the board system

        return target

    def move_to(self, position: int) -> None:
        """
        Move the piece to a specific position.

        Args:
            position: Target position index
        """
        if position < 0:
            return

        self.target_position = position
        self.is_moving = True
        self.state = MovementState.MOVING
        self.animation_progress = 0.0

    def update(self, delta_time: float) -> None:
        """
        Update piece animation and movement.

        Args:
            delta_time: Time elapsed since last update
        """
        if self.is_moving and self.target_position is not None:
            # Update animation
            self.animation_progress += delta_time * self.animation_speed * self.stats.speed

            # Update animation frame
            self.animation_timer += delta_time
            if self.animation_timer >= 0.2:  # Animation every 0.2 seconds
                self.animation_frame = (self.animation_frame + 1) % 4
                self.animation_timer = 0

            # Check if animation is complete
            if self.animation_progress >= 1.0:
                # Complete movement
                old_position = self.position
                self.position = self.target_position
                self.is_moving = False
                self.target_position = None
                self.is_selected = False

                # Check if piece reached the end path
                if self.position >= 52:  # Classic Ludo exit position
                    self.reached_end = True

                # Apply status effects
                self._update_status_effects(delta_time)

    def update_animation(self) -> None:
        """Update animation state."""
        self.animation_frame = (self.animation_frame + 1) % 4

    def _update_status_effects(self, delta_time: float) -> None:
        """
        Update status effects.

        Args:
            delta_time: Time elapsed since last update
        """
        # Decrease duration of status effects
        effects_to_remove = []
        for effect, duration in self.status_effects.items():
            duration -= delta_time
            if duration <= 0:
                effects_to_remove.append(effect)
            else:
                self.status_effects[effect] = duration

        # Remove expired effects
        for effect in effects_to_remove:
            del self.status_effects[effect]

    def apply_status_effect(self, effect: str, duration: float) -> None:
        """
        Apply a status effect to the piece.

        Args:
            effect: Effect name (e.g., 'slowed', 'lucky', 'protected')
            duration: Duration in seconds
        """
        self.status_effects[effect] = duration

    def add_bonus_move(self, count: int = 1) -> None:
        """
        Add bonus moves to the piece.

        Args:
            count: Number of bonus moves to add
        """
        self.bonus_moves += count

    def use_bonus_move(self) -> bool:
        """
        Use a bonus move.

        Returns:
            True if bonus move was used, False if no bonus moves available
        """
        if self.bonus_moves > 0:
            self.bonus_moves -= 1
            return True
        return False

    def increment_captures(self) -> None:
        """Increment capture count."""
        self.captures_made += 1

    def update_luck_modifier(self, modifier: float) -> None:
        """
        Update luck modifier.

        Args:
            modifier: Luck modifier value
        """
        self.luck_modifier = modifier