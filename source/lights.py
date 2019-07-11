import RPi.GPIO as GPIO;
import time;

# A class responsible for managing the LEDs connected to the pi, depending
# on the current mode of the dash cam.
#   LED Order of appearance (in arrays):
#     0   yellow LED ("running" indicator)
#     1   red LED ("rolling" indicator)
#     2   blue LED (not sure yet)
class LightManager:
    
    # LightManager properties:
    #   pins    An array containing the numbers of the GPIO pins used as output
    #           pins for the LEDs
    #   states  An array containing GPIO.HIGHs and GPIO.LOWs, indicating which
    #           of the LEDs are on, and which are off, at any given time
    
    # Constructor: sets up the GPIO pins
    def __init__(self):
        # set up pin numbers and initial states
        self.pins = [18, 24, 27];
        self.states = [GPIO.HIGH, GPIO.LOW, GPIO.LOW];
        
        # set up GPIO layout/settings
        GPIO.setmode(GPIO.BCM);
        GPIO.setwarnings(False);
        
        # set up the GPIO pins to be output pins, and toggle each pin
        for i in range(0, len(self.pins)):
            GPIO.setup(self.pins[i], GPIO.OUT);
            self.setLED(i, self.states[i] == GPIO.HIGH);

    
    # Destructor: resets the GPIO pins
    def __del__(self):
        # clean up
        GPIO.cleanup();
    
    
    # ---------------------------- LED Managing ----------------------------- #
    # Function that sets the LED at the given index to the given state
    # (state = True (ON), or False (OFF))
    def setLED(self, index, state):
        # make sure the index is within bounds
        if (index > -1 and index < len(self.pins)):
            # translate the state to GPIO-terms
            if (state): state = GPIO.HIGH;
            else: state = GPIO.LOW;
            
            # update the LED's state
            self.states[index] = state;
            # toggle the GPIO pin
            GPIO.output(self.pins[index], state);
    
    
    # Returns a true or false for the given LED index, indicating if the LED
    # is ON or not.
    def getLED(self, index):
        # make sure the index is within bounds
        if (index > -1 and index < len(self.pins)):
            return self.states[index] == GPIO.HIGH;
        return false;
    
    
    # Given the index of the LED to flash, and the number of flashes to
    # perform, this flashes the LED, using time.sleep() to separate
    # the LED toggles
    def flashLED(self, index, flashes):
        for i in range(0, (flashes * 2) - 1):
            time.sleep(0.075);
            self.setLED(index, not self.getLED(index));
