import PyLidar3

port = "/dev/ttyACM1" 

Obj = PyLidar3.YdLidarG4(port) #PyLidar3.your_version_of_lidar(port,chunk_size   

if(Obj.Connect()):
    Obj.Reset()
    print("Resseted device")
    Obj.Disconnect()

else:
    print("Error connecting to device")
    Obj.Disconnect()