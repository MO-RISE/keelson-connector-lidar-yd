# Keelson Connector Lidar YD

YD Lidar connector to Keelson. Publishing point clouds to the keelson network.  

**OBS! To run the scipt on other systems then linux-x86 you need to build your own python installable package of ydlindar.**

Supported and tested sensor types:

- G4 (Budrate: 230400 SampleRate: 9/8/4)
  - [Development Manual](https://www.ydlidar.com/Public/upload/files/2022-06-21/YDLIDAR%20G4%20Development%20Manual%20V1.8(220411).pdf)
  - [User Manual](https://www.ydlidar.com/Public/upload/files/2022-06-21/YDLIDAR%20G4%20Lidar%20User%20Manual%20V1.3(220411).pdf)
  - [Data Sheet](https://www.ydlidar.com/Public/upload/files/2022-06-21/YDLIDAR%20G4%20Data%20sheet%20V2.0(220411).pdf)

## Python SDKs used

[YDLidar-SDK](https://github.com/YDLIDAR/YDLidar-SDK/tree/master) Wheel package built from repo


[PyLidar3](https://github.com/lakshmanmallidi/PyLidar3) tested but connection to lidar unreliable.


## Run main.py start script examle

1) Creat an virtual enviroment 
2) Install packages
3) Start main.py with following example argumnents 

```bash
# Simple 
python bin/main.py -r rise -e boatswain --log-level 10 

# Extended settings 
python bin/main.py -r rise -e boatswain --device-port /dev/ttyACM1 --log-level 10 


# Experimental
python bin/main.py -r rise -e boatswain --device-port /dev/ttyACM1 --log-level 10 

```

## Docker compose example 
```Docker
version: '3'
services:

  keelson-connector-lidar-yd:
    image: ghcr.io/mo-rise/keelson-connector-lidar-yd:latest
    container_name: lidar-yd
    restart: unless-stopped
    network_mode: "host"
    privileged: true
    devices:
      - "/dev/ttyACM1:/dev/ttyACM1"
    command: "-r rise -e boatswain --device-port /dev/ttyACM1"
    
```

## Truble shooting / Lessons learned  

```bash
# If you do not have access rights to read devise 
sudo chmod a+rw /dev/ttyACM1
```

