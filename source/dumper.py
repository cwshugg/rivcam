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
        homePath = os.getcwd().replace("/source", "") + "/";
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
        driveInfo = os.popen("sudo blkid").readlines();
        if (len(driveInfo) > 4):
            # make sure '/dev/sd*' exists
            return "/dev/sd" in driveInfo[4];
    
    
    # Function that mounts the sda1/sdb1 flash drive to the correct folder. The
    # filer is used to log the mounting. Returns a boolean indicating mount
    # success
    def mountDrive(self, filer):
        # if the mounting path already exists, delete it
        if (os.path.exists(self.drivePath)):
            os.system("sudo rm -rf " + self.drivePath);
        # create a fresh directory for the mount
        os.system("sudo mkdir " + self.drivePath);
        os.system("sudo mkdir " + self.drivePath + self.saveDirectory);

        # look for '/dev/sd??'
        mountPoint = "sda1";
        driveInfo = os.popen("sudo blkid").readlines();
        if (len(driveInfo) > 4):
            # make sure 'dev/sd??' exists in this line
            if ("/dev/sd" in driveInfo[4]):
                # save the "sd??" value as the mount point
                mountPoint = driveInfo[4].split(":")[0].replace("/dev/", "");

        # mount
        status = os.system("sudo mount -o uid=pi,gid=pi /dev/" + mountPoint +
                           " " + self.drivePath);
        
        # log the status
        if (status == 0):
            filer.log("Mounted drive " + mountPoint + " to " + self.drivePath + "\n");
            return True;
        else:
            filer.log("Mounting unsuccessful.\n");
            return False;
    
    
    # Function that unmounts the flash drive. Uses the filer to log the status
    # of the unmounting
    def unmountDrive(self, filer):
        # umount the drive
        status = os.system("sudo umount " + self.drivePath);
        
        # report unmount to the log
        if (status == 0):
            filer.log("Unmounted drive successfully.\n");
        else:
            filer.log("Unmount unsuccessful.\n");

    
    # --------------------- Flash-Drive Dumping -------------------- #
    # Function that, assuming the target drive is plugged into the computer,
    # dumps every directory in self.dumpDirectories to the flash drive in a
    # new folder (or the same folder if it already exists). A filer is passed
    # as a parameter so that any errors can be logged, and a .zip file can be
    # created if the parameter is given. (If 'zipFirst' is passed in as True,
    # a .zip archive of all the output is first created, then THAT is sent
    # to the flash drive).
    def dumpToDrive(self, filer, zipFirst = False):
        # attempt to mount
        mountSuccess = self.mountDrive(filer);

        # if the directory to save to exists, remove it to make room
        if (os.path.exists(self.drivePath + self.saveDirectory)):
            filer.log("  Removing old directory...");
            os.system("rm -rf " + self.drivePath + self.saveDirectory);        
        
        # if zipFirst is true, zip the files and copy this instead
        if (zipFirst):
            zipName = "output.zip";
            filer.packageOutput(zipName);
            os.system("cp " + filer.path + zipName + self.drivePath +
                      self.saveDirectory + "/" + zipName);
        # otherwise, copy the directories directly
        else:
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

        # unmount the usb drive
        self.unmountDrive(filer);



        
