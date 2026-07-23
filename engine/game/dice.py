"""
Dice system for 3D Ludo.
This module handles dice rolling, probabilities, and special dice effects.
"""

import random
import time
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
class DiceType(Enum):
    CLASSIC = "classic"
    POWER = "power"
    LUCKY = "lucky"
    MAGIC = "magic"
class SpecialDie:
    """Represents a special die with unique properties."""

    def __init__(self, die_type: str, value: Any, effect: Optional[Dict[str, Any]] = None):
        """
        Initialize a special die.

        Args:
            die_type: Type of special die
            value: Base value or description
            effect: Optional effect when die is rolled
        """
        self.die_type = die_type
        self.value = value
        self.effect = effect
        self.is_active = True

    def roll(self) -> Any:
        """
        Roll the special die.

        Returns:
            Rolled value with effect applied if any
        """
        result = self.value

        if self.effect:
            result = self._apply_effect(result)

        return result

    def _apply_effect(self, value: Any) -> Any:
        """
        Apply the die's effect to the rolled value.

        Args:
            value: Original value

        Returns:
            Value with effect applied
        """
        effect_type = self.effect.get('type')

        if effect_type == 'add_bonus':
            return value + self.effect.get('amount', 0)
        elif effect_type == 'multiply':
            return value * self.effect.get('multiplier', 1)
        elif effect_type == 'random_range':
            min_val = self.effect.get('min', 0)
            max_val = self.effect.get('max', 6)
            return random.randint(min_val, max_val)
        elif effect_type == 'swap':
            return self.effect.get('swap_value', value)
        else:
            return value

    def is_exceptional(self) -> bool:
        """
        Check if this die is considered exceptional (e.g., 6 in classic dice).

        Returns:
            True if die is exceptional, False otherwise
        """
        if isinstance(self.value, (int, float)):
            return self.value == 6
        return False
