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
import time

#TODO: Need to implement our own motor class in lerobot.motors

from lerobot.teleoperators.config import TeleoperatorConfig
from lerobot.utils.errors import DeviceAlreadyConnectedError, DeviceNotConnectedError

#TODO: Figure out what is Teleoperator
from ..teleoperator import Teleoperator

from .config_earthrover_mini_plus_teleoperator import EarthroverMiniPlusConfig

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
        