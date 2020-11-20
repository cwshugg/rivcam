from lights import LightManager;
import os;

# A function that takes in an array of objects, forcefully calls their
# destructors, then shuts down the Raspberry Pi. It's also passed a
# LightManager object, which is used to flash lights. This also has
# its destructor called, so the GPIO pins are cleaned up
def shutdown_pi(lights, objects):
    # flash LEDs
    lights.setLED([0, 1, 2], False);
    for i in range(0, 3):
        lights.flashLED([i], 1);
    lights.flashLED([0, 1, 2], 1);

    # call each object's destructor
    lights.__del__();
    for obj in objects:
        obj.__del__();
    
    # shut down the pi
    os.system("sudo shutdown -h now");

