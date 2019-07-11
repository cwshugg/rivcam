# A class that represents a Video object. Contains the various properties needed
# to identify where the video is, what it's called, and its duration.
class Video:
    
    # Video Properties:
    #   fileName    The name of the video file
    #   filePath    The location of the video file's directory
    #   duration    The length of the video (in seconds)
    
    # Constructor with optional file name + path arguments
    def __init__(self, name = "", path = ""):
        self.fileName = name + ".h264";
        self.filePath = path;
        self.duration = 0.0;
    

    # --------------------- Setter Functions ---------------------- #
    # Function that takes in the new file name and attaches the correct file
    # extension to the end of the string
    def setFileName(self, newName):
        self.fileName = newName + ".h264";
        

    # --------------------- Helper Functions ---------------------- #
    # Takes the video's file name and file path, and concatenates them together to
    # form the full path to which the file is located at. The string is returned
    def getFullPath(self):
        return self.filePath + self.fileName;
