import os
import ydlidar
import time

if __name__ == "__main__":
    ydlidar.os_init()
    ports = ydlidar.lidarPortList()
    port = "/dev/ydlidar"
    for key, value in ports.items():
        port = value
        print(port)
    
    laser = ydlidar.CYdLidar()
    laser.setlidaropt(ydlidar.LidarPropSerialPort, port)
    laser.setlidaropt(ydlidar.LidarPropSerialBaudrate, 230400)
    laser.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TRIANGLE)
    laser.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)
    laser.setlidaropt(ydlidar.LidarPropScanFrequency, 10.0)
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
            r = laser.doProcessSimple(scan)
            if r:
                print(f"Scan received[{scan.stamp}]:{scan.points.size()} ranges is [{scan.config.scan_time}]Hz")
                print(f"Scan received points:{scan.points}")

                readings = [] 
                for point in scan.points:
                    readings.append([point.angle, point.range])
                print(readings)
                print(len(readings))
           
            else :
                print("Failed to get Lidar Data")
            time.sleep(0.05)
        laser.turnOff()
    laser.disconnecting()

# Start: -0.338975727558136,

# End: -0.3430665135383606


