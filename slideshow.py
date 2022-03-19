# Usage: python slideshow.py [img_directory]

import tkinter as tk
from PIL import Image, ImageTk
import sys
import os
from random import shuffle
from shutil import copy
import yaml
import pyautogui
from pathlib import Path
import logging

base_path = Path(__file__).parent
config_file_path = (base_path / "config.yml").resolve()

def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

# Read YAML config file
config = read_yaml(config_file_path)

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
        self.duration = config["SETTINGS"]["DURATION"]
        self.size_max_x = self.winfo_screenwidth()  # Max photo width based on display dimensions
        self.size_max_y = self.winfo_screenheight() # Max photo height based on display dimensions
        self.position_x = config["SETTINGS"]["POSITION_X"]
        self.position_y = config["SETTINGS"]["POSITION_Y"]
        self.fullscreen = config["SETTINGS"]["FULLSCREEN"]
        self.slideshow_paused = False               # flag to keep track of if the slideshow is paused from user input
        self.forward_index = -1                     # index for tracking position in playlist in order to show consecutive random images
        self.reverse_index = -1                     # index for tracking position in playlist in order to show the previously displayed images
        self.image_save_path = config["SETTINGS"]["IMG_SAVE_PATH"]
        self.scaled_w = None                        # for holding the width of the currently displayed image
        self.scaled_h = None                        # for holding the height of the currently displayed image
        self.random = config["SETTINGS"]["RANDOM"]
        self.cursor_enable = config["SETTINGS"]["CURSOR_ENABLE"]
        self.mouse_nudge = config["SETTINGS"]["MOUSE_NUDGE"]
        self.topmost = config["SETTINGS"]["TOPMOST"]
        self.exclusive_dir = config["SETTINGS"]["EXCLUSIVE_DIR"]

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
        self.bind("<Double-Button-1>", self.copy_image)                  # copy the current photo into the destination directory on left mouse double-click
        self.bind("<Return>", self.copy_image)                           # copy the current photo into the destination directory on return (enter) keypress
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

        self.startSlideShow()

    def getImages(self):
        # Get image path(s) from command line arguments or the config file - otherwise, use the present working directory
        if len(sys.argv) > 1:
            image_dirs = sys.argv[1:]
        elif "IMG_DIRECTORY" in config["SETTINGS"]:  # If present, use the image directory path from the config file
            image_dirs = config["SETTINGS"]["IMG_DIRECTORY"]
        else:   # Use the present working directory if no other path is found
            image_dirs = '.'

        if isinstance(image_dirs, list):
            for curr_dir in image_dirs:
                for root, dirs, files in os.walk(curr_dir):
                    for f in files:
                        if f.endswith(".png") or f.endswith(".jpg"):
                            img_path = os.path.join(root, f)
                            self.imageList.append(img_path)
                    if self.exclusive_dir == True:
                        break
        else:
            for root, dirs, files in os.walk(image_dirs):
                for f in files:
                    if f.endswith(".png") or f.endswith(".jpg"):
                        img_path = os.path.join(root, f)
                        self.imageList.append(img_path)
                if self.exclusive_dir == True:
                    break

        # Retrieve and print the length of the image list
        self.imageListLen = len(self.imageList)
        print(f"{self.imageListLen} images loaded from \"{image_dirs}\"")

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
        try:
            image = Image.open(filename)
        except Exception:
            logging.exception(f"Error occurred while opening {filename}")
            return

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

    def slideshow_cancel(self):
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None

    def mouse_click_left(self, event):
        global left_click_x, left_click_y
        left_click_x = event.x
        left_click_y = event.y
        # print(f"Mouse left-click at ({left_click_x}, {left_click_y})")

    def copy_image(self, event):
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