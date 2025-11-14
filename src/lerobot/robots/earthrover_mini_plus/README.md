# Documentation EarthRover_Mini API

## Introduction/Overview
The EarthRover_Mini API provides a simple and easy to use interfaec with the Earth Rover Mini+ robot, while integrating itself with LeRobot's data collection and uploading pipeline. 

## Installation:
To install the package, simply:


## Example:

```python
rover = EarthRoverMiniBlocking("192.168.11.1", 8888)
rover.connect()
print("\n[TEST] Ping test:")
rover.safe_ping()
print("\n[TEST] Move test (3s at speed=60, angular=360):")
rover.move(3, 60, 360)
print("\n[TEST] IMU read:")
imu_data = rover.imu_mag_read()
print("IMU/MAG Data:", imu_data)
print("\n[TEST] Telemetry read:")
telemetry = rover.get_telemetry(timeout=1.0)
print("Telemetry:", telemetry)

rover.disconnect()
```

## Functions:

## 