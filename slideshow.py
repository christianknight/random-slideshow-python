# Usage: python slideshow.py [img_directory]

import tkinter as tk
from PIL import Image, ImageTk
import sys
import os
from random import shuffle, randrange
from shutil import copy

try:
    import config
except:
    config = None

if hasattr(config, 'montage_mode') and config.montage_mode == True:
    from montage import montage_build

if not hasattr(config, 'mouse_nudge') or config.mouse_nudge == True:
    import pyautogui

class HiddenRoot(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        # Shrink root window to size 0x0 to suppress window
        self.wm_geometry("0x0+0+0")

        self.attributes('-alpha', 0.0)  # Shrink the window border size to 0
        self.iconify()                  # Turn the window into an icon without destroying

        self.window = MySlideShow(self)

class MySlideShow(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)

        self._job = None                # For storing job ID when running tk.after()
        self.persistent_image = None    # For saving reference to currently displayed image
        self.imageList = []             # For holding the list of image names in the pool
        self.imageListLen = 0           # The length of the image list
        self.duration = 4   # Default interval between photos is 4 seconds
        self.size_max_x = self.winfo_screenwidth()  # Max photo width based on display dimensions
        self.size_max_y = self.winfo_screenheight() # Max photo height based on display dimensions
        self.position_x = self.position_y = 0       # starting x-y position, in pixels, from which the image is displayed relative to the top-left corner of the display, (0, 0)
        self.fullscreen = True                      # flag to indicate whether the slideshow should take up the full screen with black background
        self.montage_mode = False                   # flag to indicate if montage mode is activated (several tiled images)
        self.montage_size = 8                       # number of photos to use in each montage when montage mode is activated
        self.slideshow_paused = False               # flag to keep track of if the slideshow is paused from user input
        self.forward_index = -1                     # index for tracking position in playlist in order to show consecutive random images
        self.reverse_index = -1                     # index for tracking position in playlist in order to show the previously displayed images
        self.image_save_path = '.'                  # directory path for saving selected photos
        self.scaled_w = None                        # for holding the width of the currently displayed image
        self.scaled_h = None                        # for holding the height of the currently displayed image
        self.random = True                          # flag to indicate whether to play the slideshow in random order or not
        self.cursor_enable = False                  # flag to indicate whether the mouse cursor should be shown on top of the slideshow or not
        self.mouse_nudge = True                     # flag to indicate whether to nudge the mouse cursor every time the slideshow advances (to keep the screensaver from activating)
        self.topmost = True                         # flag to indicate whether the slideshow is displayed on top of all other windows or not
        self.exclusive_dir = False                  # flag to indicate whethher the subdirectories within the image directory should be searched for photos

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
        if hasattr(config, 'random'):
            self.random = config.random
        if hasattr(config, 'cursor_enable'):
            self.cursor_enable = config.cursor_enable
        if hasattr(config, 'mouse_nudge'):
            self.mouse_nudge = config.mouse_nudge
        if hasattr(config, 'exclusive_dir'):
            self.exclusive_dir = config.exclusive_dir
        if hasattr(config, 'topmost'):
            self.topmost = config.topmost

        self.attributes('-topmost', self.topmost)
        self.configure(bg='black', width=self.winfo_screenwidth(), height=self.winfo_screenheight())
        self.wm_geometry("{}x{}+{}+{}".format(self.winfo_screenwidth(),self.winfo_screenheight(),0,0))

        # Remove window decorations (differently for Linux and Windows)
        if sys.platform == "linux" or sys.platform == "linux2":
            self.wm_attributes('-type', 'splash')
            if self.fullscreen:
                self.attributes('-fullscreen', True)
            else:
                self.attributes('-fullscreen', False)
        elif sys.platform == "win32":
            self.overrideredirect(True)

        # Display as background image
        self.label = tk.Label(self)
        self.label.pack(side="top", fill="both", expand=True)
        self.label.focus_force()

        # set key binding actions
        self.bind("<Button-3>", lambda e: quit())                        # terminate the slideshow on single right-click
        self.bind("<Double-Button-1>", self.double_left_click)           # copy the current photo into the destination directory on double-click
        self.bind("<Escape>", lambda e: quit())                          # terminate the slideshow on escape keypress
        self.bind("<Button-1>", self.mouse_click_left)                   # capture the x-y mouse coordinates on single left-click
        self.bind("<Left>", self.left_arrow_pressed)                     # jump to the previous image on left-arrow keypress
        self.bind("<Right>", self.right_arrow_pressed)                   # jump to the next image on right-arrow keypress
        self.bind("<space>", self.spacebar_pressed)                      # pause or resume the slideshow on spacebar keypress
        self.bind("<Up>", self.up_arrow_pressed)                         # increase the photo duration by 1 second on up arrow keypress
        self.bind("<Down>", self.down_arrow_pressed)                     # decrease the photo duration by 1 second on down arrow keypress
        self.bind("<F11>", self.f11_pressed)                             # toggle fullscreen mode on F11 keypress
        self.bind("<MouseWheel>", self.scroll_wheel_activated)           # toggle topmost mode on scroll wheel movement

        # Hide the mouse cursor (unless enabled by user config)
        if not self.cursor_enable:
            self.config(cursor="none")

        self.getImages()
        if self.random:
            shuffle(self.imageList)     # randomize the image playlist

        if self.montage_mode:
            self.startMontageSlideShow()
        else:
            self.startSlideShow()

    def getImages(self):
        # Get image path(s) from command line arguments or the config file - otherwise, use the present working directory
        if len(sys.argv) > 1:
            image_dirs = sys.argv[1:]
        elif hasattr(config, 'img_directory'):  # If present, read the photo directory path from the config file
            image_dirs = config.img_directory
        else:   # Use the present working directory if no other path is found
            image_dirs = '.'

        for curr_dir in image_dirs:
            for root, dirs, files in os.walk(curr_dir):
                for f in files:
                    if f.endswith(".png") or f.endswith(".jpg"):
                        img_path = os.path.join(root, f)
                        self.imageList.append(img_path)
                if self.exclusive_dir == True:
                    break

        # Retrieve and print the length of the image list
        self.imageListLen = len(self.imageList)
        print(f"{self.imageListLen} images loaded from '{image_dirs}'")

    def startSlideShow(self):
        if not self.slideshow_paused:                           # check if the slideshow is currently puased
            self.index_next_random_image()                      # going forward in random list, update the indexing variables
            self.showImage(self.imageList[self.forward_index])  # get next photo from a random image and show it
            if self.mouse_nudge:
                self.do_mouse_nudge()    # keep the screensaver from activating
            self._job = self.after(self.duration * 1000, self.startSlideShow)   # recursion - after the set duration, repeat

    def index_next_random_image(self):
        if self.forward_index < self.imageListLen - 1:  # check if the last image in the playlist was just displayed
            self.forward_index += 1                     # increment the playlist index
        else:                                           # randomize the image playlist and reset the indices to the beginning
            shuffle(self.imageList)
            self.forward_index = 0

        self.reverse_index = self.forward_index     # reset the reverse index (no longer back-tracking)

    def showImage(self, filename):
        image = Image.open(filename)

        # Print photo details to output
        print(filename)

        img_w, img_h = image.size
        # print(f"Image size (x, y) = ({img_w}, {img_h})")
        width, height = min(self.size_max_x, img_w), min(self.size_max_y, img_h)
        # print(f"Scaled size (x, y) = ({width}, {height})")
        image.thumbnail((width, height), Image.ANTIALIAS)

        # Store the size of the image to be displayed
        self.scaled_w, self.scaled_h = image.size

        # Set window size after scaling the original image up/down to fit screen
        # and remove the border on the image
        if not self.fullscreen:
            self.wm_geometry("{}x{}+{}+{}".format(self.scaled_w, self.scaled_h, self.position_x, self.position_y))
        
        # Create the new image 
        self.persistent_image = ImageTk.PhotoImage(image)
        self.label.configure(image=self.persistent_image, bg='black')

    def startMontageSlideShow(self):
        # Get a list of filepaths to 5 random photos
        random_file_paths = []
        for x in range(self.montage_size):
            random_file_paths.append(self.imageList[randrange(self.imageListLen)])
            print(random_file_paths[x])

        print(f"Building montage from {self.montage_size} images")
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

        self._job = self.after(self.duration * 1000, self.startMontageSlideShow)

    def slideshow_cancel(self):
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None

    def mouse_click_left(self, event):
        global left_click_x, left_click_y
        left_click_x = event.x
        left_click_y = event.y
        # print(f"Mouse left-click at ({left_click_x}, {left_click_y})")

    def double_left_click(self, event):
        if self.reverse_index < self.forward_index:                                   # check if backtracking
            copy(self.imageList[self.reverse_index], self.image_save_path)     # copy the current file into the destination directory
            print(f"{self.imageList[self.reverse_index]} copied to \"{self.image_save_path}\"")
        else:
            copy(self.imageList[self.forward_index], self.image_save_path)     # copy the current file into the destination directory
            print(f"{self.imageList[self.forward_index]} copied to \"{self.image_save_path}\"")

    def left_arrow_pressed(self, event):
        self.slideshow_cancel()      # kill the slideshow
        
        if self.reverse_index > 0:
            self.reverse_index -= 1  # decrement the reverse index to select the previous image in the playlist

        self.showImage(self.imageList[self.reverse_index]) # show selected image

        self._job = self.after(self.duration * 1000, self.startSlideShow)       # after the set duration, continue the slideshow

    def right_arrow_pressed(self, event):
        self.slideshow_cancel()                                              # kill the slideshow

        if self.reverse_index < self.forward_index:                   # already backtracking
            self.reverse_index += 1                                          # index to image ahead of last displayed
            self.showImage(self.imageList[self.reverse_index]) # show selected image
        else:
            self.index_next_random_image()                                   # going forward in random list, update the indexing variables
            self.showImage(self.imageList[self.forward_index]) # show selected image

        self._job = self.after(self.duration * 1000, self.startSlideShow)       # after the set duration, continue the slideshow

    def up_arrow_pressed(self, event):
        self.duration += 1   # increase the photo duration by 1 second
        print(f"Photo duration: {self.duration} seconds")

    def down_arrow_pressed(self, event):
        self.duration -= 1   # decrease the photo duration by 1 second
        print(f"Photo duration: {self.duration} seconds")

    def spacebar_pressed(self, event):
        if self.slideshow_paused == False:
            print("Slideshow paused, press space to resume")
            self.slideshow_paused = True
        else:
            print("Resuming slideshow")
            self.slideshow_paused = False

    def f11_pressed(self, event):
        if self.fullscreen == False:
            print("Entering fullscreen mode")
            self.fullscreen = True
            self.configure(bg='black', width=self.winfo_screenwidth(), height=self.winfo_screenheight())
            self.wm_geometry("{}x{}+{}+{}".format(self.winfo_screenwidth(),self.winfo_screenheight(), 0, 0))
            self.attributes('-fullscreen', True)
        else:
            print("Leaving fullscreen mode")
            self.fullscreen = False
            self.configure(bg='black', width=self.scaled_w, height=self.scaled_h)
            self.wm_geometry("{}x{}+{}+{}".format(self.scaled_w,self.scaled_h, 0, 0))
            self.attributes('-fullscreen', False)

    def scroll_wheel_activated(self, event):
        if self.topmost == False:
            print("Enabling topmost window mode")
            self.topmost = True
        else:
            print("Disabling topmost window mode")
            self.topmost = False

        self.attributes('-topmost', self.topmost)

    def do_mouse_nudge(self):
        pyautogui.move(0, 1)     # move the mouse cursor down by 1 pixel
        pyautogui.move(0, -1)    # move the mouse cursor up by 1 pixel

slideShow = HiddenRoot()
slideShow.mainloop()