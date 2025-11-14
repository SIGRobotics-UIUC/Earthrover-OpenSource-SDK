#!/usr/bin/env python3

import time
import logging

from lerobot.teleoperators.keyboard import KeyboardRoverTeleop
from lerobot.robots.earthrover_mini_plus import EarthRover_Mini
from lerobot.robots.earthrover_mini_plus import EarthRoverMiniPlusConfig
from lerobot.teleoperators.keyboard.configuration_keyboard import KeyboardTeleopConfig
from lerobot.utils.errors import DeviceNotConnectedError

logging.basicConfig(level=logging.INFO)

def main():
    print("\n=== EarthRover Mini – Keyboard Teleop Test (WASD) ===")
    print("Controls:")
    print("    w/s = forward/backward")
    print("    a/d = rotate left/right")
    print("    space or x = stop")
    print("    t/g = speed multiplier up/down")
    print("    r = reset velocities")
    print("    q = quit")
    print("==============================================\n")

    # -------------------------------------------------------
    # 1. Create Robot
    # -------------------------------------------------------
    robot_config = EarthRoverMiniPlusConfig()
    robot = EarthRover_Mini(robot_config)

    print("Connecting to robot...")
    robot.connect(calibrate=False)
    print("Robot connected!\n")

    # ⭐ **Start camera streaming**
    robot.start_camera_stream()

    # -------------------------------------------------------
    # 2. Create Teleop
    # -------------------------------------------------------
    teleop_cfg = KeyboardTeleopConfig() 
    teleop = KeyboardRoverTeleop(teleop_cfg)

    print("Starting keyboard teleop listener...")
    teleop.connect()
    print("Keyboard teleop active! Use WASD to drive.\n")

    # -------------------------------------------------------
    # 3. Teleop loop
    # -------------------------------------------------------
    loop_dt = 0.05   # 50ms = 20Hz
    last_print = time.time()

    try:
        while True:
            # Read key-based velocity commands
            action = teleop.get_action()     # linear + angular

            # Check events (quit, help)
            events = teleop.get_teleop_events()
            if events.get("terminate_episode", False):
                print("Quit triggered from keyboard.")
                break

            # Send to robot
            try:
                robot.send_action(action)
            except DeviceNotConnectedError:
                print("Robot lost connection!")
                break

           

            time.sleep(loop_dt)

    except KeyboardInterrupt:
        print("\nCTRL-C received. Shutting down teleop…")

    # -------------------------------------------------------
    # 4. Cleanup
    # -------------------------------------------------------
    try:
        teleop.disconnect()
    except:
        pass

    try:
        robot.close_camera_stream()
        robot.disconnect()
    except:
        pass

    print("Teleop closed. Goodbye!")


if __name__ == "__main__":
    main()
