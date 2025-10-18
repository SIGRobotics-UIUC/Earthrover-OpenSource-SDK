import logging
from socket import socket

from lerobot.utils.errors import DeviceAlreadyConnectedError, DeviceNotConnectedError

from lerobot.cameras.utils import make_cameras_from_configs

from ..robot import Robot
from .config_earthrover_mini_plus import EarthRoverMiniPlusConfig


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
        return self.is_connected
    
    def connect(self, calibrate: bool = True) -> None:
        if self.is_connected:
            raise DeviceAlreadyConnectedError(f"{self} already connected")
        
        self.configure()

        if not self.is_calibrated and calibrate:
            logging.info(
                "Mismatch between calibration values in the motor and the calibration file or no calibration file found"
            )
            self.calibrate()
            
        logger.info(f"{self} connected")
    
    def is_calibrated(self) -> bool:
        return self.is_calibrated
    
    def calibrate(self) -> None:
        if self.calibration:
            
        logger.info(f"\nRunning calibration of {self}")

        # todo
    
    def configure(self):
        # todo
        pass
    
    def get_observation(self) -> dict[str, Any]:
        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected.")

    def send_action(self, action: dict[str, Any]) -> dict[str, Any]:
        """Send control commands to Earthrover Mini Plus"""
       
        # send_ctl_cmd(self.socket, self.speed, self.angular)
        
        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected.")


    def disconnect(self):
        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected.")

        logger.info(f"{self} disconnected.")