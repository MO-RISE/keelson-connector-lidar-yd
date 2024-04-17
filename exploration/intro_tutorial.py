import PyLidar3

port = input("Enter port name which lidar is connected:") #windows

Obj = PyLidar3.YdLidarG4(port)

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