"""
Example usage of KeyboardRoverTeleop with EarthRoverMiniPlus robot.
This demonstrates how to teleoperate the rover using keyboard controls.
"""

import time
import logging
from lerobot.robots.earthrover_mini_plus.robot_earthrover_mini_plus import EarthRoverMiniPlus
from lerobot.robots.earthrover_mini_plus.config_earthrover_mini_plus import EarthRoverMiniPlusConfig
from lerobot.teleoperators.keyboard.teleop_keyboard import KeyboardRoverTeleop,  PYNPUT_AVAILABLE
from lerobot.teleoperators.keyboard.configuration_keyboard import KeyboardTeleopConfig

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
        
     
    

        """Main teleoperation loop for EarthRover Mini Plus."""


  
        # Initialize robot configuration
        robot_config = EarthRoverMiniPlusConfig(
            port="8888",
            remote_ip="192.168.11.1"
        )
        
        # Initialize keyboard teleop configuration
        teleop_config = KeyboardTeleopConfig(
            mock=False
        )
        
        # Create robot and teleop instances
        print("Initializing EarthRover Mini Plus...")
        robot = EarthRoverMiniPlus(robot_config)
        
        print("Initializing Keyboard Teleop...")
        teleop = KeyboardRoverTeleop(teleop_config)
        
        try:
            # Connect to robot
            print("Connecting to robot...")
            robot.connect(calibrate=False)
            print("Robot connected!")
            
            # Connect keyboard teleop
            print("Connecting keyboard listener...")
            teleop.connect()
            print("Keyboard listener connected!")
            
            # Show controls
            teleop.print_controls()
            
            # Optional: Start camera stream in separate thread
            # robot.start_camera_stream()
            
            print("\n🎮 Teleoperation started! Use keyboard to control the rover.")
            print("Press 'h' to show controls again, 'q' to quit.\n")
            
            # Main control loop
            loop_rate = 30  # Hz
            dt = 1.0 / loop_rate
            
            while True:
                loop_start = time.perf_counter()
                
                # Get action from keyboard
                action = teleop.get_action()
                
                # Get teleoperation events
                events = teleop.get_teleop_events()
                
                # Handle events
                if events.get("show_help", False):
                    teleop.print_controls()
                
                if events.get("terminate_episode", False):
                    print("\n🛑 Quit command received. Stopping rover...")
                    break
                
                # Send action to robot
                if action["linear_velocity"] != 0 or action["angular_velocity"] != 0:
                    print("_________calling____________--------------------------------------------------------------------")
                    robot.send_action(action)
                    
                    # Print current status
                    status = teleop.get_status()
                    print(f"\r⚡ Linear: {status['effective_linear']:6.1f} | "
                        f"Angular: {status['effective_angular']:6.1f} | "
                        f"Multiplier: {status['speed_multiplier']:.1f}x", 
                        end="", flush=True)
                else:
                    # Send stop command when velocities are zero
                    print("_________calling____________--------------------------------------------------------------------")
                    robot.send_action({"linear_velocity": 0, "angular_velocity": 0})
                
                # Optional: Get and process observations
                # obs = robot.get_observation()
                # Process camera frames, telemetry, etc.
                
                # Maintain loop rate
                elapsed = time.perf_counter() - loop_start
                sleep_time = max(0, dt - elapsed)
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  KeyboardInterrupt received.")
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
            logging.exception("Error in main loop")
        finally:
            # Cleanup
            print("\nCleaning up...")
            
            # Stop the rover
            try:
                robot.send_action({"linear_velocity": 0, "angular_velocity": 0})
                print("✅ Rover stopped")
            except:
                pass
            
            # Disconnect teleop
            try:
                teleop.disconnect()
                print("✅ Keyboard disconnected")
            except:
                pass
            
            # Close camera stream if started
            try:
                robot.close_camera_stream()
                print("✅ Camera stream closed")
            except:
                pass
            
            # Disconnect robot
            try:
                robot.disconnect()
                print("✅ Robot disconnected")
            except:
                pass
            
            print("\n👋 Teleoperation ended.\n")
