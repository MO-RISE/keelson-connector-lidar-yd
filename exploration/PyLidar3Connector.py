# Source: https://github.com/YDLIDAR/YDLidar-SDK/tree/master/python/examples

import PyLidar3
import logging
import time

logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s %(message)s", level=args.log_level
    )

logging.info(f"Conneting to device: {args.device_port}")
port = "/dev/ttyACM1" 
port = args.device_port
# Obj = PyLidar3.YdLidarG4(args.device_port)
Obj = PyLidar3.YdLidarG4(port)

if(Obj.Connect()):
    logging.info(f"DeviceInfo: {Obj.GetDeviceInfo()}")
    logging.info(f"HealtStatus: {Obj.GetHealthStatus()}")
    logging.info(f"CurrentFrequency: {Obj.GetCurrentFrequency()}")
    logging.info(f"CurrentRangingFrequency:{Obj.GetCurrentRangingFrequency()}")

    gen = Obj.StartScanning()
    t = time.time() # start time 
    
    while (time.time() - t) < 30: #scan for 30 seconds
        ingress_timestamp = time.time_ns()
        scan_360 = next(gen) # Output: Dict, {angle_degrees(key) : distance_millimeters(int), ...}
        logging.debug(f"scan_360: {scan_360}") 
        logging.debug(f"scan_360: {type(scan_360)}") 
        payload = LaserScan()
        payload.timestamp.FromNanoseconds(ingress_timestamp)
        payload.start_angle = 0 # Bearing of first point, in radians
        payload.start_angle = 6.26573 # Bearing of last point, in radians
        # Distance of detections from origin; assumed to be at equally-spaced angles between `start_angle` and `end_angle`
        ranges = scan_360.values()     
        ranges_arr_float = [float(value) for value in ranges]
        payload.ranges.extend(ranges_arr_float) 

        # POSE ???? 

        # Zero relative position
        payload.pose.position.x = 0
        payload.pose.position.y = 0
        payload.pose.position.z = 0

        # Identity quaternion
        # payload.pose.rotation.x = 0
        # payload.pose.rotation.y = 0
        # payload.pose.rotation.z = 0
        # payload.pose.rotation.w = 1

        # Fields are in float64 (8 bytes each)
        # payload.fields.add(name="x", offset=0, type=8)
        # payload.fields.add(name="y", offset=8, type=8)
        # payload.fields.add(name="z", offset=16, type=8)

        serialized_payload = payload.SerializeToString()
        envelope = keelson.enclose(serialized_payload)
        pub_scan.put(envelope)

        
        time.sleep(0.5)
    Obj.StopScanning()
    Obj.Disconnect()
else:
    logging.error("Error connecting to device")