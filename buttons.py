import RPi.GPIO as GPIO;

# A class responsible for watching for button presses by the user and reporting
# them to the Controller when asked.
class ButtonManager:
    
    # ButtonManager properties:
    #   pins       An array holding the GPIO input pins of the buttons. The pins
    #              come in the order of these buttons: "power", "capture"        
    #   durations  The current number of consecutive times each button has been
    #              held down (useful for click/hold button actions)
    
    # Constructor: set up the pins as input pins
    def __init__(self):
        # set up the pins
        self.pins = [16, 5];
        self.durations = [0, 0];

        # set up GPIO pin layout/settings
        GPIO.setmode(GPIO.BCM);
        GPIO.setwarnings(False);

        # set up each GPIO pin to be input pins
        for i in range(0, len(self.pins)):
            GPIO.setup(self.pins[i], GPIO.IN);
    
    
    # Destructor: resets the GPIO pins
    def __del__(self):
        # clean up pins
        GPIO.cleanup();

    
    # ------------------ Button-checking Functions ----------------- #
    # Determines if the power button is pressed, and returns a boolean value
    # accordingly
    def isPowerPressed(self):
        buttonDown = not GPIO.input(self.pins[0]);
        # increment the power button's duration
        self.durations[0] = int(buttonDown) * (self.durations[0] + 1);
        return buttonDown;
    

    # Determines if the capture button is pressed, and returns a boolean value
    # accordingly
    def isCapturePressed(self):
        buttonDown = not GPIO.input(self.pins[1]);
        # increment the capture button's duration
        self.durations[1] = int(buttonDown) * (self.durations[1] + 1);
        return buttonDown;
    

