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

import time
from typing import Any      
import warnings
import logging



import numpy as np
from lerobot.cameras.utils import make_cameras_from_configs
from lerobot.motors import Motor, MotorCalibration

from lerobot.utils.errors import DeviceAlreadyConnectedError, DeviceNotConnectedError

from ..robot import Robot
from .config_earthrover_mini_plus import EarthRoverMiniPlusConfig

logger = logging.get_logger(__name__)

class EarthRoverMiniPlus(Robot):

    config_class = EarthRoverMiniPlusConfig
    name = "earthrover_mini_plus"

    def __init__(self, config: EarthRoverMiniPlusConfig):
        super().__init__(config)

        self.config = config

        self.cameras = make_cameras_from_configs(config.cameras)

        self._last_command_time = time.time()
        self._command_timeout = 1.0  # seconds

        self._state = {
            "left_speed": 0.0,
            "right_speed": 0.0,
            # todo: anything else
        }

        # any motors or sensors
        # self.cameras = make_cameras_from_configs(config.cameras)

        logger.info(f"{self.name} initialized.")

    def configure(self) -> None:
        # set up motors and sensors
        logger.info(f"{self.name} configuring...")


    def get_observation(self) -> dict[str, Any]:
        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected")