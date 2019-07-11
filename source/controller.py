import datetime;
import os;
import time;
from time import sleep;
from dashcam import DashCam;
from filer import Filer;
from dash_in import DashInput;
from dumper import Dumper;
from lights import LightManager;

# The main runner class for the program. Handles Camera interaction, file
# saving/deletion, and other input/output
class Controller:
    
    # Controller properties:
    #   camera       The Camera object used to record videos/take pictures
    #   filer        The Filer object responsible for managing system files
    #   dumper       The Dumper object used to dump files onto a flash drive
    #   lights       The LightManager object used for toggling LEDs
    #   mode         An integer representing what "mode" the dash cam is in.
    #                Used to determine what action to take in the main loop.
    #                   0   Passive Record
    #                   1   Active Record
    
    # Controller constants:
    #   TICK_RATE    The time interval (in seconds) at which the system ticks
    #                to check for/make updates
    #   PASSIVE_LEN  The length (in seconds) of the dash cam's passive videos
    
    # Constructor
    def __init__(self):
        # create a camera
        self.camera = DashCam();
        # create a Filer
        self.filer = Filer();
        # create a filer dumper
        self.dumper = Dumper("DASHCAM");
        # create a light manager
        self.lights = LightManager();
        
        # create constants
        self.TICK_RATE = 0.25;
        self.PASSIVE_LEN = 10.0 * 60;
        
        # by default, the mode is 0: passive record
        self.mode = 0;

        # log that a new session has begun
        self.filer.log("---------- New Session: " + str(datetime.datetime.now())
                       + " ----------\n", True);
        
        
    # Destructor
    def __del__(self):
        # make one last flash-drive dump, if possible
        if (self.dumper.driveExists()):
            self.dumpFiles();
        
        # log that the session has ended
        self.filer.log("--------- Session Ended: " + str(datetime.datetime.now())
                       + " ---------\n\n", True);

    
    # Main process function. Loops indefinitely until the program is terminated
    def main(self):        
        # start passively recording
        self.passiveRecording(1);
        
        # variables for keeping track of flash drive
        driveInLastTick = False;
        
        # termination code: used to help determine why the main loop
        # was broken (could be the power button, could be too hot
        # of a cpu, etc.)
        #   -1  =  not terminated
        #    0  =  CPU is too hot
        #    1  =  power button was pressed
        terminateCode = -1;
        
        # --------------- main loop --------------- #
        ticks = 0.0;
        tickSeconds = 0.0;
        terminate = False;
        while (not terminate):
            tickOnSecond = tickSeconds.is_integer();
            # write a tick string to be printed to the log
            tickString = "Tick: {t1:9.2f}  |  Running Time: {t2:9.2f}";
            tickString = tickString.format(t1 = ticks, t2 = int(tickSeconds));
            tickString = "[M" + str(self.mode) + "] " + tickString;            
            
            # check the CPU temperature (terminate if needed)
            if (tickOnSecond):
                cpuTemp = self.getCPUTemp();
                terminate = cpuTemp > 80.0;
                # add to the tick string
                tickString += "  (CPU Temp: " + str(cpuTemp) + ")";
                # if the temperature exceeds the threshold, stop the program
                terminate = cpuTemp > 80;
                if (terminate):
                    tickString += " (Too hot! Shutting down...)";
                    terminateCode = 0;
            
            # perform any mode actions needed
            tickString += self.update(ticks, tickSeconds);
            
            # check for button presses
            btn = -1;#DashInput.checkButtons();
            if (btn == 0):
                tickString += "  (Power button was pressed)";
            elif (btn == 1):
                tickString += "  (Image Capture button was pressed)";
            elif (btn == 2):
                tickString += "  (Active Record button was pressed)";
            elif (btn == 3):
                tickString += "  (Sentry Mode button was pressed)";
            
            # update the camera's overlay text
            if (self.camera.currVideo != None):                
                self.camera.updateOverlays(datetime.datetime.now());
                self.camera.currVideo.duration += self.TICK_RATE;
            
            # sleep for one tick rate
            self.camera.picam.wait_recording(self.TICK_RATE);            
            # increment ticks            
            ticks += 1;
            tickSeconds += self.TICK_RATE;            
            # log the tick string
            self.filer.log(tickString + "\n");
            
            # check for flash-drive being plugged in
            driveJustIn = self.dumper.driveExists() and not driveInLastTick;
            if (driveJustIn):
                self.dumpFiles();            
            # update variable used for current-tick drive-in detection
            driveInLastTick = self.dumper.driveExists();
        # ----------------------------------------- #
        
        # check terminate code: shutdown if needed
        if (terminateCode == 0 or terminateCode == 1):
            self.shutdownPi();
    
    
    # ------------------------ Mode Updates ------------------------ #
    # Main update method for whatever mode the dash cam is in. Takes in
    # the main loop's tick and tick-second count. Returns a string to
    # be added to the "tickString" in the main loop to reflect any
    # changes that were made in this function
    def update(self, ticks, tickSeconds):
        stringAddon = "";
        tickOnSecond = tickSeconds.is_integer();
        
        # PASSIVE RECORD
        if (self.mode == 0):
            # if the tick is on a second, toggle the "rolling" LED
            if (tickOnSecond):
                self.lights.setLED(1, not self.lights.getLED(1));
            
            # if it's time to save the video, split the recording
            if (tickSeconds % self.PASSIVE_LEN == 0 and ticks > 0):
                self.passiveRecording(0);
                # add to the tick string
                stringAddon += "  (Starting next passive video)";
                # flash LED
                self.lights.flashLED(1, 3);
                
        
        # ACTIVE RECORD
        if (self.mode == 1):
            # toggle the RED led to be solid red (only do this once)
            if (not self.lights.getLED(1)):
                self.lights.setLED(1, True);
        
        # return the string to be added to the tickString
        return stringAddon;
    
    
    # -------------------- File Saving/Deleting -------------------- #
    # Helper function that's called whenever a dump to a flash drive is made
    # by the controller. Adds a note to the log and invokes the Dumper's
    # "dumpToDrive" method
    def dumpFiles(self):
        self.filer.log("Drive: " + self.dumper.driveName + " inserted. Dumping...");
        self.dumper.dumpToDrive(self.filer);
    

    # Deletes the oldest passive recording and begins a new one (or splits one
    # that's already running)
    def passiveRecording(self, isNew):
        # delete the oldest passive recording
        self.filer.deleteOldestPassive();
        
        # depending on the given input, either START a new video, or split it
        if (isNew):
            self.filer.log("Beginning passive recording...\n");
            self.camera.startVideo(Filer.makeFileName(0), self.filer.passivePath);
        else:            
            self.camera.splitVideo(Filer.makeFileName(0));


    # ---------------------- Helper Functions ---------------------- #
    # Function that finds the cpu's current temperature and returns the value
    # as a double
    def getCPUTemp(self):
        # run the temp check in the command line and parse the output
        tempOutput = os.popen("vcgencmd measure_temp | egrep -o '[0-9]*\.[0-9]*'").readlines();
        return float(tempOutput[0].replace("\n", ""));
    
    
    # Ends the process, gives up the camera, and shuts down the pi
    def shutdownPi(self):
        # call destructor
        self.__del__();
        # shutdown the pi
        os.system("shutdown -h now");


# running the program
cont = Controller();
cont.main();
