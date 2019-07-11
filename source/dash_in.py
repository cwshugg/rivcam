# A class responsible for watching for button presses by the user and reporting
# them to the Controller when asked.
class DashInput:
    
    # InManager properties:
    #   TODO                   (once I get some actual buttons to use)
        
    

    # ------------------ Button-checking Functions ----------------- #
    # Checks for various GPIO buttons being pressed, and returns an integer
    # indicating which button was pressed at the moment it was checked.
    # The integers are as follows:
    #  -1   Nothing was pressed
    #   0   The power button was pressed
    #   1   The "take picture" button was pressed
    #   2   The "active record" button was pressed
    #   3   The "sentry mode" button was pressed
    @staticmethod
    def checkButtons():
        key = input("Input a key: ");
        # check for button presses        (DEBUGGING: currently key presses instead)
        if (key == 0):    # power button
            return 0;
        if (key == 1):    # picture button
            return 1;
        if (key == 2):    # record button
            return 2
        if (key == 3):    # sentry button
            return 3;
        
        # if the function made it this far, then nothing was pressed
        return -1;



