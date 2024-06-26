"""
Script for connecting YDlidar to Keelson
-----------------------------------------
"""

import zenoh
import logging
import warnings
import atexit
import json
import time
import keelson
import ydlidar
import math
import numpy as np

from terminal_inputs import terminal_inputs

from keelson.payloads.TimestampedFloat_pb2 import TimestampedFloat
from keelson.payloads.TimestampedString_pb2 import TimestampedString
from keelson.payloads.PointCloud_pb2 import PointCloud
from keelson.payloads.Experimental_PointCloudSimplified_pb2 import PointCloudSimplified
from keelson.payloads.Experimental_PointCloudSimplified_pb2 import RelPointsPosition
from keelson.payloads.LaserScan_pb2 import LaserScan

# Global variable for Zenoh session
session = None


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

    # Point cloud Simplified publisher
    pubkey_point_cloud_simple = keelson.construct_pub_sub_key(
        realm=args.realm,
        entity_id=args.entity_id,
        subject="point_cloud_simplified",
        source_id="ydlidar",
    )
    pub_point_cloud_simple = session.declare_publisher(pubkey_point_cloud_simple)
    logging.info(f"Decler up TELEMETRY publisher: {pubkey_point_cloud_simple}")

    # -----------------------------
    # -----------------------------

    # YDLIDAR Connector
    # -----------------------------
    logging.info(f"Conneting to device: {args.device_port}")

    ydlidar.os_init()
    ports = ydlidar.lidarPortList()
    port = args.device_port

    logging.info(f"Conneting on port: {port}")

    laser = ydlidar.CYdLidar()
    logging.info(f"Conneted: {port}")

    try:
        laser.setlidaropt(ydlidar.LidarPropSerialPort, port)
        laser.setlidaropt(ydlidar.LidarPropSerialBaudrate, 230400)
        laser.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TRIANGLE)
        laser.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)
        laser.setlidaropt(ydlidar.LidarPropScanFrequency, 12.0)
        laser.setlidaropt(ydlidar.LidarPropSampleRate, 9)
        laser.setlidaropt(ydlidar.LidarPropSingleChannel, False)
        laser.setlidaropt(ydlidar.LidarPropMaxAngle, 180.0)
        laser.setlidaropt(ydlidar.LidarPropMinAngle, -180.0)
        laser.setlidaropt(ydlidar.LidarPropMaxRange, 16.0)
        laser.setlidaropt(ydlidar.LidarPropMinRange, 0.1)
        laser.setlidaropt(ydlidar.LidarPropIntenstiy, False)

        ret = laser.initialize()
   
    except Exception as e:
        logging.error(f"ERROR initializing YDLidar: {e}")
        laser.turnOff()
        laser.disconnecting()
        ret = False

    try:
        if ret:
            ret = laser.turnOn()
            scan = ydlidar.LaserScan()

            while ret and ydlidar.os_isOk():

                ret = laser.doProcessSimple(scan)

                if ret:
                    ingress_timestamp = time.time_ns()

                    logging.debug(
                        f"Scan received[{scan.stamp}]:{scan.points.size()} ranges is [{scan.config.scan_time*100}]Hz"
                    )

                    # Point Cloud Parsing and Publishing
                    relative_positions = []
                    simple_points = []

                    for point in scan.points: # Point range in meters and angle in radians
                        if point.range > 0:  
                            # Rounding to millimeters
                            x = round(point.range * math.sin(point.angle),4)
                            y = round(point.range * math.cos(point.angle),4)
                            relative_positions.append([x, y, 0])

                            relpos = RelPointsPosition()
                            relpos.coordinates.extend([float(x), float(y), float(0)])
                            simple_points.append(relpos)

                    logging.debug(f"Points: {len(relative_positions)}")

                    np_relative_pos = np.array(relative_positions)

                    logging.debug(np_relative_pos.dtype)

                    data = np_relative_pos.tobytes()
                    point_stride = len(data) / len(np_relative_pos)

                    payload = PointCloud()
                    payload.point_stride = int(point_stride)
                    payload.data = data
                    payload.timestamp.FromNanoseconds(ingress_timestamp)
                    payload.pose.position.x = 0
                    payload.pose.position.y = 0
                    payload.pose.position.z = 0
                    payload.pose.orientation.x = 0.0
                    payload.pose.orientation.y = 0.0
                    payload.pose.orientation.z = 0.0
                    payload.pose.orientation.w = 1.0
                    # Fields are in float64 (8 bytes each)
                    payload.fields.add(name="x", offset=0, type=8)
                    payload.fields.add(name="y", offset=8, type=8)
                    payload.fields.add(name="z", offset=16, type=8)
                    if args.frame_id is not None:
                        payload.frame_id = args.frame_id
                    serialized_payload = payload.SerializeToString()
                    envelope = keelson.enclose(serialized_payload)
                    pub_point_cloud.put(envelope)
                    logging.debug("...published point cloud to zenoh!")

                    # Simplified Point Cloud Parsing and Publishing (Crowsnest)
                    payload_simple = PointCloudSimplified()
                    payload_simple.timestamp.FromNanoseconds(ingress_timestamp)
                    payload_simple.point_positions.extend(simple_points)
                    serialized_payload_simple = payload_simple.SerializeToString()
                    envelope_simple = keelson.enclose(serialized_payload_simple)
                    pub_point_cloud_simple.put(envelope_simple)
                    logging.debug("...published point cloud SIMPLE to zenoh!")

                else:
                    logging.debug("Failed to get Lidar Data")

                time.sleep(0.05)
            laser.turnOff()

        laser.disconnecting()

    except Exception as e:
        logging.error(f"Exept Error: {e}")
        laser.turnOff()
        laser.disconnecting()

    logging.info(f"END OF SCRIPT")
