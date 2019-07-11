import picamera;
from video import Video;
from image import Image;

# A class that handles the pi camera: creating Video and Image objects
# (helpful stuff: https://picamera.readthedocs.io/en/release-1.10/recipes1.html)
class DashCam:
    
    # DashCam properties:
    #   picam        The PiCamera object used to work the Camera Module
    #   currVideo    The current video that's being recorded (if any)
    #                (set to None otherwise)
    
    # Constructor: takes in an optional parameter: camera resolution
    def __init__(self, resolution = [1600, 900]):
        self.currVideo = None;
        self.picam = picamera.PiCamera();
        # set up the camera'a resolution and rotation
        self.picam.resolution = (resolution[0], resolution[1]);
        self.picam.rotation = 180;
    
    
    # Destructor: releases the picamera
    def __del__(self):
        # release the pi camera
        self.picam.close();
    
    
    # -------------------- Recording/Capturing -------------------- #
    # Creates a new video (with the given parameters), and starts the
    # python camera's video mode. self.currVideo is updated
    def startVideo(self, vidName, vidPath):
        # create the video object
        self.currVideo = Video(vidName, vidPath);
        
        # start recording the video
        self.picam.start_recording(self.currVideo.getFullPath());
        return;
    
    
    # Stops the recording of the current video, and returns the Video
    # object from self.currVideo. self.currVideo is nulled out.
    def stopVideo(self):
        # stop recording
        self.picam.stop_recording();

        # return the Video and empty self.currVideo
        vid = self.currVideo;
        self.currVideo = None;
        return vid;

    
    # Function that saves what's been currently recorded to self.currVideo's
    # specified file + path. self.currVideo's video name is updated for the next
    # time the video is saved or split
    def splitVideo(self, newName):
        self.picam.split_recording(self.currVideo.getFullPath());
        # update the video's name
        self.currVideo.setFileName(newName);


    # Takes a picture with the Pi Camera, returning an Image object containing
    # the information of the picture that was captured. (If self.currVideo is
    # NOT None, then a picture can't be taken, as a video is being recorded).
    def takePicture(self, picName, picPath):
        # create the image object
        img = Image(picName, picPath);
        
        # take the picture and return the Image object
        self.picam.capture(img.getFullPath());        
        return img;
    

    # --------------------- Helper Functions ---------------------- #    
    # Updates the text being displayed over the camera's video/pictures
    def updateOverlays(self, currentTime):
        self.picam.annotate_background = picamera.Color("black");
        self.picam.annotate_foreground = picamera.Color("white");
        self.picam.annotate_text_size = 15;
        
        # determine what to display depending on the second (it's the
        # current date/time by default)
        annotation = currentTime.strftime("%Y-%m-%d, %H:%M:%S");        
        if (self.currVideo.duration % 3 == 0):
            annotation = "Mod 3";
        
        # update the overlay text
        self.picam.annotate_text = str(annotation);



# debugging
# from time import sleep;
# c = DashCam();
# print("Picture name: " + c.makeFileName(False));
# print("Video name:   " + c.makeFileName(True));
# # video capturing
# print("Recording...");
# c.startVideo("dashcamVideo1", "/home/pi/coding/python/dash/test_data/");
# c.picam.wait_recording(12);
# vid = c.stopVideo();
# # image capturing
# pic = c.takePicture("dashcamPicture1", "/home/pi/coding/python/dash/test_data/");
# pic = c.takePicture(DashCam.makeFileName(False), "/home/pi/coding/python/dash/test_data/");
