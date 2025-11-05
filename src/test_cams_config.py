import sys
import cv2
from dataclasses import dataclass, field

from lerobot.robots.robot import Robot
from lerobot.cameras.camera import Camera
from lerobot.cameras.configs import CameraConfig, Cv2Rotation
from lerobot.robots.earthrover_mini_plus import (EarthRoverMiniPlusConfig, EarthRoverMiniPlus)
from lerobot.cameras.earthrover_mini_camera import EarthRoverMiniCamera
from lerobot.cameras.earthrover_mini_camera.configuration_earthrover_mini import EarthRoverMiniCameraConfig, ColorMode
# EXAMPLE TESTING FILE FOR EARTHROVER CAMERAS



#client_config = EarthRoverMiniPlusConfig(remote_ip="192.168.11.1", port=8888) 
#client = EarthRoverMiniPlus(client_config)

# --------------------------------------------------------------------------------
# Define camera configurations
def earthrover_mini_plus_cameras_config() -> dict[str, CameraConfig]:
    # to edit based on earth rover's cameras
    return {
        "front main": EarthRoverMiniCameraConfig(
            index_or_path= EarthRoverMiniCameraConfig.FRONT_CAM_MAIN, color_mode=ColorMode.RGB
        ),
        "rear main": EarthRoverMiniCameraConfig(
            index_or_path=EarthRoverMiniCameraConfig.REAR_CAM_MAIN, color_mode=ColorMode.RGB
        ),
        "front sub": EarthRoverMiniCameraConfig(
            index_or_path= EarthRoverMiniCameraConfig.FRONT_CAM_SUB, color_mode=ColorMode.RGB
        ),
        "rear sub": EarthRoverMiniCameraConfig(
            index_or_path=EarthRoverMiniCameraConfig.REAR_CAM_SUB, color_mode=ColorMode.RGB
        )
    }
# front_main_config = EarthRoverMiniCameraConfig(
#     index_or_path=EarthRoverMiniCameraConfig.FRONT_CAM_MAIN,  # front main stream
#     color_mode=ColorMode.RGB
# )

# front_sub_config = EarthRoverMiniCameraConfig(
#     index_or_path=EarthRoverMiniCameraConfig.FRONT_CAM_SUB,  # front sub stream
#     color_mode=ColorMode.RGB
# )

# rear_main_config = EarthRoverMiniCameraConfig(
#     index_or_path=EarthRoverMiniCameraConfig.REAR_CAM_MAIN,  # rear main stream
#     color_mode=ColorMode.RGB
# )

# rear_sub_config = EarthRoverMiniCameraConfig(
#     index_or_path=EarthRoverMiniCameraConfig.REAR_CAM_SUB,  # rear sub stream
#     color_mode=ColorMode.RGB
# )
config_list = earthrover_mini_plus_cameras_config()
print(config_list["front main"])
# config_list = [front_main_config, front_sub_config, rear_main_config, rear_sub_config]
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# Create all cameras
cameras = {}
for key, cfg in config_list.items():
    print(f"[KEY {key}] CONFIG = {cfg}")
    cameras[key] = EarthRoverMiniCamera(cfg)
    print(f"cameras item = {cameras[key]}")

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# Connect to all cameras
for cam in cameras.values():
    print(f"Connecting to camera {cam.config.index_or_path}...")
    cam.connect()
    if cam.is_connected:
        print(f"{cam.config.index_or_path} connected successfully!")
    else:
        print(f"Failed to connect to {cam.config.index_or_path}. Exiting...")
        sys.exit(1)
# --------------------------------------------------------------------------------
# Read frames from cameras
try:
    while True:
        for idx, cam in enumerate(cameras.values()):
            frame = cam.read()
            cv2.imshow(f"RTSP Stream {idx}", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
finally:
    for cam in cameras:
        cam.disconnect()
    cv2.destroyAllWindows()
# --------------------------------------------------------------------------------