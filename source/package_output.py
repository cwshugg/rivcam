# A script for the dash camera used to package up all the video, image, and log
# files into a .zip file

import os;
from lights import LightManager;

# create a light manager
lights = LightManager();
lights.setLED([2], True);

# remove the old output.zip
os.system("rm ../output.zip");
# use system commands to package all files into a .zip file
os.system("zip ../output.zip ../media/*/* ../logs/*");

# flash the blue light to indicate the zip file was created
lights.flashLED([2], 3);
lights.setLED([2], False);
