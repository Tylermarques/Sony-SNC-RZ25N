# SONY SNC-RZ25N

## Setting up communication

First thing on the list of TODOs was figure out how the hell I get an image out of it. The camera has 4 interfaces on the back of it.
VCC and Ground are pretty self-explanatory, the camera appears to run on some form of electricity. There is also ethernet and what looks like 
a coax cable but without the threaded part. Given that I have never used coax, have none on hand, and no way to get that signal into my computer, I opted to fight with 
the networking settings.

I tried connecting the cameras directly to my router and seeing if any new devices showed up and thankfully it did. It however was on the wrong subnet 
so I couldn't reach it from any of my other devices. I found a manual on [manualslib.com](https://www.manualslib.com/manual/325135/Sony-Ipela-Snc-Rz25n.html#product-SNC-RZ25N%20-%20Network%20Camera)
that said that the camera can have all of its settings (including IP and subnet) changed from its web interface. Super useful when you can't reach the web interface. 
What I was unaware of at the time was that you can connect two devices directly via an ethernet connection and set the subnet manually. This allows the 
devices to communicate. I tried first on my Mac, only to be met with disappointment when the interface that loaded up was Flash based, meaning that it would not load
on Chrome. Deciding to turn my back on modern technology, I fired up my older Windows machine and launched IE. After reconnecting and reconfiguring the ethernet interface,
I could load the interface without issue. I finally could set the IP to be in the right subnet and properly communicate with the camera.

## Controlling the cameras

In the web interface, there was some basic configuration options. What I was mostly interested in was the Live View which
allowed you to view the camera's feed and direct the camera to reposition. I opened wireshark and captured the packets being sent to the camera
from IE. This let me find the endpoints, as well as the data needed to send to them in order to command movement. I had some issues
with the schema for sending the position changes, as they are in a pattern I don't recognize. 
```text
curl -X POST http://.../command/ptzf.cgi --user user:password -H Content-Type=application/x-www-form-urlencoded --data AbsolutePanTilt=0000,0000,0
```
It looks like the `AbsoutlePanTilt` key took a value of two bytes for each Pan and Tilt option. That is a total of 4 bytes in hex. I was still unclear on what the last
digit did. The scale for the camera also seems odd. The 0000 point for Pan is center between either end of its rotation, with Tilt 
0000 being horizon level. See below for my crude attempts at drawing anything useful.
![Camera Movement Range](https://github.com/Tylermarques/Sony-SNC-RZ25N/images/Camera_movement.png)

## TODOs
- What does the last digit on AbsolutePanTilt zoom do?

