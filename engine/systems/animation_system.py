"""
Animation system for 3D Ludo (migrated into engine.systems).

This module is a copy of `core/animation_system.py` and serves as the
migration target for the animation system.
"""

import time
import math
import threading
from typing import List, Dict, Any, Optional, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, field
class AnimationType(Enum):
    MOVEMENT = "movement"
    LADDER_CLIMB = "ladder_climb"
    SNAKE_BITE = "snake_bite"
    CAPTURE = "capture"
    WIN = "win"
    SPELL_CAST = "spell_cast"
    SPECIAL_EFFECT = "special_effect"
class AnimationPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
@dataclass
class AnimationEffect:
    """Animation effect parameters."""

    effect_type: str
    duration: float
    start_time: float
    start_value: float
    end_value: float
    easing_type: str = "linear"
    on_complete: Optional[Callable[[], None]] = None
    loops: int = 1
    current_loop: int = 0
    is_active: bool = True

    def update(self, delta_time: float) -> bool:
        if not self.is_active:
            return False

        self.start_time += delta_time

        if self.start_time >= self.duration:
            if self.loops == -1 or self.current_loop < self.loops - 1:
                self.start_time = 0
                self.current_loop += 1
                return True
            else:
                self.is_active = False
                if self.on_complete:
                    self.on_complete()
                return False

        return True

    def get_current_value(self) -> float:
        if self.duration == 0:
            return self.end_value

        elapsed = min(self.start_time, self.duration)
        progress = elapsed / self.duration

        if self.easing_type == "linear":
            eased_progress = progress
        elif self.easing_type == "ease_in":
            eased_progress = progress * progress
        elif self.easing_type == "ease_out":
            eased_progress = 1 - (1 - progress) * (1 - progress)
        elif self.easing_type == "ease_in_out":
            if progress < 0.5:
                eased_progress = 2 * progress * progress
            else:
                eased_progress = 1 - 2 * (1 - progress) * (1 - progress)
        else:
            eased_progress = progress

        return self.start_value + (self.end_value - self.start_value) * eased_progress

    def reset(self) -> None:
        self.start_time = 0
        self.current_loop = 0
        self.is_active = True
@dataclass
class Animation:
    """Animation for a piece or effect."""

    animation_id: str
    animation_type: AnimationType
    target_piece_id: Optional[int]
    duration: float
    start_time: float
    is_looping: bool = False
    is_playing: bool = True
    priority: AnimationPriority = AnimationPriority.NORMAL
    effects: List[AnimationEffect] = field(default_factory=list)
    position_offsets: List[Tuple[float, float, float]] = field(default_factory=list)
    scale_factors: List[float] = field(default_factory=list)
    rotation_angles: List[float] = field(default_factory=list)
    color_changes: List[Tuple[float, float, float, float]] = field(default_factory=list)

    def update(self, delta_time: float) -> bool:
        if not self.is_playing:
            return False

        effects_to_remove = []
        for effect in self.effects:
            if not effect.update(delta_time):
                effects_to_remove.append(effect)

        for effect in effects_to_remove:
            self.effects.remove(effect)

        if not self.effects and not self.is_looping:
            self.is_playing = False
            return False

        if self.is_looping and not self.effects:
            self.is_playing = False
            return False

        return True

    def add_effect(self, effect: AnimationEffect) -> None:
        self.effects.append(effect)

    def set_position_offset(self, start_pos: Tuple[float, float, float], end_pos: Tuple[float, float, float], duration: float) -> None:
        self.position_offsets.append({
            'start': start_pos,
            'end': end_pos,
            'duration': duration,
            'start_time': time.time()
        })

    def set_scale_factor(self, start_scale: float, end_scale: float, duration: float) -> None:
        self.scale_factors.append({
            'start': start_scale,
            'end': end_scale,
            'duration': duration,
            'start_time': time.time()
        })

    def get_current_position(self, start_pos: Tuple[float, float, float]) -> Tuple[float, float, float]:
        x, y, z = start_pos

        for offset in self.position_offsets:
            progress = min((time.time() - offset['start_time']) / offset['duration'], 1.0)
            if progress > 0:
                x += (offset['end'][0] - offset['start'][0]) * progress
                y += (offset['end'][1] - offset['start'][1]) * progress
                z += (offset['end'][2] - offset['start'][2]) * progress

        return (x, y, z)

    def get_current_scale(self, start_scale: float) -> float:
        scale = start_scale

        for scale_factor in self.scale_factors:
            progress = min((time.time() - scale_factor['start_time']) / scale_factor['duration'], 1.0)
            if progress > 0:
                scale += (scale_factor['end'] - scale_factor['start']) * progress

        return scale
