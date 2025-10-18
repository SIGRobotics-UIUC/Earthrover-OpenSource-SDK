from socket import socket
import logging

from .config_earthrover_mini_plus import EarthRoverMiniPlusConfig, EarthRoverMiniPlusHostConfig
from earthrover_mini_plus import EarthRoverMiniPlus


class EarthRoverMiniPlusHost:
    def __init__(self, config: EarthRoverMiniPlusHostConfig):
        self.port_cmd = config.port_cmd
        self.port_observations = config.port_observations

        self.connection_time_s = config.connection_time_s
        self.watchdog_timeout_ms = config.watchdog_timeout_ms
        self.max_loop_freq_hz = config.max_loop_freq_hz
    
    def disconnect(self):
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)  # disabling send and receive
            except OSError:
                pass  # socket already closed or not connected
            self.socket.close()
            self.socket = None  # clear reference

def main():
    logging.info("Configuring Earthrover Mini Plus")
    robot_config = EarthRoverMiniPlusConfig()
    robot = EarthRoverMiniPlus(robot_config)

    logging.info("Connecting Earthrover Mini Plus")
    robot.connect()

    logging.info("Starting HostAgent")
    host_config = EarthRoverMiniPlusHostConfig()
    host = EarthRoverMiniPlusHost(host_config)

    last_cmd_time = time.time()
    watchdog_active = False
    logging.info("Waiting for commands...")
    try:
        # commands based on API

    except KeyboardInterrupt:
        print("Keyboard interrupt received. Exiting...")
    finally:
        print("Shutting down Earthrover Mini Plus Host.")
        robot.disconnect()
        host.disconnect()

    logging.info("Finished Earthrover Mini Plus cleanly")



if __name__ == "__main__":
    main()