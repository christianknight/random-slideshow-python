# Python 3 - random photo slideshow using tkinter and pillow (PIL)
# Usage: python3 random-slideshow.py [img_directory]

import tkinter as tk
from PIL import Image, ImageTk
import sys
import os
from random import shuffle

class HiddenRoot(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        # Shrink root window to size 0x0 in order to keep
        # ability to use key bindings (for "Esc" key)
        self.wm_geometry("0x0+0+0")

        self.attributes('-alpha', 0.0)  # Shrink the window border size to 0
        self.iconify()                  # Turn the window into an icon without destroying

        self.window = MySlideShow(self)
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
        self.pixNum = 0

        # Display as background image
        self.label = tk.Label(self)
        self.label.pack(side="top", fill="both", expand=True)

        self.getImages()

    def getImages(self):
        # Get image directory from command line or use current directory
        if len(sys.argv) == 2:
            curr_dir = sys.argv[1]
        else:
            curr_dir = '.'

        for root, dirs, files in os.walk(curr_dir):
            for f in files:
                if f.endswith(".png") or f.endswith(".jpg"):
                    img_path = os.path.join(root, f)
                    print(img_path)
                    self.imageList.append(img_path)

        # Randomize the image sequence
        shuffle(self.imageList)

        # Print the length of the image list
        print("{0} images loaded".format(len(self.imageList)))

    def startSlideShow(self, delay=4): #delay in seconds
        myimage = self.imageList[self.pixNum]
        self.pixNum = (self.pixNum + 1) % len(self.imageList)
        self.showImage(myimage)
        self.after(delay*1000, self.startSlideShow)

    def showImage(self, filename):
        image = Image.open(filename)

        # Print photo details to output
        print(filename)

        img_w, img_h = image.size
        print("Image size (x, y) = ({0}, {1})".format(img_w, img_h))
        scr_w, scr_h = self.winfo_screenwidth(), self.winfo_screenheight()
        print("Screen size (x, y) = ({0}, {1})".format(scr_w, scr_h))
        width, height = min(scr_w, img_w), min(scr_h, img_h)
        print("Scaled size (x, y) = ({0}, {1})".format(width, height))
        image.thumbnail((width, height), Image.ANTIALIAS)

        # Set window size after scaling the original image up/down to fit screen
        # and remove the border on the image
        scaled_w, scaled_h = image.size
        self.wm_geometry("{}x{}+{}+{}".format(scaled_w,scaled_h,0,0))
        
        # Create the new image 
        self.persistent_image = ImageTk.PhotoImage(image)
        self.label.configure(image=self.persistent_image)

    def pause(self):
        input('Slideshow paused, press any key to resume')

    def quit(self):
        self.root.destroy()

slideShow = HiddenRoot()
slideShow.bind("<Escape>", lambda e: slideShow.quit())  # Terminate on "Esc" keypress
slideShow.bind("<Insert>", lambda e: slideShow.pause())  # Pause slideshow on "Insert" keypress
slideShow.mainloop()
