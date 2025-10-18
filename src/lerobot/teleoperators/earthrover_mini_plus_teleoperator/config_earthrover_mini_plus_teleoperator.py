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

from dataclasses import dataclass #we are using this because this is a data holder class (since its a config file) where its main operation is just to store data, very minimal edits

from ..config import TeleoperatorConfig #goes back one folder to import a base config file that defines how any teleoperator configuration should behave


@TeleoperatorConfig.register_subclass("earthrover_mini_plus") #this allows you to register a different teleoperator and allows you to differentiate various teleoperators
@dataclass #works with the import statement as a decorator so it knows for this class to auto create an __init__.py and other boilerplate code
class EarthroverMiniPlusConfig(TeleoperatorConfig):
    # the variables below don't have any default value so need to pass one in
    port: str #Port to connect to the earthrover
    ip: str #Robot's IP to connect to the earthrover
    
    #TODO: Come up later on with what other parameters we need for the config file

@TeleoperatorConfig.register_subclass("earthrover_keyboard")
@dataclass
class KeyboardTeleopConfig(TeleoperatorConfig):
    #check if we want to state what keys we will capture/listen to
    mock: bool = False

# @TeleoperatorConfig.register_subclass("earthrover_keyboard_ee")
# @dataclass
# class KeyboardEndEffectorTeleopConfig(KeyboardTeleopConfig):
#     #this class specifically controls the end effector, commented out for now
#     use_gripper: bool = True
