import PyLidar3

port = "/dev/ttyACM1" 

Obj = PyLidar3.YdLidarX4(port) #PyLidar3.your_version_of_lidar(port,chunk_size   

if(Obj.Connect()):
    Obj.Reset()

    print("Resseted device")