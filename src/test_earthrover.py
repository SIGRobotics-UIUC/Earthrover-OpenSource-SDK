import sys
import cv2
from lerobot.cameras.earthrover_mini_camera import EarthRoverMiniCamera
from lerobot.cameras.earthrover_mini_camera.configuration_earthrover_mini import EarthRoverMiniCameraConfig, ColorMode


config = EarthRoverMiniCameraConfig(
    index_or_path=EarthRoverMiniCameraConfig.FRONT_CAM_MAIN,  # front main stream
    fps=30,
    width=640,
    height=480,
    color_mode=ColorMode.RGB
)

# 2️⃣ Instantiate the camera
camera = EarthRoverMiniCamera(config)

# 3️⃣ Connect to the camera
print("Connecting to camera...")
camera.connect()

if camera.is_connected:
    print("Camera connected successfully!")
else:
    print("Failed to connect to the camera. Exiting...")
    sys.exit(1)

# 4️⃣ Display frames in a loop
try:
    while True:
        frame = camera.read()  # synchronous read
        cv2.imshow("Earth Rover Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # 5️⃣ Disconnect and cleanup
    camera.disconnect()
    cv2.destroyAllWindows()
