import PyLidar3

port = "/dev/ttyACM1" 

Obj = PyLidar3.YdLidarX4(port) #PyLidar3.your_version_of_lidar(port,chunk_size   

if(Obj.Connect()):
    print(Obj.GetDeviceInfo())
    print(Obj.GetCurrentFrequency())
    Obj.IncreaseCurrentFrequency(PyLidar3.FrequencyStep.oneTenthHertz)
    print(Obj.GetCurrentFrequency())
    Obj.DecreaseCurrentFrequency(PyLidar3.FrequencyStep.oneHertz)
    print(Obj.GetCurrentFrequency())
    Obj.Disconnect()
else:
    print("Error connecting to device")