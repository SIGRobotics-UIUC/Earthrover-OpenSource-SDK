#!/usr/bin/env python3

import time
import logging
import asyncio
import threading
import queue
import cv2 # Needed for the display thread

from lerobot.teleoperators.earthrover_mini_plus_teleoperator import (
    EarthroverKeyboardTeleopActions,
    EarthroverKeyboardTeleopConfigActions,
)
from lerobot.robots.earthrover_mini_plus import (
    EarthRoverMiniPlusConfig,
    EarthRoverMiniPlus,
)

# -------------------------------------------------------------
# 1. DISPLAY SETUP: Queue and Thread Function
# -------------------------------------------------------------

# Define a thread-safe queue to pass frames from the main (async) loop 
# to the display (sync) thread. Maxsize=1 means we always pass the LATEST frame.
DISPLAY_QUEUE = queue.Queue(maxsize=100) 

def display_loop():
    """
    Synchronous function that runs in a separate thread. 
    It handles all blocking OpenCV GUI operations.
    """
    window_name = "Earth Rover Front Camera Feed (Press 'q' to quit)"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    while True:
        try:
            # Get the frame from the queue, wait up to 30ms (a typical video frame time)
            frame = DISPLAY_QUEUE.get(timeout=0.03) 
            
            # Display the frame
            cv2.imshow(window_name, frame)
            
            # Must call waitKey to refresh the window and process events.
            # waitKey(1) waits 1ms for a key press.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except queue.Empty:
            # This happens when the main loop is running, but no new frame is available yet.
            # We still need to call cv2.waitKey(1) to keep the window responsive.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            # Handle unexpected shutdown
            print(f"Display thread error: {e}")
            break
    
    cv2.destroyAllWindows()
    print("Display thread shut down.")

# -------------------------------------------------------------
# 2. ASYNC MAIN LOOP
# -------------------------------------------------------------

async def main():
    # Step 1: Create teleop config and instance
    teleop_config = EarthroverKeyboardTeleopConfigActions()
    teleop = EarthroverKeyboardTeleopActions(teleop_config)
    teleop.connect()

    # Step 2: Create robot client config and instance
    client_config = EarthRoverMiniPlusConfig(remote_ip="192.168.11.1", port=8888) 
    print("Client config: " + str(client_config))
    client = EarthRoverMiniPlus(client_config)
    
    # Connect to robot and cameras
    await client.connect()
    print("Teleop and client connected. Starting control loop...")
    
    # --- Start the separate display thread here ---
    display_thread = threading.Thread(target=display_loop, daemon=True)
    display_thread.start()
    print("Display thread started...")
    # -----------------------------------------------

    try:
        # Loop continues as long as the display window is open
        while display_thread.is_alive(): 

            # Step 3: Get observation (includes frame and robot telemetry)
            obs_dict = await client.get_observation()
            
            # Extract the front camera frame using the key defined in the config
            frame = obs_dict.get("front")

            # Non-blocking frame push to display thread
            if frame is not None:
                if DISPLAY_QUEUE.full():
                    # Discard the old frame if the queue is full (prioritize latest)
                    try:
                        DISPLAY_QUEUE.get_nowait()
                    except queue.Empty:
                        pass # Should not happen if full() was True

                # Put the new frame into the queue
                DISPLAY_QUEUE.put_nowait(frame) 

            # Step 4: Read teleop keys
            teleop_action = teleop.get_action()
            
            # Step 5: Convert to robot API format
            linear_velocity = teleop_action.get("speed", 0.0)
            angular_velocity = teleop_action.get("angular", 0.0)

            action_dict = {
                "linear_velocity": linear_velocity,
                "angular_velocity": angular_velocity,
            }

            # Step 6: Send action to robot
            await client.send_action(action_dict)
            
            # Optional: yield control to the asyncio loop
            await asyncio.sleep(0.05) 

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received.")

    finally:
        # Disconnect everything cleanly
        print("Shutting down...")
        teleop.disconnect()
        await client.disconnect()
        
        # In case the display thread didn't stop, manually clear the windows
        cv2.destroyAllWindows() 
        
        # Signal display thread to stop (by joining it)
        if display_thread.is_alive():
            print("Waiting for display thread to join...")
            # We don't have an explicit stop signal other than 'q', but joining is good practice.
            display_thread.join(timeout=2) 
        
        print("Client and teleop disconnected.")


if __name__ == "__main__":
    # Ensure cv2 is imported before asyncio.run for stability on some systems
    asyncio.run(main())