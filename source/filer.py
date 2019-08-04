import os;
import datetime;
from lights import LightManager;

# A class responsible for managing the files of the dash cam
class Filer:
    
    # Filer properties:
    #   mediaPath    The path to the directory where all media is kept
    #   passivePath  The path to the directory where passive recordings are
    #                stored on the System
    #   activePath   The path to the directory where active recordings are
    #                stored on the System
    #   imagePath    The path to the directory where images are stored    
    #   logPath      The path to the directory where log files are stored
    #   logString    A temporary string holding log information
    #   displayLog   A boolean telling whether or not to print any logged
    #                strings to the terminal
    
    # Filer constants:    
    #   PASSIVE_LIM  The number of video files passive recording will save before
    #                deleting the oldest one once a new one is created
    #   LOG_LIM      The length the filer's logString can be before it's written to
    #                a log file. (Used to minimize file writes)

    # Constructor
    def __init__(self):
        # create file paths
        path = "/home/pi/coding/python/dash/";
        self.path = path;
        self.mediaPath = path + "media/";
        self.passivePath = self.mediaPath + "passive/";
        self.activePath = self.mediaPath + "active/";
        self.imagePath = self.mediaPath + "images/";      
        self.logPath = path + "logs/";
        
        # set up log info
        self.logString = "";
        self.displayLog = True;
        
        # create constants        
        self.PASSIVE_LIM = 18;
        self.LOG_LIM = 512;
        
        # check all directories
        self.checkDirectories();


    # -------------------------- Helper Functions --------------------------- #
    # Checks the controller's various directories, and creates them if they don't
    # exist in the current directory
    def checkDirectories(self):
        # if any of the directories don't exist, create them
        if (not os.path.exists(self.mediaPath)):
            os.mkdir(self.mediaPath);
        if (not os.path.exists(self.passivePath)):
            os.mkdir(self.passivePath);
        if (not os.path.exists(self.activePath)):
            os.mkdir(self.activePath);
        if (not os.path.exists(self.imagePath)):
            os.mkdir(self.imagePath);
        if (not os.path.exists(self.logPath)):
            os.mkdir(self.logPath);
    
    
    # Function that uses the current date-time to generate a name for either a
    # video or an image that will be recorded/captured. The input parameter,
    # "fileType" should be given in the following format:
    #     0    A video file name
    #     1    An image file name
    #     2    A log file name
    #     3    A set-up log file name (used by the Configurer)
    @staticmethod
    def makeFileName(fileType):
        now = datetime.datetime.now();
        name = str(now);
        name = name[:(str.find(name, ".") + 2)];
        # replace any spaces with underscores, and periods/colons with dashes
        name = name.replace(" ", "_");
        name = name.replace(":", "-");
        name = name.replace(".", "-");
        
        # add an appropriate prefix and suffix
        if (fileType == 0):
            name = "vid_" + name;
        elif (fileType == 1):
            name = "img_" + name;
        elif (fileType == 2):
            name = "log_" + str(now.year) + "-" + str(now.month) + "-" + str(now.day);
        elif (fileType == 3):
            name = "config_" + str(now.year) + "-" + str(now.month) + "-" + str(now.day);
        
        # return the name of the file
        return name;
    

    # ----------------------- Passive-Recording Files ----------------------- #
    # Deletes the oldest passive recording from memory to make room for the next
    def deleteOldestPassive(self):
        # get the list of files in the passive directory
        files = os.listdir(self.passivePath);        
        
        # determine if one should be deleted yet
        if (len(files) >= self.PASSIVE_LIM and len(files) > 0):
            remIndex = 0; # the index to remove
            minTime = os.path.getmtime(self.passivePath + files[0]);
            
            # find the file with the earliest creation time
            for i in range(0, len(files)):                
                t = os.path.getmtime(self.passivePath + files[i]);                
                # update the minimum time/remove index
                if (os.path.isfile(self.passivePath + files[i])
                    and "vid" in files[i] and t < minTime):
                    # update the removal index and the minimum time
                    remIndex = i;
                    minTime = t;        
            
            # remove the oldest file from the directory
            os.remove(self.passivePath + files[remIndex]);
            self.log("Removing Oldest Passive Recording: " + files[i] + "\n");
    

    # -------------------- Compression/Conversion Functions ----------------- #
    # Helper function that creates a .zip file containing all the current .h264,
    # .mp4, .png, and log .txt files into a zip file at the given path. A light
    # manager is passed in to have indicator lights display packaging progress
    def packageOutput(self, zipName, lights):
        # hold the blue LED to show things are processing
        lights.setLED([0, 1, 2], False);
        lights.setLED([2], True);
        
        # remove the old .zip, if one exists
        os.system("rm " + zipName);
        # use system commands to package all files into a .zip file
        os.system("zip " + self.path + zipName + " " + self.mediaPath + "*/* " + self.logPath + "*");

        # flash the blue and red LEDs to show the zip file was created
        lights.flashLED([1, 2], 3);
        lights.setLED([1, 2], False);


    # Function that converts all .h264 videos to .mp4 files, then deletes the
    # .h264 files. Places the .mp4's in the same location as the .h264's
    def convertVideos(self, lights):
        # check to make sure 'gpac' is installed (this has MP4Box)
        status = os.system("dpkg --get-selections | grep gpac");
        if (status != 0):
            os.system("sudo apt-get install gpac");

        # turn the blue light on to indicate the pi is busy converting
        lights.setLED([2], True);

        directories = [self.passivePath, self.activePath];
        # iterate through each of the two video directories
        for i in range(0, len(directories)):
            # get a list of the files in the directory
            files = os.listdir(directories[i]);

            # iterate through each file in the directory
            for j in range(0, len(files)):
                # if the file is a .h264 file, convert it to .mp4
                if (".h264" in files[j]):
                    os.system("MP4Box -add " + directories[i] + files[j] + " " +
                              directories[i] + files[j].replace(".h264", ".mp4"));
                    # flash the blue LED once to indicate a video was processed
                    lights.flashLED([2], 1);
                    # remove the .h264 video
                    os.system("sudo rm " + files[j]);

        # flash the blue and red LEDs to show the convertions are complete
        lights.setLED([1, 2], False);
        lights.flashLED([1, 2], 3);

    
    
    # -------------------------- Logging Functions -------------------------- #
    # Takes the given string and "logs" it. Usually, this means appending it to
    # the end of the filer's logString. If the "forceWrite" parameter is True,
    # then whatever is in the logString will immediately be written to the file.
    def log(self, text, forceWrite = False):
        self.logString += text;
        
        # if display is true, print to console
        if (self.displayLog):
            print(text.replace("\n", ""));

        # determine what kind of log file this is
        logType = 2;
        if ("config" in self.logString.lower()):
            logType = 3;
        
        # if the log string has exceeded its length, write it to the log file
        if (len(self.logString) >= self.LOG_LIM or forceWrite):
            # make a file name and open it for writing
            fname = Filer.makeFileName(logType);
            f = open(self.logPath + fname + ".txt", "a+");
            
            # write the text and close the file
            f.write(self.logString);
            f.close();
            
            # reset the log string
            self.logString = "";


