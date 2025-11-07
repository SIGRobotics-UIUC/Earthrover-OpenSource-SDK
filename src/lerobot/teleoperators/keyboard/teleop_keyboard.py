#!/usr/bin/env python

# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import sys
import time
from queue import Queue
from typing import Any

from lerobot.utils.errors import DeviceAlreadyConnectedError, DeviceNotConnectedError

from ..teleoperator import Teleoperator
from ..utils import TeleopEvents
from .configuration_keyboard import KeyboardEndEffectorTeleopConfig, KeyboardTeleopConfig

PYNPUT_AVAILABLE = True
try:
    if ("DISPLAY" not in os.environ) and ("linux" in sys.platform):
        logging.info("No DISPLAY set. Skipping pynput import.")
        raise ImportError("pynput blocked intentionally due to no display.")

    from pynput import keyboard
except ImportError:
    keyboard = None
    PYNPUT_AVAILABLE = False
except Exception as e:
    keyboard = None
    PYNPUT_AVAILABLE = False
    logging.info(f"Could not import pynput: {e}")


class KeyboardTeleop(Teleoperator):
    """
    Teleop class to use keyboard inputs for control.
    """

    config_class = KeyboardTeleopConfig
    name = "keyboard"

    def __init__(self, config: KeyboardTeleopConfig):
        super().__init__(config)
        self.config = config
        self.robot_type = config.type

        self.event_queue = Queue()
        self.current_pressed = {}
        self.listener = None
        self.logs = {}

    @property
    def action_features(self) -> dict:
        return {
            "dtype": "float32",
            "shape": (len(self.arm),),
            "names": {"motors": list(self.arm.motors)},
        }

    @property
    def feedback_features(self) -> dict:
        return {}

    @property
    def is_connected(self) -> bool:
        return PYNPUT_AVAILABLE and isinstance(self.listener, keyboard.Listener) and self.listener.is_alive()

    @property
    def is_calibrated(self) -> bool:
        pass

    def connect(self) -> None:
        if self.is_connected:
            raise DeviceAlreadyConnectedError(
                "Keyboard is already connected. Do not run `robot.connect()` twice."
            )

        if PYNPUT_AVAILABLE:
            logging.info("pynput is available - enabling local keyboard listener.")
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release,
            )
            self.listener.start()
        else:
            logging.info("pynput not available - skipping local keyboard listener.")
            self.listener = None

    def calibrate(self) -> None:
        pass

    def _on_press(self, key):
        if hasattr(key, "char"):
            self.event_queue.put((key.char, True))

    def _on_release(self, key):
        if hasattr(key, "char"):
            self.event_queue.put((key.char, False))
        if key == keyboard.Key.esc:
            logging.info("ESC pressed, disconnecting.")
            self.disconnect()

    def _drain_pressed_keys(self):
        while not self.event_queue.empty():
            key_char, is_pressed = self.event_queue.get_nowait()
            self.current_pressed[key_char] = is_pressed

    def configure(self):
        pass

    def get_action(self) -> dict[str, Any]:
        before_read_t = time.perf_counter()

        if not self.is_connected:
            raise DeviceNotConnectedError(
                "KeyboardTeleop is not connected. You need to run `connect()` before `get_action()`."
            )

        self._drain_pressed_keys()

        # Generate action based on current key states
        action = {key for key, val in self.current_pressed.items() if val}
        self.logs["read_pos_dt_s"] = time.perf_counter() - before_read_t

        return dict.fromkeys(action, None)

    def send_feedback(self, feedback: dict[str, Any]) -> None:
        pass

    def disconnect(self) -> None:
        if not self.is_connected:
            raise DeviceNotConnectedError(
                "KeyboardTeleop is not connected. You need to run `robot.connect()` before `disconnect()`."
            )
        if self.listener is not None:
            self.listener.stop()


