"""
Script for connecting YDlidar to Keelson.
"""

import zenoh
import logging
import warnings
import atexit
import json
import time
import keelson
import PyLidar3

from terminal_inputs import terminal_inputs

from keelson.payloads.TimestampedFloat_pb2 import TimestampedFloat
from keelson.payloads.TimestampedString_pb2 import TimestampedString
from keelson.payloads.LaserScan_pb2 import LaserScan
# Global variable for Zenoh session
session = None

"""
Arguments / configurations are set in docker-compose.yml
"""
if __name__ == "__main__":
    
    # BASE SETUP and INITIALIZATION
    # -----------------------------

    # Input arguments and configurations
    args = terminal_inputs()
    # Setup logger
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s %(message)s", level=args.log_level
    )
    logging.captureWarnings(True)
    warnings.filterwarnings("once")
    ## Construct session
    logging.info("Opening Zenoh session...")
    conf = zenoh.Config()
    if args.connect is not None:
        conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(args.connect))
    session = zenoh.open(conf)
    def _on_exit():
        session.close()
    atexit.register(_on_exit)
    logging.info(f"Zenoh session: {session.info()}")
    # -----------------------------
    # -----------------------------


    # INITIALIZATION PUBLISHERS 
    # -----------------------------
    
    # Scan publisher
    pubkey_scan = keelson.construct_pub_sub_key(
        realm=args.realm,
        entity_id=args.entity_id,
        subject="laser_scan",
        source_id="ydlidar",
    )
    pub_scan = session.declare_publisher(pubkey_scan)
    logging.info(f"Decler up TELEMETRY publisher: {pubkey_scan}")

    # Point cloud publisher
    pubkey_point_cloud = keelson.construct_pub_sub_key(
        realm=args.realm,
        entity_id=args.entity_id,
        subject="point_cloud",
        source_id="ydlidar",
    )
    pub_point_cloud = session.declare_publisher(pubkey_point_cloud)
    logging.info(f"Decler up TELEMETRY publisher: {pubkey_point_cloud}")

    # -----------------------------
    # -----------------------------



    # YDLIDAR Connector 
    # -----------------------------
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
            scan_360 = next(gen) # Dict, {angle(degrees) : distance(millimeters), ...}
            logging.debug(f"scan_360: {scan_360}") 
            payload = LaserScan()
            payload.timestamp.FromNanoseconds(ingress_timestamp)
            payload.start_angle = 0 # Bearing of first point, in radians
            payload.start_angle = 6.28319 # Bearing of last point, in radians
            # Distance of detections from origin; assumed to be at equally-spaced angles between `start_angle` and `end_angle`
            payload.ranges = scan_360.values()  

            # POSE ???? 

            # Zero relative position
            payload.pose.position.x = 0
            payload.pose.position.y = 0
            payload.pose.position.z = 0

            # Identity quaternion
            payload.pose.rotation.x = 0
            payload.pose.rotation.y = 0
            payload.pose.rotation.z = 0
            payload.pose.rotation.w = 1

            # Fields are in float64 (8 bytes each)
            payload.fields.add(name="x", offset=0, type=8)
            payload.fields.add(name="y", offset=8, type=8)
            payload.fields.add(name="z", offset=16, type=8)

            serialized_payload = payload.SerializeToString()
            envelope = keelson.enclose(serialized_payload)
            pubkey_scan.put(envelope)

            
            time.sleep(0.5)
        Obj.StopScanning()
        Obj.Disconnect()

    else:
        logging.error("Error connecting to device")

    logging.info(f"END OF SCRIPT") 