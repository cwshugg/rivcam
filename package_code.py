# A script for the dash camera used to package up all the .py files into a .zip
# file

import os;
from lights import LightManager;

# create a light manager
lights = LightManager();
lights.setLED([2], True);

# use system commands to package all files into a .zip file
os.system("zip ../code.zip ./*.py");

# flash the blue light to indicate the zip file was created
lights.flashLED([2], 5);
lights.setLED([2], False);
