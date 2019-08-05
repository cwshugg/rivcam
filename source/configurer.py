import os;
import datetime;
from time import sleep;
from filer import Filer;
from dumper import Dumper;
from lights import LightManager;
from buttons import ButtonManager;
from controller import Controller;
from shutdown import shutdown_pi;

# A class that launches a "set-up" mode for the dash cam, before actually
# starting with the passive recording. Allows the users to package and send
# output, as well as connect to new WiFi networks
class Configurer:
    
    # Configurer Properties:
    #   filer       The Filer object used to write logs/package output
    #   lights      The LightManager used for toggling LEDs
    #   buttons     The ButtonManager used for user input
    #   dumper      The Dumper object used to dump files to a flash drive
    
    # Configurer Constants:
    #   TICK_RATE   The time interval (in seconds) at which the configurer
    #               ticks to check for/make updates
    #   WAIT_TIME   The time the Configurer waits before automatically going
    #               into dash-cam mode (this is in seconds)
    
    # Constructor
    def __init__(self):
        # create the filer, light manager, button manager, and dumper
        self.filer = Filer();
        self.lights = LightManager();
        self.buttons = ButtonManager();
        self.dumper = Dumper("dashdrive");

        # create constants
        self.TICK_RATE = 0.125;
        self.WAIT_TIME = 5.0;

        # log a new config session
        self.filer.log("---------- New Config Session: " + str(datetime.datetime.now())
                               + " ----------\n", True);
    

    # Main function
    def main(self):
        # set up loop variables
        ticks = 0.0;
        tickSeconds = 0.0;
        
        # the terminate codes are as follows:
        #   -1      Don't terminate
        #    0      Terminate and launch dash cam
        #    1      Terminate and shut down
        terminateCode = -1;
        
        self.filer.log("Configuration mode...\n");

        # main loop
        while (terminateCode < 0):
            # slowly flash the yellow light (twice every second)
            self.lights.setLED([0], tickSeconds.is_integer() or
                               (tickSeconds + 0.5).is_integer());
            
            tickString = "[Ticks: {t1:9.2f}]  [Running Time: {t2:9.2f}]";
            tickString = tickString.format(t1 = ticks, t2 = int(tickSeconds));
            tickString = "[config]  " + tickString;

            # if the WAIT_TIME has been exceeded, terminate with code 0
            if (tickSeconds == self.WAIT_TIME):
                tickString += "  (Wait time exceeded: terminating configuration and launching dash cam...)";
                terminateCode = 0;
            
            # check for user input (red/yellow hold: shut down)
            if (self.buttons.isPowerPressed() and self.buttons.durations[0] * self.TICK_RATE >= 2.0 and
                self.buttons.isCapturePressed() and self.buttons.durations[1] * self.TICK_RATE >= 2.0):
                self.filer.log("Red/Yellow buttons held. Shutting down...");
                # create a controller and use its shutdown sequence
                shutdown_pi(self.lights, [self.buttons]);
            # check for user input (output config)
            elif (self.buttons.isCapturePressed() and self.buttons.durations[1] * self.TICK_RATE < 1.0 and
                  self.buttons.durations[1] * self.TICK_RATE >= 0.25 and not self.buttons.isPowerPressed()):
                self.filer.log("Entering output config...\n");
                # disable yellow LED
                self.lights.setLED([0], False);
                self.mainOutput();
                
                # reset button durations (so shutdown doesn't trigger)
                self.buttons.durations = [0, 0];
                # reset the ticks/tickSeconds
                ticks = 0.0;
                tickSeconds = 0.0;
                # flash yellow LED to indicate mode switch
                self.lights.flashLED([0], 2);
            # check for user input (connect config)
            elif (self.buttons.isPowerPressed() and self.buttons.durations[0] * self.TICK_RATE < 1.0 and
                  self.buttons.durations[0] * self.TICK_RATE >= 0.25 and not self.buttons.isCapturePressed()):
                self.filer.log("Entering connect config...\n");
                # disable yellow LED
                self.lights.setLED([0], False);
                self.mainConnect();

                # reset button durations (so shutdown doesn't trigger)
                self.buttons.durations = [0, 0];
                # reset the ticks/tickSeconds
                ticks = 0.0;
                tickSeconds = 0.0;
                # flash yellow LED to indicate mode switch
                self.lights.flashLED([0], 2);

            # only log the tickString if the ticks are currently on a second
            if (tickSeconds.is_integer()):
                self.filer.log(tickString + "\n");

            # update the ticks
            ticks += 1;
            tickSeconds += self.TICK_RATE;
            # sleep for one TICK_RATE
            sleep(self.TICK_RATE);
        
        # the loop was terminated: determine why
        if (terminateCode == 0):
            # force GPIO-using classes to clean up
            self.lights.__del__();
            self.buttons.__del__();

            self.filer.log("--------- Config Session Ended: " + str(datetime.datetime.now())
                                           + " ---------\n\n", True);
            # create a controller to launch the dash cam
            cont = Controller();
            cont.main();


    # Output Mode main function
    def mainOutput(self):
        # set up loop variables
        ticks = 0.0;
        tickSeconds = 0.0;
        # terminate codes are as follows:
        #   -1      Don't terminate
        #    0      Terminate and return to config
        terminateCode = -1;
        
        # main loop
        while (terminateCode < 0):
            # slowly flash the red/blue lights (twice every second)
            self.lights.setLED([1, 2], tickSeconds.is_integer() or
                               (tickSeconds + 0.5).is_integer());
            
            # create a tick string
            tickString = "[Ticks: {t1:9.2f}]  [Running Time: {t2:9.2f}]";
            tickString = tickString.format(t1 = ticks, t2 = int(tickSeconds));
            tickString = "[config-output]  " + tickString;
            
            # get button durations before updating them
            captureDuration = self.buttons.durations[1];
            powerDuration = self.buttons.durations[0];

            # check for red/yellow button hold (back to config)
            if (self.buttons.isCapturePressed() and self.buttons.durations[1] * self.TICK_RATE >= 2.0
            and self.buttons.isPowerPressed() and self.buttons.durations[0] * self.TICK_RATE >= 2.0):
                tickString += "  (Capture/Power buttons were held)";
                terminateCode = 0;
            # check for red button (package output)
            elif (not self.buttons.isCapturePressed() and not self.buttons.isPowerPressed() and
                  captureDuration < ticks and captureDuration > 0.0):
                # do different actions depending on the hold-length
                if (captureDuration * self.TICK_RATE < 1.5):
                    # package output
                    self.filer.packageOutput("output.zip", self.lights);
                else:
                    # disable all lights and toggle the blue light to indicate "thinking"
                    self.lights.setLED([0, 1, 2], False);
                    # dump output to flash drive, if it's plugged in
                    if (self.dumper.driveExists()):
                        self.filer.log("Drive found. Dumping files...\n");
                        self.lights.setLED([2], True);
                        # dump files
                        self.dumper.dumpToDrive(self.filer);
                        # flash the blue/red lights to show success
                        self.lights.setLED([1, 2], False);
                        self.lights.flashLED([1, 2], 3);
                    else:
                        self.filer.log("Drive not found. Cannot dump files.\n");
                        # flash the red light to show failure
                        self.lights.flashLED([1], 3);                    
            # check for yellow button (convert videos)
            elif (self.buttons.isPowerPressed() and self.buttons.durations[0] * self.TICK_RATE < 1.0 and
                  self.buttons.durations[0] < ticks and not self.buttons.isCapturePressed()):
                # convert videos to mp4
                self.filer.convertVideos(self.lights);
            

            # log tick string if the tick is on a second
            if (tickSeconds.is_integer()):
                self.filer.log(tickString + "\n");

            # update ticks
            ticks += 1;
            tickSeconds += self.TICK_RATE;
            # sleep for one TICK_RATE
            sleep(self.TICK_RATE);
        
        # print termination message
        if (terminateCode == 0):
            self.filer.log("Returning to config...\n");
            # disable blue/red LEDs
            self.lights.setLED([1, 2], False);


    # Connect Mode main function
    def mainConnect(self):
        # set up loop variables
        ticks = 0.0;
        tickSeconds = 0.0;
        # terminate codes are as follows:
        #   -1      Don't terminate
        #    0      Terminate and return to config
        terminateCode = -1;

        # main loop
        while (terminateCode < 0):
            # slowly flash the blue/yellow lights (twice every second)
            self.lights.setLED([0, 2], tickSeconds.is_integer() or
                               (tickSeconds + 0.5).is_integer());

            # create tick string
            tickString = "[Ticks: {t1:9.2f}]  [Running Time: {t2:9.2f}]";
            tickString = tickString.format(t1 = ticks, t2 = int(tickSeconds));
            tickString = "[config-connect]  " + tickString;

            # check for red/yellow button hold (back to config)
            if (self.buttons.isCapturePressed() and self.buttons.durations[1] * self.TICK_RATE >= 1.0
            and self.buttons.isPowerPressed() and self.buttons.durations[0] * self.TICK_RATE >= 1.0):
                tickString += "  (Capture/Power buttons were held)";
                terminateCode = 0;

            # log the tick string if the tickSeconds is on a second
            if (tickSeconds.is_integer()):
                self.filer.log(tickString + "\n");

            # update ticks
            ticks += 1;
            tickSeconds += self.TICK_RATE;
            # sleep for one TICK_RATE
            sleep(self.TICK_RATE);
        
        # print termination message
        if (terminateCode == 0):
            self.filer.log("Returning to config...\n");
            # disable blue/yellow LEDs
            self.lights.setLED([0, 2], False);


# run the configurer
config = Configurer();
config.main();