class AnimationSystem:
    """
    Animation system for 3D Ludo.
    Handles piece animations, special effects, and visual effects.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_enabled = config.get('enabled', True)
        self.animation_speed = config.get('animation_speed', 1.0)
        self.particle_system_enabled = config.get('particle_system_enabled', True)
        self.particle_quality = config.get('particle_quality', 'medium')

        self.animations: Dict[str, Animation] = {}
        self.active_animations: List[Animation] = []
        self.animation_queue: List[Animation] = []

        self.special_effects: List[Dict[str, Any]] = []

        self.screen_shake: Dict[str, Any] = {'intensity': 0, 'duration': 0, 'start_time': 0}
        self.flash_effect: Dict[str, Any] = {'color': (1, 1, 1, 1), 'duration': 0, 'start_time': 0}

        self.max_animations = config.get('max_animations', 20)
        self.animation_cleanup_interval = config.get('animation_cleanup_interval', 5.0)
        self.last_cleanup_time = time.time()

        self.particles: List[Dict[str, Any]] = []

        self._setup_animation_presets()

    def _setup_animation_presets(self) -> None:
        self.presets = {
            'smooth_movement': {
                'easing': 'ease_in_out',
                'duration': 0.5
            },
            'quick_move': {
                'easing': 'linear',
                'duration': 0.2
            },
            'magical_movement': {
                'easing': 'ease_in',
                'duration': 1.0
            },
            'bounce_movement': {
                'easing': 'ease_out',
                'duration': 0.3
            }
        }

    def create_animation(self, animation_id: str, animation_type: AnimationType,
                        target_piece_id: Optional[int], duration: float,
                        preset: Optional[str] = None, priority: Optional[AnimationPriority] = None) -> Animation:
        if priority is None:
            priority = AnimationPriority.NORMAL

        animation = Animation(
            animation_id=animation_id,
            animation_type=animation_type,
            target_piece_id=target_piece_id,
            duration=duration,
            start_time=time.time(),
            priority=priority
        )

        if preset and preset in self.presets:
            preset_config = self.presets[preset]
            effect = AnimationEffect(
                effect_type='movement',
                duration=duration,
                start_time=0,
                start_value=0,
                end_value=1,
                easing_type=preset_config['easing']
            )
            animation.add_effect(effect)

        return animation

    def play_animation(self, animation: Animation) -> bool:
        if not self.is_enabled:
            return False

        if len(self.active_animations) >= self.max_animations:
            self.active_animations.sort(key=lambda a: a.priority.value)
            removed_count = 0

            while len(self.active_animations) >= self.max_animations and removed_count < 5:
                self.active_animations.pop(0)
                removed_count += 1

        self.animation_queue.append(animation)
        return True

    def animate_piece_movement(self, piece_id: int, target_position: Tuple[float, float, float],
                             preset: Optional[str] = None) -> str:
        animation_id = f"move_{piece_id}_{int(time.time() * 1000)}"

        animation = self.create_animation(
            animation_id=animation_id,
            animation_type=AnimationType.MOVEMENT,
            target_piece_id=piece_id,
            duration=0.5,
            preset=preset or 'smooth_movement'
        )

        start_pos = (0, 0, 0)
        animation.set_position_offset(start_pos, target_position, 0.5)

        self.play_animation(animation)

        return animation_id

    def animate_ladder_climb(self, piece_id: int) -> str:
        animation_id = f"ladder_{piece_id}_{int(time.time() * 1000)}"

        animation = self.create_animation(
            animation_id=animation_id,
            animation_type=AnimationType.LADDER_CLIMB,
            target_piece_id=piece_id,
            duration=1.0,
            preset='magical_movement'
        )

        self.play_animation(animation)

        self.play_sound_for_animation('ladder', piece_id)
        self.create_particles('ladder', piece_id)

        return animation_id

    def animate_snake_bite(self, piece_id: int) -> str:
        animation_id = f"snake_{piece_id}_{int(time.time() * 1000)}"

        animation = self.create_animation(
            animation_id=animation_id,
            animation_type=AnimationType.SNAKE_BITE,
            target_piece_id=piece_id,
            duration=0.8,
            preset='quick_move'
        )

        self.play_animation(animation)

        self.play_sound_for_animation('snake', piece_id)
        self.create_particles('snake', piece_id)

        return animation_id

    def animate_capture(self, piece_id: int) -> str:
        animation_id = f"capture_{piece_id}_{int(time.time() * 1000)}"

        animation = self.create_animation(
            animation_id=animation_id,
            animation_type=AnimationType.CAPTURE,
            target_piece_id=piece_id,
            duration=1.0,
            preset='bounce_movement'
        )

        self.play_animation(animation)

        self.play_sound_for_animation('capture', piece_id)
        self.create_particles('capture', piece_id)

        return animation_id

    def animate_win(self, player_id: int) -> str:
        animation_id = f"win_{player_id}_{int(time.time() * 1000)}"

        animation = self.create_animation(
            animation_id=animation_id,
            animation_type=AnimationType.WIN,
            target_piece_id=None,
            duration=2.0,
            preset='magical_movement'
        )

        self.play_animation(animation)

        self.play_sound_for_animation('win', player_id)
        self.create_particles('win', player_id)

        return animation_id

    def play_sound_for_animation(self, sound_type: str, piece_id: int) -> None:
        if self.config.get('debug', False):
            print(f"Playing sound '{sound_type}' for piece {piece_id}")

    def create_particles(self, particle_type: str, piece_id: int) -> None:
        if not self.particle_system_enabled:
            return

        num_particles = 10 if particle_type != 'win' else 50
        particle_data = {
            'type': particle_type,
            'position': (0, 0, 0),
            'velocity': (0, 0, 0),
            'size': 0.1,
            'life': 1.0,
            'max_life': 1.0,
            'color': self._get_particle_color(particle_type),
            'spawn_time': time.time()
        }

        self.particles.append(particle_data)

    def _get_particle_color(self, particle_type: str) -> Tuple[float, float, float]:
        colors = {
            'ladder': (0.2, 0.8, 0.2),
            'snake': (0.2, 0.2, 0.8),
            'capture': (0.8, 0.2, 0.2),
            'win': (0.8, 0.8, 0.2),
            'movement': (0.2, 0.2, 0.2)
        }

        return colors.get(particle_type, (1, 1, 1))

    def update(self, delta_time: float) -> None:
        if not self.is_enabled:
            return

        for animation in self.active_animations[:]:
            if not animation.update(delta_time):
                self.active_animations.remove(animation)

        for particle in self.particles[:]:
            particle['life'] -= delta_time / particle['max_life']
            if particle['life'] <= 0:
                self.particles.remove(particle)

        for effect in self.special_effects[:]:
            effect['duration'] -= delta_time
            if effect['duration'] <= 0:
                self.special_effects.remove(effect)

        if self.screen_shake['duration'] > 0:
            self.screen_shake['duration'] -= delta_time
            if self.screen_shake['duration'] <= 0:
                self.screen_shake['intensity'] = 0

        if self.flash_effect['duration'] > 0:
            self.flash_effect['duration'] -= delta_time

        current_time = time.time()
        if current_time - self.last_cleanup_time > self.animation_cleanup_interval:
            self._cleanup_animations()
            self.last_cleanup_time = current_time

    def _cleanup_animations(self) -> None:
        current_time = time.time()
        cleanup_time = 60.0

        self.active_animations = [
            anim for anim in self.active_animations
            if current_time - anim.start_time < cleanup_time
        ]

        self.particles = [
            particle for particle in self.particles
            if current_time - particle['spawn_time'] < 2.0
        ]

    def add_screen_shake(self, intensity: float, duration: float) -> None:
        self.screen_shake['intensity'] = intensity
        self.screen_shake['duration'] = duration
        self.screen_shake['start_time'] = time.time()

    def add_flash_effect(self, color: Tuple[float, float, float, float], duration: float) -> None:
        self.flash_effect['color'] = color
        self.flash_effect['duration'] = duration
        self.flash_effect['start_time'] = time.time()

    def get_active_animations(self) -> List[Dict[str, Any]]:
        return [
            {
                'id': anim.animation_id,
                'type': anim.animation_type.value,
                'target_piece_id': anim.target_piece_id,
                'duration': anim.duration,
                'start_time': anim.start_time,
                'is_looping': anim.is_looping,
                'is_playing': anim.is_playing
            }
            for anim in self.active_animations
        ]

    def render(self, screen) -> None:
        if self.config.get('debug', False):
            print(f"Rendering {len(self.active_animations)} animations")

    def cleanup(self) -> None:
        self.active_animations.clear()
        self.animation_queue.clear()
        self.animations.clear()
        self.particles.clear()
        self.special_effects.clear()
        self.screen_shake = {'intensity': 0, 'duration': 0, 'start_time': 0}
        self.flash_effect = {'color': (1, 1, 1, 1), 'duration': 0, 'start_time': 0}

    def to_dict(self) -> Dict[str, Any]:
        return {
            'is_enabled': self.is_enabled,
            'animation_speed': self.animation_speed,
            'particle_system_enabled': self.particle_system_enabled,
            'particle_quality': self.particle_quality,
            'active_animations_count': len(self.active_animations),
            'special_effects_count': len(self.special_effects),
            'particles_count': len(self.particles),
            'screen_shake': self.screen_shake,
            'flash_effect': self.flash_effect
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        self.is_enabled = data['is_enabled']
        self.animation_speed = data['animation_speed']
        self.particle_system_enabled = data['particle_system_enabled']
        self.particle_quality = data['particle_quality']
