import PyLidar3

port = "/dev/ttyACM1" 

Obj = PyLidar3.YdLidarG4(port)  

if(Obj.Connect()):
    Obj.Reset()
    print("Resseted device")
    Obj.Disconnect()

else:
    print("Error connecting to device")
    Obj.Disconnect()