class Dice:
    """
    Dice system for 3D Ludo.
    Manages dice rolling, probabilities, and special dice effects.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the dice system with configuration.

        Args:
            config: Dice configuration dictionary
        """
        self.config = config
        self.dice_type = DiceType(config.get('type', 'classic'))
        self.num_dice = config.get('num_dice', 1)
        self.last_roll: List[Any] = []
        self.roll_history: List[List[Any]] = []
        self.roll_times: List[float] = []

        # Special dice
        self.special_dice: List[SpecialDie] = []
        self.setup_special_dice(config.get('special_dice', []))

        # Statistics
        self.roll_count = 0
        self.total_sum = 0
        self.average_roll = 0.0
        self.most_common_roll = None
        self.distribution: Dict[Any, int] = {}

    def setup_special_dice(self, special_config: List[Dict[str, Any]]) -> None:
        """
        Setup special dice based on configuration.

        Args:
            special_config: List of special dice configurations
        """
        self.special_dice.clear()

        for die_config in special_config:
            die = SpecialDie(
                die_type=die_config['type'],
                value=die_config.get('value'),
                effect=die_config.get('effect')
            )
            self.special_dice.append(die)

    def roll(self) -> List[Any]:
        """
        Roll all dice.

        Returns:
            List of rolled values
        """
        self.last_roll = []
        roll_time = time.time()

        # Roll regular dice
        for _ in range(self.num_dice):
            value = self._roll_single_die()
            self.last_roll.append(value)

        # Roll special dice
        for die in self.special_dice:
            if die.is_active:
                value = die.roll()
                self.last_roll.append(value)

        # Update statistics
        self.roll_count += 1
        self.roll_times.append(roll_time)
        self.roll_history.append(self.last_roll.copy())

        # Calculate total and average
        numeric_values = [v for v in self.last_roll if isinstance(v, (int, float))]
        if numeric_values:
            self.total_sum += sum(numeric_values)
            self.average_roll = self.total_sum / (self.roll_count * self.num_dice)

            # Update distribution
            for value in numeric_values:
                self.distribution[value] = self.distribution.get(value, 0) + 1

            # Find most common roll
            self.most_common_roll = max(self.distribution.items(), key=lambda x: x[1])[0]

        return self.last_roll

    def _roll_single_die(self) -> int:
        """
        Roll a single regular die.

        Returns:
            Rolled value (1-6 for classic dice)
        """
        if self.dice_type == DiceType.CLASSIC:
            return random.randint(1, 6)
        elif self.dice_type == DiceType.POWER:
            # Weighted towards higher numbers
            weights = [1, 2, 3, 4, 2, 1]  # 6 is most likely
            return random.choices([1, 2, 3, 4, 5, 6], weights=weights)[0]
        elif self.dice_type == DiceType.LUCKY:
            # Lucky die - higher chance of good numbers
            weights = [1, 2, 3, 4, 2, 3]  # Slightly favor 6
            return random.choices([1, 2, 3, 4, 5, 6], weights=weights)[0]
        elif self.dice_type == DiceType.MAGIC:
            # Magic die - can be anything
            return random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        else:
            return random.randint(1, 6)

    def get_roll_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the last roll.

        Returns:
            Dictionary with roll summary
        """
        return {
            'last_roll': self.last_roll,
            'roll_count': self.roll_count,
            'average_roll': self.average_roll,
            'most_common_roll': self.most_common_roll,
            'distribution': self.distribution.copy(),
            'total_sum': self.total_sum,
            'is_exceptional': any(die.is_exceptional() for die in self.special_dice if die.is_active)
        }

    def get_dice_info(self) -> Dict[str, Any]:
        """
        Get information about all dice.

        Returns:
            Dictionary with dice information
        """
        return {
            'dice_type': self.dice_type.value,
            'num_dice': self.num_dice,
            'special_dice': [
                {
                    'type': die.die_type,
                    'value': die.value,
                    'effect': die.effect,
                    'is_active': die.is_active
                }
                for die in self.special_dice
            ]
        }

    def activate_special_die(self, die_index: int) -> bool:
        """
        Activate a special die.

        Args:
            die_index: Index of special die to activate

        Returns:
            True if activated successfully, False otherwise
        """
        if 0 <= die_index < len(self.special_dice):
            self.special_dice[die_index].is_active = True
            return True
        return False

    def deactivate_special_die(self, die_index: int) -> bool:
        """
        Deactivate a special die.

        Args:
            die_index: Index of special die to deactivate

        Returns:
            True if deactivated successfully, False otherwise
        """
        if 0 <= die_index < len(self.special_dice):
            self.special_dice[die_index].is_active = False
            return True
        return False

    def get_active_special_dice(self) -> List[SpecialDie]:
        """
        Get list of active special dice.

        Args:
            None

        Returns:
            List of active special dice
        """
        return [die for die in self.special_dice if die.is_active]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert dice system to dictionary for saving.

        Returns:
            Dictionary representation of dice
        """
        return {
            'dice_type': self.dice_type.value,
            'num_dice': self.num_dice,
            'last_roll': self.last_roll,
            'roll_history': self.roll_history,
            'roll_times': self.roll_times,
            'roll_count': self.roll_count,
            'total_sum': self.total_sum,
            'average_roll': self.average_roll,
            'most_common_roll': self.most_common_roll,
            'distribution': self.distribution,
            'special_dice': [
                {
                    'type': die.die_type,
                    'value': die.value,
                    'effect': die.effect,
                    'is_active': die.is_active
                }
                for die in self.special_dice
            ]
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load dice system from dictionary.

        Args:
            data: Dictionary representation of dice
        """
        self.dice_type = DiceType(data['dice_type'])
        self.num_dice = data['num_dice']
        self.last_roll = data['last_roll']
        self.roll_history = data['roll_history']
        self.roll_times = data['roll_times']
        self.roll_count = data['roll_count']
        self.total_sum = data['total_sum']
        self.average_roll = data['average_roll']
        self.most_common_roll = data['most_common_roll']
        self.distribution = data['distribution']

        # Recreate special dice
        self.special_dice.clear()
        for die_config in data['special_dice']:
            die = SpecialDie(
                die_type=die_config['type'],
                value=die_config['value'],
                effect=die_config['effect']
            )
            die.is_active = die_config['is_active']
            self.special_dice.append(die)