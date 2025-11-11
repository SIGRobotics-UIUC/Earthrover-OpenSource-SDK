        
import logging
import os
import sys
import time
from queue import Queue
from typing import Any

from lerobot.utils.errors import DeviceAlreadyConnectedError, DeviceNotConnectedError

from lerobot.teleoperators.teleoperator import Teleoperator
from lerobot.teleoperators.utils import TeleopEvents
from lerobot.teleoperators.keyboard.configuration_keyboard import KeyboardEndEffectorTeleopConfig, KeyboardTeleopConfig
from lerobot.teleoperators.keyboard import KeyboardTeleop

class KeyboardRoverTeleop(KeyboardTeleop):
    """
    Teleop class to use keyboard inputs for rover control.
    Designed to be used with the `EarthRoverMiniPlus` robot.
    
    Controls (WASD-style):
    - w/s: Forward/Backward linear velocity
    - a/d: Turn left/right (angular velocity)
    - t/g: Increase/Decrease speed multiplier
    - Space/x: Stop (zero all velocities)
    - r: Reset to default values
    - q: Quit/terminate episode
    """

    name = "keyboard_rover"

    def __init__(self, config: KeyboardTeleopConfig):
        super().__init__(config)
        self.config = config
        self.misc_keys_queue = Queue()
        
        # Movement parameters
        self.linear_velocity = 0.0
        self.angular_velocity = 0.0
        
        # Control parameters
        self.linear_step = 10  # Linear velocity increment
        self.angular_step = 10  # Angular velocity increment
        self.speed_multiplier = 1.0
        self.speed_step = 0.1
        
        # Limits
        self.max_linear_velocity = 100
        self.min_linear_velocity = -100
        self.max_angular_velocity = 100
        self.min_angular_velocity = -100
        self.max_speed_multiplier = 2.0
        self.min_speed_multiplier = 0.1

    @property
    def action_features(self) -> dict:
        return {
            "dtype": "float32",
            "shape": (2,),
            "names": {"linear_velocity": 0, "angular_velocity": 1},
        }

    def get_action(self) -> dict[str, Any]:
        """
        Get the current action based on keyboard state.
        The velocities persist until changed or stopped.
        
        Returns:
            Dictionary containing:
                - linear_velocity: Forward/backward speed
                - angular_velocity: Turning speed
        """
        before_read_t = time.perf_counter()
        
        if not self.is_connected:
            raise DeviceNotConnectedError(
                "KeyboardRoverTeleop is not connected. You need to run `connect()` before `get_action()`."
            )

        self._drain_pressed_keys()
        
        # Process keyboard inputs - only act on key presses (True), not releases
        keys_to_process = [(k, v) for k, v in self.current_pressed.items() if v]
        
        for key, is_pressed in self.current_pressed.items():
            # Skip key releases
            if not is_pressed:
                continue
            
            # WASD movement controls
            if key == 'w':  # Forward
                self.linear_velocity = min(
                    self.linear_velocity + self.linear_step, 
                    self.max_linear_velocity
                )
                print(f"📈 Forward! Linear velocity: {self.linear_velocity}")
            elif key == 's':  # Backward
                self.linear_velocity = max(
                    self.linear_velocity - self.linear_step, 
                    self.min_linear_velocity
                )
                print(f"📉 Backward! Linear velocity: {self.linear_velocity}")
            elif key == 'a':  # Turn left
                self.angular_velocity = min(
                    self.angular_velocity + self.angular_step, 
                    self.max_angular_velocity
                )
                print(f"↪️  Left! Angular velocity: {self.angular_velocity}")
            elif key == 'd':  # Turn right
                self.angular_velocity = max(
                    self.angular_velocity - self.angular_step, 
                    self.min_angular_velocity
                )
                print(f"↩️  Right! Angular velocity: {self.angular_velocity}")
            
            # Speed multiplier (t/g for turbo/gear down)
            elif key == 't':
                self.speed_multiplier = min(
                    self.speed_multiplier + self.speed_step, 
                    self.max_speed_multiplier
                )
                print(f"⚡ Speed multiplier: {self.speed_multiplier:.1f}x")
            elif key == 'g':
                self.speed_multiplier = max(
                    self.speed_multiplier - self.speed_step, 
                    self.min_speed_multiplier
                )
                print(f"🐌 Speed multiplier: {self.speed_multiplier:.1f}x")
            
            # Stop
            elif key == 'x' or key == ' ':
                self.linear_velocity = 0.0
                self.angular_velocity = 0.0
                print("🛑 STOP! All velocities zeroed")
            
            # Reset to defaults
            elif key == 'r':
                self.linear_velocity = 0.0
                self.angular_velocity = 0.0
                self.speed_multiplier = 1.0
                print("🔄 Reset to defaults")
            
            # Misc keys for events
            elif key in ['q', 'h']:
                self.misc_keys_queue.put(key)
        
        # Clear processed keys
        self.current_pressed.clear()
        
        # Apply speed multiplier
        effective_linear = self.linear_velocity * self.speed_multiplier
        effective_angular = self.angular_velocity * self.speed_multiplier
        
        self.logs["read_pos_dt_s"] = time.perf_counter() - before_read_t
        
        return {
            "linear_velocity": effective_linear,
            "angular_velocity": effective_angular,
        }

    def get_teleop_events(self) -> dict[str, Any]:
        """
        Get extra control events from the keyboard.
        
        Keyboard mappings:
        - Any movement keys pressed = intervention active
        - 'h': Request help/show controls
        - 'q': Quit episode (terminate)
        
        Returns:
            Dictionary containing:
                - is_intervention: bool - Whether human is currently intervening
                - terminate_episode: bool - Whether to terminate the current episode
                - show_help: bool - Whether to show help message
        """
        if not self.is_connected:
            return {
                TeleopEvents.IS_INTERVENTION: False,
                TeleopEvents.TERMINATE_EPISODE: False,
                "show_help": False,
            }
        
        # Check if any movement keys are currently pressed (indicates intervention)
        movement_keys = [
            keyboard.Key.up,
            keyboard.Key.down,
            keyboard.Key.left,
            keyboard.Key.right,
        ]
        is_intervention = any(self.current_pressed.get(key, False) for key in movement_keys)
        
        # Check for episode control commands from misc_keys_queue
        terminate_episode = False
        show_help = False
        
        # Process any pending misc keys
        while not self.misc_keys_queue.empty():
            key = self.misc_keys_queue.get_nowait()
            if key == 'q':
                terminate_episode = True
            elif key == 'h':
                show_help = True
        
        return {
            TeleopEvents.IS_INTERVENTION: is_intervention,
            TeleopEvents.TERMINATE_EPISODE: terminate_episode,
            "show_help": show_help,
        }

    def print_controls(self):
        """Print the control scheme to console."""
        controls = """
        ═══════════════════════════════════════════════════════
        EarthRover Mini Plus - Keyboard Controls
        ═══════════════════════════════════════════════════════
        Movement:
          ↑ / ↓     : Increase/Decrease forward speed
          ← / →     : Turn left/right
          Space     : Stop (zero all velocities)
          
        Parameters:
          w / s     : Increase/Decrease speed multiplier
          r         : Reset all values to defaults
          
        Control:
          h         : Show this help message
          q         : Quit/terminate episode
          ESC       : Disconnect
        ═══════════════════════════════════════════════════════
        Current Values:
          Linear Velocity  : {:.1f}
          Angular Velocity : {:.1f}
          Speed Multiplier : {:.1f}x
          Effective Linear : {:.1f}
          Effective Angular: {:.1f}
        ═══════════════════════════════════════════════════════
        """.format(
            self.linear_velocity,
            self.angular_velocity,
            self.speed_multiplier,
            self.linear_velocity * self.speed_multiplier,
            self.angular_velocity * self.speed_multiplier
        )
        print(controls)

    def get_status(self) -> dict[str, Any]:
        """Get current status of the teleop controller."""
        return {
            "linear_velocity": self.linear_velocity,
            "angular_velocity": self.angular_velocity,
            "speed_multiplier": self.speed_multiplier,
            "effective_linear": self.linear_velocity * self.speed_multiplier,
            "effective_angular": self.angular_velocity * self.speed_multiplier,
        }