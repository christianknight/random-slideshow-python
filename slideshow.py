# Usage: python slideshow.py [img_directory]

import tkinter as tk
from PIL import Image, ImageTk
import sys
import os
from random import randrange
from time import sleep
import cv2 
import numpy as np

try:
    import config
except:
    config = None

def pause_for_x_seconds(seconds):
        print('Pausing slideshow for {0} seconds...'.format(seconds))
        sleep(seconds)
        print('Resuming slideshow')

class HiddenRoot(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        # Shrink root window to size 0x0 to suppress window
        self.wm_geometry("0x0+0+0")

        self.attributes('-alpha', 0.0)  # Shrink the window border size to 0
        self.iconify()                  # Turn the window into an icon without destroying

        self.window = MySlideShow(self)

        self.window.configure(bg='black', width=self.winfo_screenwidth(), height=self.winfo_screenheight())
        self.window.wm_geometry("{}x{}+{}+{}".format(self.winfo_screenwidth(),self.winfo_screenheight(),0,0))

        if hasattr(config, 'topmost'):
            self.window.attributes('-topmost', config.topmost)
        else:
            self.window.attributes('-topmost', 1)   # Force the slideshow to always be on top

        self.window.bind("<Button-1>", lambda e: quit())                # terminate the slideshow on single-click
        self.window.bind("<Double-Button-1>", lambda e: quit())         # terminate the slideshow on double-click
        self.window.bind("<Escape>", lambda e: quit())                  # terminate the slideshow on escape keypress
        self.window.bind("<Key>", lambda e: quit())                  # terminate the slideshow on any keypress
        self.window.bind("<Insert>", lambda e: pause_for_x_seconds(20)) # Pause slideshow on "Insert" keypress

        self.window.startSlideShow()

class MySlideShow(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        # Remove window decorations 
        self.overrideredirect(True)

        # Save reference to photo so that garbage collection
        # Does not clear image variable in "show_image()"
        self.persistent_image = None
        self.imageList = []
        self.imageListLen = 0
        self.video_list = []
        self.video_list_len = 0
        self.duration = 4   # Default interval between photos is 4 seconds
        self.size_max_x = self.winfo_screenwidth()  # Max photo width based on display dimensions
        self.size_max_y = self.winfo_screenheight() # Max photo height based on display dimensions
        self.position_x = self.position_y = 0       # starting x-y position, in pixels, from which the image is displayed relative to the top-left corner of the display, (0, 0)
        self.fullscreen = False;                    # flag to indicate whether the slideshow should take up the full screen with black background
        self.video_player_enable = False            # flag to indicate if the slideshow is in video mode

        # If present, read from configuration file
        if hasattr(config, 'duration'):
            self.duration = config.duration
        if hasattr(config, 'size_max_x'):
            self.size_max_x = config.size_max_x
        if hasattr(config, 'size_max_y'):
            self.size_max_y = config.size_max_y
        if hasattr(config, 'position_x'):
            self.position_x = config.position_x
        if hasattr(config, 'position_y'):
            self.position_y = config.position_y
        if hasattr(config, 'fullscreen'):
            self.fullscreen = config.fullscreen
        if hasattr(config, 'video_player_enable'):
            self.video_player_enable = config.video_player_enable

        # Display as background image
        self.label = tk.Label(self)
        self.label.pack(side="top", fill="both", expand=True)

        if self.video_player_enable:
            self.getVideos()
        else:
            self.getImages()

    def getImages(self):
        # Get image directory from command line or use current directory
        if len(sys.argv) == 2:
            curr_dir = sys.argv[1]
        elif hasattr(config, 'img_directory'):  # If present, read the photo directory path from the config file
            curr_dir = config.img_directory
        else:
            curr_dir = '.'

        for root, dirs, files in os.walk(curr_dir):
            for f in files:
                if f.endswith(".png") or f.endswith(".jpg"):
                    img_path = os.path.join(root, f)
                    self.imageList.append(img_path)

        # Retrieve and print the length of the image list
        self.imageListLen = len(self.imageList)
        print("{0} images loaded".format(self.imageListLen))

    def getVideos(self):
        # Get image directory from command line or use current directory
        if len(sys.argv) == 2:
            curr_dir = sys.argv[1]
        elif hasattr(config, 'img_directory'):  # If present, read the photo directory path from the config file
            curr_dir = config.img_directory
        else:
            curr_dir = '.'

        for root, dirs, files in os.walk(curr_dir):
            for f in files:
                if f.endswith(".mp4"):
                    vid_path = os.path.join(root, f)
                    self.video_list.append(vid_path)

        # Retrieve and print the length of the video list
        self.video_list_len = len(self.video_list)
        print("{0} videos loaded".format(self.video_list_len))

    def startSlideShow(self):
        if not self.video_player_enable:
            myimage = self.imageList[randrange(self.imageListLen)]  # Show a random image from the image list
            self.showImage(myimage)
            self.after(self.duration * 1000, self.startSlideShow)
        else:
            video = self.video_list[randrange(self.video_list_len)]  # Show a random video from the video list
            self.showVideo(video)
            self.startSlideShow()

    def showImage(self, filename):
        image = Image.open(filename)

        # Print photo details to output
        print(filename)

        img_w, img_h = image.size
        print("Image size (x, y) = ({0}, {1})".format(img_w, img_h))
        width, height = min(self.size_max_x, img_w), min(self.size_max_y, img_h)
        print("Scaled size (x, y) = ({0}, {1})".format(width, height))
        image.thumbnail((width, height), Image.ANTIALIAS)

        # Set window size after scaling the original image up/down to fit screen
        # and remove the border on the image
        if not self.fullscreen:
            scaled_w, scaled_h = image.size
            self.wm_geometry("{}x{}+{}+{}".format(scaled_w,scaled_h,self.position_x,self.position_y))
        
        # Create the new image 
        self.persistent_image = ImageTk.PhotoImage(image)
        self.label.configure(image=self.persistent_image, bg='black')

    def showVideo(self, filename):
        # Read the input file
        vid = cv2.VideoCapture(filename) 
   
        # Check if the file was opened successfully 
        if (vid.isOpened() == False):  
            print("Error opening video file")

        # Get video dimensions, in pixels
        video_width  = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print('Video dimensions: ({0}, {1})'.format(video_width, video_height))

        # Playback loop - display each frame of the video until it is complete
        while(vid.isOpened()): 
            # Capture the next pending frame
            ret, frame = vid.read()
            # Check if the frame was captured successfully
            if ret == True: 
                # Resize the frame to fit the display
                window_name = 'Frame'
                cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
                cv2.moveWindow(window_name, 0, 0)
                cv2.setWindowProperty(window_name, cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
                cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

                # Display the frame
                cv2.imshow(window_name, frame)

                # Check for keypresses
                key = cv2.waitKey(25) & 0xFF
                if key == ord('q') or key == 27: # 'q' or 'Esc' keys
                    quit()
                elif key == 32: # Space bar
                    break
             
            # Break the loop if no frame was captured (end of video)
            else:  
                break
         
        # When playback is complete, release the video capture object 
        vid.release() 
         
        # Close the window
        cv2.destroyAllWindows()

slideShow = HiddenRoot()
slideShow.mainloop()