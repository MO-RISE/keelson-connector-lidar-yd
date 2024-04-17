# Keelson Connector Lidar YD

Supported and tested sensor types:

- G2 (Budrate: 230400 SampleRate: 5)
  - [Development Manual](https://www.ydlidar.com/Public/upload/files/2022-07-25/YDLIDAR%20G2%20Development%20Manual%20V1.1(211230).pdf)
  - [User Manual](https://www.ydlidar.com/Public/upload/files/2022-06-21/YDLIDAR%20G2%20Lidar%20User%20Manual%20V1.3(211230).pdf)
  - [Data Sheet](https://www.ydlidar.com/Public/upload/files/2022-06-21/YDLIDAR%20G2%20Data%20Sheet%20V1.3(211230).pdf)

## Python SDK

[PyLidar3](https://github.com/lakshmanmallidi/PyLidar3)

Output: Dictionry angle(degrees) and distance(millimeters) 

## Run main.py start script examle

```bash
python bin/main.py -r rise -e boatswain --device-port /dev/ttyACM1 --log-level 10 
```

## Truble shooting / Lessons learned  

```bash
# If you do not have access rights to read devise 
sudo chmod a+rw /dev/ttyACM1
```

https://github.com/YDLIDAR/YDLidar-SDK/blob/master/doc/YDLIDAR_SDK_API_for_Developers.md 