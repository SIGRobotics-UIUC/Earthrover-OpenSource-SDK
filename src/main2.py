#!/usr/bin/env python3

import time
import logging
import asyncio

from lerobot.teleoperators.earthrover_mini_plus_teleoperator import (
    EarthroverKeyboardTeleopActions,
    EarthroverKeyboardTeleopConfigActions,
)
from lerobot.robots.earthrover_mini_plus import (
    EarthRoverMiniPlusConfig,
    EarthRoverMiniPlus,
)

#logging.basicConfig(level=logging.INFO)

async def main():
    # Step 1: Create teleop config and instance
    teleop_config = EarthroverKeyboardTeleopConfigActions()
    teleop = EarthroverKeyboardTeleopActions(teleop_config)
    
    # Connect keyboard listener
    teleop.connect()

    # Step 2: Create robot client config and instance
    client_config = EarthRoverMiniPlusConfig(remote_ip="192.168.11.1", port=8888)  # change IP to your robot
    print("client config: \n")
    print(client_config)
    print("\n")
    client = EarthRoverMiniPlus(client_config)
    
    # Connect to robot
    await client.connect()
    #logging.info("Teleop and client connected. Starting control loop...")

    try:
        while True:
            # # Step 3: Read teleop keys
            teleop_action = teleop.get_action()
            # teleop_action example: {'speed': 5.0, 'angular': 0.5, 'duration': 0.5}

            # Step 4: Convert to robot API format
            linear_velocity = teleop_action.get("speed", 0.0)
            angular_velocity = teleop_action.get("angular", 0.0)

            action_dict = {
                "linear_velocity": linear_velocity,
                "angular_velocity": angular_velocity,
            }

            # Step 5: Send action to robot
            await client.send_action(action_dict)

            # Optional: small sleep to avoid busy loop
            time.sleep(0.05)  # 20 Hz loop

    except KeyboardInterrupt:
        pass
        #logging.info("Keyboard interrupt received. Shutting down...")

    finally:
        # Disconnect everything cleanly
        print("hello disconneted")
        teleop.disconnect()
        await client.disconnect()
        #logging.info("Teleop and client disconnected.")

if __name__ == "__main__":
    asyncio.run(main())

