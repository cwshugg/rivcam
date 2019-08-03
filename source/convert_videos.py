# A script that converts all .h264 video files in both the passive and active
# video directories for the dash cam

import os;
from lights import LightManager;

# check for 'gpac' installed (this has MP4Box)
status = os.system("dpkg --get-selections | grep gpac");
if (status != 0):
    # install gpac
    print("gpac is not installed. Installing now.");
    os.system("sudo apt-get install gpac");

# create light manager
lm = LightManager();
lm.setLED([1, 2], True);

directories = ["../media/passive", "../media/active"];
# iterate through the two video directories
for i in range(0, len(directories)):
    # list the files in the directory
    files = os.listdir(directories[i]);
    # walk through every file
    for j in range(0, len(files)):
        # if the file is a .h264 file, convert it to MP4
        if (".h264" in files[j]):
            # convert using MP4Box
            os.system("MP4Box -add " + directories[i] + "/" + files[j] + " " +
                      directories[i] + "/" + files[j].replace(".h264", ".mp4"));
            # remove the old .h264 file
            os.system("rm " + directories[i] + "/" + files[j]);
            # flash LED to show a video was converted
            lm.flashLED([1, 2], 3);

