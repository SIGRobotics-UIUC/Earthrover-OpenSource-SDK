#!/usr/bin/env python

# Copyright 2025 SIGRobotics team. All rights reserved.
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

from .config_earthrover_mini_plus_teleoperator import EarthroverMiniPlusConfig, EarthroverKeyboardTeleopConfig
from .earthrover_mini_plus_teleoperator import EarthroverMiniPlus, EarthroverKeyboardTeleop


#TODO: Need to implement our own motor class in lerobot.motors

from lerobot.teleoperators.config import TeleoperatorConfig
from lerobot.utils.errors import DeviceAlreadyConnectedError, DeviceNotConnectedError

#TODO: Figure out what is Teleoperator
from ..teleoperator import Teleoperator
from ..utils import TeleopEvents

PYNPUT_AVAILABLE = True #this is just a flag to see whether PYNPUT is able to be imported or not
try:
    if ("DISPLAY" not in os.environ) and ("linux" in sys.platform):
        logging.info("No DISPLAY set. Skipping pynput import.")
        raise ImportError("pynput blocked intentionally. This is because pynput utilizes a GUI and your OS global input system to function. However, you do not have a GUI (and thus are running a headless linux system).")
    
    from pynput import keyboard
except ImportError:
    keyboard = None
    PYNPUT_AVAILABLE = False
except Exception as e: #catches any other errors and displays them
    keyboard = None
    PYNPUT_AVAILABLE = False
    logging.info(f"Could not import pynput: {e}")

class EarthroverKeyboardTeleop(Teleoperator):
    """
    Teleop class to use keyboard inputs for control.
    """
    
    config_class = EarthroverKeyboardTeleopConfig
    name = "keyboard"

    def __init__(self, config: EarthroverKeyboardTeleopConfig): #prepares everything an object needs (runs automatically) such as the variables needed, config tells what kind of robot this is
        super().__init__(config) #this tells the parent class to do its setup first (calls the parent class's __init__ function [its constructor])
        self.config = config #saves the setting box into the object
        self.robot_type = config.type #saves the setting box type (what kind of robot) into the object

        self.event_queue = Queue() #creates a queue for key presses
        self.current_pressed = {} #creates a dictionary to track which keys are pressed down at any point in time
        self.listener = None #prepares what will actually listen for keyboard inputs
        self.logs = {} #sets up a dictionary to log all key presses

    @property #turns this function into a read-only function like a variable
    def action_features(self) -> dict:  #describing all properties of an action in an array; creating a blueprint/metadata
        return {
            "dtype": "float32", #data type of values in the action, like how motor positions are this data type
            "shape": (4,), #four arguments to pass in to move the robot (size of the array/how many values)
            "names": { #describing what each element represents
                "fields": ["sock", "duration", "speed", "angular"] #TODO: check if i need to set them to have default values later on
            },
        }



















logger = logging.getLogger(__name__)

class EarthroverMiniPlus(Teleoperator):
    """
    Earthrover Mini Plus designed by SIGRobotics and FrodoBots AI.
    """

    config_class = EarthroverMiniPlusConfig
    name = "earthrover_mini_plus"

    def __init__(self, config: EarthroverMiniPlusConfig):
        super().__init__(config)
        self.config = config
        