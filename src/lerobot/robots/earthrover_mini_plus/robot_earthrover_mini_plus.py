import logging
from socket import socket

from lerobot.utils.errors import DeviceAlreadyConnectedError, DeviceNotConnectedError

from lerobot.cameras.utils import make_cameras_from_configs

from ..robot import Robot
from .config_earthrover_mini_plus import EarthRoverMiniPlusConfig


# The import from our low-level API, so we can call actual functions on the robot
from api import api_structure


logger = logging.get_logger(__name__)

class EarthRoverMiniPlus(Robot):

    config_class = EarthRoverMiniPlusConfig
    name = "earthrover_mini_plus"

    def __init__(self, config: EarthRoverMiniPlusConfig):

        super().__init__(config)
        self.config = config

        self.base_motors = [] # todo
        self.cameras = make_cameras_from_configs(config.cameras)

    @cached_property
    def is_connected(self) -> bool:

        # When are we connected?
        # class api_structure:
        #     def __init__(self, ip, port=5500):
        #         self.__socket = self.connect_to_rover(ip, port)
        # We are connected once the api_structure object has been created, so we need to check it exists

        return self.is_connected
    
    def connect(self, calibrate: bool = True) -> None:
        if self.is_connected:
            raise DeviceAlreadyConnectedError(f"{self} already connected")
        
        # Currently doesn't do anything, no configuration needed? Only need to connect.
        self.configure()

        # Connect to the EarthRover here by instantiating an api_structure object (this creates the socket connection automatically)


        if not self.is_calibrated and calibrate:
            logging.info(
                "Mismatch between calibration values in the motor and the calibration file or no calibration file found"
            )
            self.calibrate()
            
        logger.info(f"{self} connected")
    
    def is_calibrated(self) -> bool:
        return self.is_calibrated
    
    def calibrate(self) -> None:
        # Calibrate the IMU, motors, etc?
        if self.calibration:
            
        logger.info(f"\nRunning calibration of {self}")

        # todo
    
    # Not necessary for right now, no configuration needed for the EarthRover
    # Just need to connect using the socket in connect, so possibly configure is unnecessary
    def configure(self):
        # todo
        pass
    
    def get_observation(self) -> dict[str, Any]:
        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected.")

    def send_action(self, action: dict[str, Any]) -> dict[str, Any]:
        """Send control commands to Earthrover Mini Plus"""
       
        # send_ctl_cmd(self.socket, self.speed, self.angular)

        """
        Example of possible action dictionary:

        action = {
            "linear_velocity": 0.2,
            "angular_velocity": 5
        }
        """
        
        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected.")
        
        # The action is the movement command, with a linear velocity and angular velocity
        if "linear_velocity" in action and "angular_velocity" in action:
            v = action["linear_velocity"]
            w = action["angular_velocity"]
            # Call the api call for move, should be higher level not send_ctl_cmd




    def disconnect(self):
        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected.")

        logger.info(f"{self} disconnected.")