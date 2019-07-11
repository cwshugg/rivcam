# A class used to represent the information regarding an Image taken by the
# Raspberry Pi Camera Module v2. Contains file path/name information.
class Image:
    
    # Image properties:
    #   fileName    The name of the file the image is saved to
    #   filePath    The path to the directory in which the file is contained
    
    def __init__(self, name, path):
        self.fileName = name + ".jpg";
        self.filePath = path;
    

    # --------------------- Setter Functions ---------------------- #
    # Function that takes in the new file name and attaches the correct file
    # extension to the end of the string
    def setFileName(self, newName):
        self.fileName = newName + ".jpg";
        
    
    # --------------------- Helper Functions ---------------------- #
    # Takes the image's file name and file path, and concatenates them together to
    # form the full path to which the file is located at. The string is returned
    def getFullPath(self):
        return self.filePath + self.fileName;

