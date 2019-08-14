# Test program for the Raspberry Pi Camera Module v2
# Video used to learn: "Raspberry Pi Tutorial 12 - Take a Picture with Python"
#                      by Alexander Baran-Harper

import picamera;
from time import sleep;
import os;

print("Testing file removal...");
path = "/home/pi/coding/python/dash/media/passive/";
f = os.listdir(path);
for file in f:
    t = os.path.getmtime(path + file);
    print(str(file) + " last modified: " + str(t));
print(f);
print("Done testing file removal.");
sleep(5);

cam = picamera.PiCamera();
cam.capture("testImage1.jpg");
sleep(1);
print("Closing open camera...");
cam.close();

# set up the camera (avoid stealing control over the camera from another
# script that might be using it)
with picamera.PiCamera() as camera:
    # set resolution
    print("Setting resolution...");
    camera.resolution = (1600, 900);
    
    # take a picture
    print("Capturing image...");
    camera.capture("scriptImage1.jpg");
    
    # take a video
    print("Taking a video...");
    camera.start_recording("scriptVideo1.h264");
    sleep(5);
    camera.stop_recording();