import datetime;
import os;
import time;
from time import sleep;
from dashcam import DashCam;
from filer import Filer;
from lights import LightManager;
from buttons import ButtonManager;
from shutdown import shutdown_pi;

# The main runner class for the program. Handles Camera interaction, file
# saving/deletion, and other input/output
class Controller:
    
    # Controller properties:
    #   camera       The Camera object used to record videos/take pictures
    #   filer        The Filer object responsible for managing system files
    #   lights       The LightManager object used for toggling LEDs
    #   buttons      The ButtonManager used to sense button presses
    
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
        # create a light manager and turn on the power LED
        self.lights = LightManager();
        self.lights.setLED([0], True);
        # create a button manager
        self.buttons = ButtonManager();
        
        
        # create constants
        self.TICK_RATE = 0.125;
        self.PASSIVE_LEN = 10.0 * 60;

        # log that a new session has begun
        self.filer.log("---------- New Session: " + str(datetime.datetime.now())
                       + " ----------\n", True);
        
        
    # Destructor
    def __del__(self):        
        # log that the session has ended
        self.filer.log("--------- Session Ended: " + str(datetime.datetime.now())
                       + " ---------\n\n", True);

    
    # Main process function. Loops indefinitely until the program is terminated
    def main(self):        
        # start passively recording
        self.passiveRecording(1);
        
        # termination code: used to help determine why the main loop
        # was broken (could be the power button, could be too hot
        # of a cpu, etc.)
        #   -1  =  not terminated
        #    0  =  CPU is too hot
        #    1  =  power button was pressed
        #    2  =  debug terminate (exit program but keep pi powered on)
        terminateCode = -1;
        
        # --------------- main loop --------------- #
        ticks = 0.0;
        tickSeconds = 0.0;
        tickPrintRate = 1; # logs the tickString every 'tickPrintRate' seconds
        terminate = False;
        while (not terminate):
            tickOnSecond = tickSeconds.is_integer();
            # write a tick string to be printed to the log
            tickString = "Tick: {t1:9.2f}  |  Running Time: {t2:9.2f}";
            tickString = tickString.format(t1 = ticks, t2 = int(tickSeconds));
            tickHeader = "[dashcam]  ";
            tickHeader += "[LED: " + (str(self.lights.states[0]) +
                                      str(self.lights.states[1]) +
                                      str(self.lights.states[2])) + "]  ";
            tickHeader += "[Button: " + (str(int(self.buttons.durations[0] * self.TICK_RATE)) + "|" +
                                         str(int(self.buttons.durations[1] * self.TICK_RATE)) + "]  ");
            tickString = tickHeader + tickString;
            
            # check the CPU temperature (terminate if needed)
            if (tickOnSecond):
                cpuTemp = self.getCPUTemp();
                terminate = cpuTemp > 80.0;
                # add to the tick string
                tickString += "  [CPU Temp: " + str(cpuTemp) + "]";
                # if the temperature exceeds the threshold, stop the program
                terminate = cpuTemp > 80;
                if (terminate):
                    self.filer.log("CPU running too hot! Shutting down...");
                    terminateCode = 0;
            
            # perform any mode actions needed
            tickString += self.update(ticks, tickSeconds);

            # grab the initial button durations
            powerDuration = self.buttons.durations[0];
            captureDuration = self.buttons.durations[1];
            # call the button-detection methods to update their durations
            self.buttons.isPowerPressed();
            self.buttons.isCapturePressed();

            # check for both buttons being pressed
            if (self.buttons.isPowerPressed() and powerDuration * self.TICK_RATE >= 2.0
            and self.buttons.isCapturePressed() and captureDuration * self.TICK_RATE >= 2.0):
                # terminate and shut down
                terminate = True;
                terminateCode = 1;
            # check for power button press
            elif (self.buttons.isPowerPressed() and powerDuration * self.TICK_RATE >= 2.0 and
              not self.buttons.isCapturePressed()):
                # terminate but don't shut down
                terminate = True;
                terminateCode = 2;
            # check for capture button press (TAKE PICTURE)
            elif (captureDuration * self.TICK_RATE <= 2.0 and
                  captureDuration * self.TICK_RATE > 0.0 and
                  not self.buttons.isCapturePressed()):
                self.filer.log("Capturing image..."); 
                # flash LED and take picture
                self.lights.flashLED([1], 2);
                self.camera.takePicture(Filer.makeFileName(1), self.filer.imagePath);
            
            # update the camera's overlay text
            if (self.camera.currVideo != None):                
                self.camera.updateOverlays(datetime.datetime.now());
                self.camera.currVideo.duration += self.TICK_RATE;
            
            # sleep for one tick rate
            self.camera.picam.wait_recording(self.TICK_RATE);
            # log the tick string
            if (tickSeconds % tickPrintRate == 0):
                self.filer.log(tickString + "\n");
            # increment ticks
            ticks += 1;
            tickSeconds += self.TICK_RATE;
        # ----------------------------------------- #

        self.filer.log("Terminate Code: " + str(terminateCode) + "\n"); 
        # check terminate code: shutdown if needed
        if (terminateCode == 0 or terminateCode == 1):
            self.filer.log("Shutting down...\n");
            shutdown_pi(self.lights, [self.buttons, self]);
        
        if (terminateCode == 2):
            # flash LED to show debug terminate
            self.lights.setLED([0, 1], False);
            self.lights.flashLED([0, 1], 5);
            self.filer.log("Terminating dash cam, but keeping Pi powered on...\n");
    
    
    # ------------------------ Mode Updates ------------------------ #
    # Main update method for whatever mode the dash cam is in. Takes in
    # the main loop's tick and tick-second count. Returns a string to
    # be added to the "tickString" in the main loop to reflect any
    # changes that were made in this function
    def update(self, ticks, tickSeconds):
        stringAddon = "";
        tickOnSecond = tickSeconds.is_integer();
        
        # if the tick is on a second, toggle the "rolling" LED
        if (tickOnSecond):
            self.lights.setLED([1], not self.lights.getLED(1));
            
        # if it's time to save the video, split the recording
        if (tickSeconds % self.PASSIVE_LEN == 0 and ticks > 0):
            self.passiveRecording(0);
            # add to the tick string
            stringAddon += "  (Starting next passive video)";
            # flash LED
            self.lights.flashLED([1], 4);
        
        # return the string to be added to the tickString
        return stringAddon;
    
    
    # -------------------- File Saving/Deleting -------------------- #
    # Deletes the oldest passive recording and begins a new one (or splits one
    # that's already running)
    def passiveRecording(self, isNew):
        # delete the oldest passive recording (if it's not new)
        if (not isNew):
            self.filer.deleteOldestPassive();
        
        # depending on the given input, either START a new video, or STOP the
        # current one and create a new one
        if (isNew):
            self.filer.log("Beginning passive recording...\n");
            self.camera.startVideo(Filer.makeFileName(0), self.filer.passivePath);
        else:
            self.camera.stopVideo();
            self.camera.startVideo(Filer.makeFileName(0), self.filer.passivePath);


    # ---------------------- Helper Functions ---------------------- #
    # Function that finds the cpu's current temperature and returns the value
    # as a double
    def getCPUTemp(self):
        # run the temp check in the command line and parse the output
        tempOutput = os.popen("vcgencmd measure_temp | egrep -o '[0-9]*\.[0-9]*'").readlines();
        return float(tempOutput[0].replace("\n", ""));


