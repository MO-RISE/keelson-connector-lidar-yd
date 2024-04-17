import PyLidar3
import time 

port = "/dev/ttyACM1" 

Obj = PyLidar3.YdLidarG4(port)

if(Obj.Connect()):
    print("DeviceInfo:",Obj.GetDeviceInfo())
    print("HealtStatus:",Obj.GetHealthStatus())
    print("CurrentFrequency:",Obj.GetCurrentFrequency())
    print("CurrentRangingFrequency:",Obj.GetCurrentRangingFrequency())

    gen = Obj.StartScanning()
    t = time.time() # start time 
    
    while (time.time() - t) < 30: #scan for 30 seconds
        print(next(gen)) #  angle(degrees) and distance(millimeters).
        time.sleep(0.5)
    Obj.StopScanning()
    Obj.Disconnect()

else:
    print("Error connecting to device")