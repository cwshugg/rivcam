import os;
import shutil;

# A class responsible for looking for a flash drive on the system, and
# "dumping" the dash cam's files onto it, either immediately when the flash
# drive is plugged in, or periodically, with the flash drive plugged in
class Dumper:
    
    # Dumper properties:
    #   dumpDirectories    A list of paths pointing to directories to be dumped
    #                      to a plugged-in flash drive
    #   driveName          The name of the flash drive to search for
    #   drivePath          The full path of the flash drive in the system
    #   saveDirectory      The name of the directory the files will be copied
    #                      to on the flash drive
    
    # Constructor: sets up the name of the flash drive to dump to
    def __init__(self, name):
        # set up the name/path
        self.setDriveName(name);
        
        # set up directories to dump
        homePath = os.getcwd() + "/";
        self.dumpDirectories = [homePath + "logs", homePath + "media"];


    # ---------------------- Set-up Functions ---------------------- #
    # Modifies the Dumper's driveName and full drivePath to match the drive
    # with the given name.
    def setDriveName(self, name):
        self.driveName = name;
        self.drivePath = "/media/pi/" + name + "/";
        self.saveDirectory = "dashcam";
    
    
    # -------------------- Flash-Drive Detection ------------------- #
    # Function that checks if the flash drive by the object's name is plugged
    # in. Returns a boolean accordingly
    def driveExists(self):
        return os.path.exists(self.drivePath);
    
    
    # --------------------- Flash-Drive Dumping -------------------- #
    # Function that, assuming the target drive is plugged into the computer,
    # dumps every directory in self.dumpDirectories to the flash drive in a
    # new folder (or the same folder if it already exists). A filer is passed
    # as a parameter so that any errors can be logged
    def dumpToDrive(self, filer):
        # if the directory to save to exists, remove it to make room
        if (os.path.exists(self.drivePath + self.saveDirectory)):
            filer.log("  Removing old directory...");
            os.system("rm -rf " + self.drivePath + self.saveDirectory);        
        
        # walk through the dump directories
        for i in range(0, len(self.dumpDirectories)):
            # get the name of the current dump directory
            dName = self.dumpDirectories[i].split("/");
            dName = dName[len(dName) - 1];
            copyPath = self.drivePath + self.saveDirectory + "/" + dName;
            
            # attempt to copy files
            try:
                # copy over the contents of the dump directory and log it
                shutil.copytree(self.dumpDirectories[i], copyPath);
                filer.log("  Dumping " + dName + "...");
            # catch exceptions
            except shutil.Error as e:
                filer.log("  Directory: '" + self.dumpDirectories[i] +
                          "' not copied due to shutil error: " + str(e));
            except OSError as e:
                filer.log("  Directory: '" + self.dumpDirectories[i] +
                          "' not copied due to OS error: " + str(e));

        