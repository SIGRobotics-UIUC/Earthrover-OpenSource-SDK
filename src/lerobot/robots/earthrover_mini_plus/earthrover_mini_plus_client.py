import logging
from socket import socket

from lerobot.utils.errors import DeviceAlreadyConnectedError, DeviceNotConnectedError

from ..robot import Robot
from .config_earthrover_mini_plus import EarthRoverMiniPlusConfig


class EarthRoverMiniPlusClient(Robot):
    config_class = EarthRoverMiniPlusConfig
    name = "earthrover_mini_plus_client"

    def __init__(self, config: EarthRoverMiniPlusConfig):

        super().__init__(config)
        self.config = config

        self.remote_ip = config.remote_ip
        self.port_cmd = config.port_cmd
        self.port_observations = config.port_observations

        self.teleop_keys = config.teleop_keys
        self.cameras = config.cameras
        

        self.polling_timeout_ms = config.polling_timeout_ms
        self.connect_timeout_s = config.connect_timeout_s

        self.is_connected = False
        self.logs = {}

    @cached_property
    def is_connected(self) -> bool:
        return self.is_connected
    
    def connect(self) -> None:
        """Establish ZMQ sockets with the remote mobile robot"""

        if self.is_connected:
            raise DeviceAlreadyConnectedError(
                "Earthrover Mini Plus is already connected. Do not run `robot.connect()` twice."
            )

        self.socket = socket.create_connection((self.ip, self.port_cmd))
        self.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        # todo: check if this is valid
        if self.socket.timeout:
            raise DeviceNotConnectedError("Timeout waiting for Earthrover Mini Plus Host to connect expired.")

        self._is_connected = True

    def disconnect(self):

        if not self._is_connected:
            raise DeviceNotConnectedError(
                "LeKiwi is not connected. You need to run `robot.connect()` before disconnecting."
            )

        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)  # disabling send and receivedisables both send and receive
            except OSError:
                pass  # socket already closed or not connected
            self.socket.close()
            self.socket = None  # clear reference
        
        self._is_connected = False