import logging
import asyncio
from socket import socket

from lerobot.utils.errors import DeviceAlreadyConnectedError, DeviceNotConnectedError

from ..robot import Robot
from .config_earthrover_mini_plus import EarthRoverMiniPlusConfig

# temporary import directly from the file api
# change to import from the pip
from .earthrover_api.earthrover_api import Earthrover_API


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

        self.rover = None

    @cached_property
    def is_connected(self) -> bool:
        return self.is_connected
    
    async def connect_async(self):
        self.rover = Earthrover_API(self.ip, self.port_cmd)
        await self.rover.connect()  # your async connect call
        print("Successfully connected to Earthrover")
        self._is_connected = True
    
    def connect(self) -> None:
        # """Establish ZMQ sockets with the remote mobile robot"""

        # if self.is_connected:
        #     raise DeviceAlreadyConnectedError(
        #         "Earthrover Mini Plus is already connected. Do not run `robot.connect()` twice."
        #     )

        # self.socket = socket.create_connection((self.ip, self.port_cmd))
        # self.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        # # todo: check if this is valid
        # if self.socket.timeout:
        #     raise DeviceNotConnectedError("Timeout waiting for Earthrover Mini Plus Host to connect expired.")

        if self.is_connected:
            raise DeviceAlreadyConnectedError(
                "Earthrover Mini Plus is already connected. Do not run `robot.connect()` twice."
            )
        
        # The client (laptop or other device) connects through socket connection,
        # done through the Earthrover api
        # Get the current event loop (or create one if none exists)
        try:
            loop = asyncio.get_running_loop()
            # If we are already in an async context, schedule the task
            loop.create_task(self.connect_async())
        except RuntimeError:
            # No running loop, safe to run blocking
            asyncio.run(self.connect_async())
    
    async def disconnect_async(self):
        if self.rover:
            await self.rover.disconnect()
            print("Successfully disconnected from Earthrover")
            self.is_connected = False


    def disconnect(self):

        if not self._is_connected:
            raise DeviceNotConnectedError(
                "Earthrover is not connected. You need to run `robot.connect()` before disconnecting."
            )

        # if self.socket:
        #     try:
        #         self.socket.shutdown(socket.SHUT_RDWR)  # disabling send and receivedisables both send and receive
        #     except OSError:
        #         pass  # socket already closed or not connected
        #     self.socket.close()
        #     self.socket = None  # clear reference

        try:
            loop = asyncio.get_running_loop()
            future = asyncio.run_coroutine_threadsafe(self._disconnect_async(), loop)
            future.result()  # blocks until done
        except RuntimeError:
            asyncio.run(self.disconnect_async())