class KeyboardEndEffectorTeleop(KeyboardTeleop):
    """
    Teleop class to use keyboard inputs for end effector control.
    Designed to be used with the `So100FollowerEndEffector` robot.
    """

    config_class = KeyboardEndEffectorTeleopConfig
    name = "keyboard_ee"

    def __init__(self, config: KeyboardEndEffectorTeleopConfig):
        super().__init__(config)
        self.config = config
        self.misc_keys_queue = Queue()

    @property
    def action_features(self) -> dict:
        if self.config.use_gripper:
            return {
                "dtype": "float32",
                "shape": (4,),
                "names": {"delta_x": 0, "delta_y": 1, "delta_z": 2, "gripper": 3},
            }
        else:
            return {
                "dtype": "float32",
                "shape": (3,),
                "names": {"delta_x": 0, "delta_y": 1, "delta_z": 2},
            }

    def get_action(self) -> dict[str, Any]:
        if not self.is_connected:
            raise DeviceNotConnectedError(
                "KeyboardTeleop is not connected. You need to run `connect()` before `get_action()`."
            )

        self._drain_pressed_keys()
        delta_x = 0.0
        delta_y = 0.0
        delta_z = 0.0
        gripper_action = 1.0

        # Generate action based on current key states
        for key, val in self.current_pressed.items():
            if key == keyboard.Key.up:
                delta_y = -int(val)
            elif key == keyboard.Key.down:
                delta_y = int(val)
            elif key == keyboard.Key.left:
                delta_x = int(val)
            elif key == keyboard.Key.right:
                delta_x = -int(val)
            elif key == keyboard.Key.shift:
                delta_z = -int(val)
            elif key == keyboard.Key.shift_r:
                delta_z = int(val)
            elif key == keyboard.Key.ctrl_r:
                # Gripper actions are expected to be between 0 (close), 1 (stay), 2 (open)
                gripper_action = int(val) + 1
            elif key == keyboard.Key.ctrl_l:
                gripper_action = int(val) - 1
            elif val:
                # If the key is pressed, add it to the misc_keys_queue
                # this will record key presses that are not part of the delta_x, delta_y, delta_z
                # this is useful for retrieving other events like interventions for RL, episode success, etc.
                self.misc_keys_queue.put(key)

        self.current_pressed.clear()

        action_dict = {
            "delta_x": delta_x,
            "delta_y": delta_y,
            "delta_z": delta_z,
        }

        if self.config.use_gripper:
            action_dict["gripper"] = gripper_action

        return action_dict

    def get_teleop_events(self) -> dict[str, Any]:
        """
        Get extra control events from the keyboard such as intervention status,
        episode termination, success indicators, etc.

        Keyboard mappings:
        - Any movement keys pressed = intervention active
        - 's' key = success (terminate episode successfully)
        - 'r' key = rerecord episode (terminate and rerecord)
        - 'q' key = quit episode (terminate without success)

        Returns:
            Dictionary containing:
                - is_intervention: bool - Whether human is currently intervening
                - terminate_episode: bool - Whether to terminate the current episode
                - success: bool - Whether the episode was successful
                - rerecord_episode: bool - Whether to rerecord the episode
        """
        if not self.is_connected:
            return {
                TeleopEvents.IS_INTERVENTION: False,
                TeleopEvents.TERMINATE_EPISODE: False,
                TeleopEvents.SUCCESS: False,
                TeleopEvents.RERECORD_EPISODE: False,
            }

        # Check if any movement keys are currently pressed (indicates intervention)
        movement_keys = [
            keyboard.Key.up,
            keyboard.Key.down,
            keyboard.Key.left,
            keyboard.Key.right,
            keyboard.Key.shift,
            keyboard.Key.shift_r,
            keyboard.Key.ctrl_r,
            keyboard.Key.ctrl_l,
        ]
        is_intervention = any(self.current_pressed.get(key, False) for key in movement_keys)

        # Check for episode control commands from misc_keys_queue
        terminate_episode = False
        success = False
        rerecord_episode = False

        # Process any pending misc keys
        while not self.misc_keys_queue.empty():
            key = self.misc_keys_queue.get_nowait()
            if key == "s":
                success = True
            elif key == "r":
                terminate_episode = True
                rerecord_episode = True
            elif key == "q":
                terminate_episode = True
                success = False

        return {
            TeleopEvents.IS_INTERVENTION: is_intervention,
            TeleopEvents.TERMINATE_EPISODE: terminate_episode,
            TeleopEvents.SUCCESS: success,
            TeleopEvents.RERECORD_EPISODE: rerecord_episode,
        }
    

        
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
                print(f" Forward Linear velocity: {self.linear_velocity}")
            elif key == 's':  # Backward
                self.linear_velocity = max(
                    self.linear_velocity - self.linear_step, 
                    self.min_linear_velocity
                )
                print(f"Backward Linear velocity: {self.linear_velocity}")
            elif key == 'a':  # Turn left
                self.angular_velocity = min(
                    self.angular_velocity + self.angular_step, 
                    self.max_angular_velocity
                )
                print(f" Left Angular velocity: {self.angular_velocity}")
            elif key == 'd':  # Turn right
                self.angular_velocity = max(
                    self.angular_velocity - self.angular_step, 
                    self.min_angular_velocity
                )
                print(f"Right! Angular velocity: {self.angular_velocity}")
            
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
                print(f" Speed multiplier: {self.speed_multiplier:.1f}x")
            
            # Stop
            elif key == 'x' or key == ' ':
                self.linear_velocity = 0.0
                self.angular_velocity = 0.0
                print(" STOP! All velocities zeroed")
            
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