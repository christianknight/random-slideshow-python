# Usage: python slideshow.py [img_directory]

import tkinter as tk
from PIL import Image, ImageTk
import sys
import os
from random import shuffle
from montage import montage_build
from shutil import copy

try:
    import config
except:
    config = None

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

        # set key binding actions
        self.window.bind("<Button-3>", lambda e: quit())                        # terminate the slideshow on single right-click
        self.window.bind("<Double-Button-1>", self.double_left_click)           # copy the current photo into the destination directory on double-click
        self.window.bind("<Escape>", lambda e: quit())                          # terminate the slideshow on escape keypress
        self.window.bind("<Key>", lambda e: quit())                             # terminate the slideshow on any keypress
        self.window.bind("<Button-1>", self.mouse_click_left)                   # capture the x-y mouse coordinates on single left-click
        self.window.bind("<Left>", self.left_arrow_pressed)                     # jump to the previous image on left-arrow keypress
        self.window.bind("<Right>", self.right_arrow_pressed)                   # jump to the next image on right-arrow keypress
        self.window.bind("<space>", self.spacebar_pressed)                      # pause or resume the slideshow on spacebar keypress
        self.window.bind("<Up>", self.up_arrow_pressed)                         # increase the photo duration by 1 second on up arrow keypress
        self.window.bind("<Down>", self.down_arrow_pressed)                     # decrease the photo duration by 1 second on down arrow keypress

        if self.window.montage_mode:
            self.window.startMontageSlideShow()
        else:
            self.window.startSlideShow()

    def mouse_click_left(self, event):
        global left_click_x, left_click_y
        left_click_x = event.x
        left_click_y = event.y
        # print("Mouse left-click at ({0}, {1})".format(left_click_x, left_click_y))

    def double_left_click(self, event):
        if self.window.reverse_index < self.window.forward_index:                                   # check if backtracking
            copy(self.window.imageList[self.window.reverse_index], self.window.image_save_path)     # copy the current file into the destination directory
        else:
            copy(self.window.imageList[self.window.forward_index], self.window.image_save_path)     # copy the current file into the destination directory

    def left_arrow_pressed(self, event):
        if self.window.reverse_index > 0:
            self.window.reverse_index -= 1  # decrement the reverse index to select the previous image in the playlist

        self.window.showImage(self.window.imageList[self.window.reverse_index]) # show selected image

    def right_arrow_pressed(self, event):
        if self.window.reverse_index < self.window.forward_index:                   # already backtracking
            self.window.reverse_index += 1                                          # index to image ahead of last displayed
            self.window.showImage(self.window.imageList[self.window.reverse_index]) # show selected image
        else:
            self.window.index_next_random_image()                                   # going forward in random list, update the indexing variables
            self.window.showImage(self.window.imageList[self.window.forward_index]) # show selected image

    def up_arrow_pressed(self, event):
        self.window.duration += 1   # increase the photo duration by 1 second
        print("Photo duration: {0} seconds".format(self.window.duration))

    def down_arrow_pressed(self, event):
        self.window.duration -= 1   # decrease the photo duration by 1 second
        print("Photo duration: {0} seconds".format(self.window.duration))

    def spacebar_pressed(self, event):
        if self.window.slideshow_paused == False:
            print("Slideshow paused, press space to resume")
            self.window.slideshow_paused = True
        else:
            print("Resuming slideshow")
            self.window.slideshow_paused = False

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
        self.duration = 4   # Default interval between photos is 4 seconds
        self.size_max_x = self.winfo_screenwidth()  # Max photo width based on display dimensions
        self.size_max_y = self.winfo_screenheight() # Max photo height based on display dimensions
        self.position_x = self.position_y = 0       # starting x-y position, in pixels, from which the image is displayed relative to the top-left corner of the display, (0, 0)
        self.fullscreen = False                     # flag to indicate whether the slideshow should take up the full screen with black background
        self.montage_mode = False                   # flag to indicate if montage mode is activated (several tiled images)
        self.montage_size = 8                       # number of photos to use in each montage when montage mode is activated
        self.slideshow_paused = False               # flag to keep track of if the slideshow is paused from user input
        self.forward_index = -1                     # index for tracking position in playlist in order to show consecutive random images
        self.reverse_index = -1                     # index for tracking position in playlist in order to show the previously displayed images
        self.image_save_path = '.'                  # directory path for saving selected photos

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
        if hasattr(config, 'montage_mode'):
            self.montage_mode = config.montage_mode
        if hasattr(config, 'montage_size'):
            self.montage_size = config.montage_size
        if hasattr(config, 'image_save_path'):
            self.image_save_path = config.image_save_path

        # Display as background image
        self.label = tk.Label(self)
        self.label.pack(side="top", fill="both", expand=True)

        self.getImages()
        shuffle(self.imageList)     # randomize the image playlist

    def getImages(self):
        # Get image directory from command line or use current directory
        if len(sys.argv) == 2:
            curr_dir = sys.argv[1]
        elif hasattr(config, 'img_directory'):  # If present, ready the photo directory path from the config file
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

    def startSlideShow(self):
        if not self.slideshow_paused:                           # check if the slideshow is currently puased
            self.index_next_random_image()                      # going forward in random list, update the indexing variables
            self.showImage(self.imageList[self.forward_index])  # get next photo from a random image and show it

        self.after(self.duration * 1000, self.startSlideShow)   # recursion - after the set duration, repeat

    def index_next_random_image(self):
        if self.forward_index < self.imageListLen:  # check if the last image in the playlist was just displayed
            self.forward_index += 1                 # increment the playlist index
        else:                                       # randomize the image playlist and reset the indices to the beginning
            self.shuffle(imageList)
            self.forward_index = 0

        self.reverse_index = self.forward_index     # reset the reverse index (no longer back-tracking)

    def showImage(self, filename):
        image = Image.open(filename)

        # Print photo details to output
        print(filename)

        img_w, img_h = image.size
        # print("Image size (x, y) = ({0}, {1})".format(img_w, img_h))
        width, height = min(self.size_max_x, img_w), min(self.size_max_y, img_h)
        # print("Scaled size (x, y) = ({0}, {1})".format(width, height))
        image.thumbnail((width, height), Image.ANTIALIAS)

        # Set window size after scaling the original image up/down to fit screen
        # and remove the border on the image
        if not self.fullscreen:
            scaled_w, scaled_h = image.size
            self.wm_geometry("{}x{}+{}+{}".format(scaled_w,scaled_h,self.position_x,self.position_y))
        
        # Create the new image 
        self.persistent_image = ImageTk.PhotoImage(image)
        self.label.configure(image=self.persistent_image, bg='black')

    def startMontageSlideShow(self):
        # Get a list of filepaths to 5 random photos
        random_file_paths = []
        for x in range(self.montage_size):
            random_file_paths.append(self.imageList[randrange(self.imageListLen)])
            print(random_file_paths[x])

        print("Building montage from {0} images".format(self.montage_size))
        montage = montage_build(random_file_paths)

        img_w, img_h = montage.size
        width, height = min(self.size_max_x, img_w), min(self.size_max_y, img_h)
        montage.thumbnail((width, height), Image.ANTIALIAS)

        if not self.fullscreen:
            scaled_w, scaled_h = montage.size
            self.wm_geometry("{}x{}+{}+{}".format(scaled_w,scaled_h,self.position_x,self.position_y))
        
        # Create the new image 
        self.persistent_image = ImageTk.PhotoImage(montage)
        self.label.configure(image=self.persistent_image, bg='black')

        self.after(self.duration * 1000, self.startMontageSlideShow)

slideShow = HiddenRoot()
slideShow.mainloop()