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


#TODO: Need to implement our own motor class in lerobot.motors

from lerobot.teleoperators.config import TeleoperatorConfig
from lerobot.utils.errors import DeviceAlreadyConnectedError, DeviceNotConnectedError

#TODO: Figure out what is Teleoperator
from ..teleoperator import Teleoperator
from ..utils import TeleopEvents
from keyboard.configuration_keyboard import KeyboardEndEffectorTeleopConfig, KeyboardTeleopConfig

from .config_earthrover_mini_plus_teleoperator import EarthroverMiniPlusConfig

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
        