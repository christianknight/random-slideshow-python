random-slideshow-python

A python script for playing a randomized slideshow from images within a specified directory.

Required modules:
- `Pillow`
- `image`
- `pyautogui`

On Ubuntu, install the following packages:
- `sudo apt-get install python3-tk python3-pil python3-pil.imagetk`
- `python3 -m pip install pyautogui python-xlib`

Usage:
- Windows - `python slideshow.py [img_directory]`
- Ubuntu - `python3 slideshow.py [img_directory]`

In the `config.py` file, the following settings can be modified: 
- `duration` - time, in seconds, between image transitions. If no value is specified, the default duration is 4 seconds.
- `img_directory` - path to a folder containing image files (.jpg and .png only). If no path is specified, the default image directory is the present working directory.
- `topmost` - boolean flag to set whether the slideshow is displayed on top of all other windows or not
- `size_max_x`, `size_max_y` - maxiumum size, in pixels, to display the image at in the horizontal (x) and vertical (y) directions. If no values are specified, the default maximum values are determined by the current display resolution.
- `position_x`, `position_y` - starting position, in pixels, from which the image is displayed relative to the top-left corner of the display, (0, 0). If no values are specified, the default starting position is (0, 0).
- `fullscreen` - flag to indicate whether the slideshow should take up the full screen with black background
- `montage_mode` - flag to indicate if montage mode is activated (several tiled images)
- `montage_size` - number of photos to use in each montage when montage mode is activated
- `random` - flag to indicate whether to play the slideshow in random order or not
- `cursor_enable` - flag to indicate whether the mouse cursor should be shown on top of the slideshow or not
- `mouse_nudge` - flag to indicate whether to nudge the mouse cursor every time the slideshow advances (to keep the screensaver from activating)

To exit the slideshow, click anywhere in the image or press any key on the keyboard.