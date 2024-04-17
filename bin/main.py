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
    # Obj = PyLidar3.YdLidarG4(args.device_port)
    Obj = PyLidar3.YdLidarG4(port)

    if(Obj.Connect()):

        logging.info("DeviceInfo:",Obj.GetDeviceInfo())
        logging.info("HealtStatus:",Obj.GetHealthStatus())
        logging.info("CurrentFrequency:",Obj.GetCurrentFrequency())
        logging.info("CurrentRangingFrequency:",Obj.GetCurrentRangingFrequency())

        gen = Obj.StartScanning()
        t = time.time() # start time 
        
        while (time.time() - t) < 30: #scan for 30 seconds
            logging.debug(next(gen)) #  angle(degrees) and distance(millimeters).
            time.sleep(0.5)
        Obj.StopScanning()
        Obj.Disconnect()

    else:
        logging.error("Error connecting to device")

    logging.info(f"END OF SCRIPT") 