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

from terminal_inputs import terminal_inputs

from keelson.payloads.TimestampedFloat_pb2 import TimestampedFloat
from keelson.payloads.TimestampedString_pb2 import TimestampedString
from keelson.payloads.PointCloud_pb2 import PointCloud
import struct

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

    ydlidar.os_init()
    ports = ydlidar.lidarPortList()
    port = args.device_port

    for key, value in ports.items():
        port = value
        logging.info(f"Conneting to port: {port}")

    laser = ydlidar.CYdLidar()
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

                # logging.debug(f"Scan received points:{scan.points}")

                readings = []
                for point in scan.points:
                    readings.append([point.angle, point.range])

                # logging.debug(readings)
                logging.debug(f"Readings: {len(readings)}")

                relative_positions = []

                for point in scan.points:

                    x = point.range * math.cos(point.angle)
                    y = point.range * math.sin(point.angle)
                    
                    if x > 0 or y > 0:
                        relative_positions.append([x, y, 0])
                    # else:
                    #     logging.debug(f"Point Coord: {x, y}")
                    #     logging.debug(f"Point: {point.angle, point.range}")

                # logging.debug(relative_positions)
                logging.debug(f"Points: {len(relative_positions)}")

                payload = PointCloud()

                # data = relative_positions.tobytes() ERROR 
                # Convert relative_positions to bytes
                data = b"".join(struct.pack("dd", x, y) for x, y, _ in relative_positions)
                
                point_stride = len(data) / len(relative_positions)

                logging.debug("Point stride: %s", point_stride)
                payload.point_stride = int(point_stride)

                payload.data = data

                payload.timestamp.FromNanoseconds(ingress_timestamp)
                # POSE 
                payload.pose.position.x = 0
                payload.pose.position.y = 0
                payload.pose.position.z = 0
                # payload.pose.rotation.x = 0 ERROR 
                # payload.pose.rotation.y = 0
                # payload.pose.rotation.z = 0
                # payload.pose.rotation.w = 1
                            # Fields are in float64 (8 bytes each)
                payload.fields.add(name="x", offset=0, type=8)
                payload.fields.add(name="y", offset=8, type=8)
                payload.fields.add(name="z", offset=16, type=8)
                serialized_payload = payload.SerializeToString()

                logging.debug("...serialized.")

                envelope = keelson.enclose(serialized_payload)
                # logging.debug("...enclosed into envelope, serialized as: %s", envelope)

                pub_point_cloud.put(envelope)
                logging.debug("...published to zenoh!")

            else:
                logging.debug("Failed to get Lidar Data")

            time.sleep(0.05)
        laser.turnOff()
    laser.disconnecting()

    logging.info(f"END OF SCRIPT")
