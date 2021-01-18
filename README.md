random-slideshow-python

A python script for playing a randomized slideshow from images within a specified directory.

Required modules:
- `Pillow`
- `image`

On Ubuntu, install the following packages:
- `sudo apt-get install python3-tk python3-pil python3-pil.imagetk`

Usage:
- Windows - `python slideshow.py [img_directory]`
- Ubuntu - `python3 slideshow.py [img_directory]`

In the `config.py` file, the following settings can be modified: 
- `duration` - time, in seconds, between image transitions. If no value is specified, the default duration is 4 seconds.
- `img_directory` - path to a folder containing image files (.jpg and .png only). If no path is specified, the default image directory is the present working directory.
- `topmost` - boolean flag to set whether the slideshow is displayed on top of all other windows or not
- `size_max_x`, `size_max_y` - maxiumum size, in pixels, to display the image at in the horizontal (x) and vertical (y) directions. If no values are specified, the default maximum values are determined the current display resolution.
- `position_x`, `position_y` - starting position, in pixels, from which the image is displayed relative to the top-left corner of the display, (0, 0). If no values are specified, the default starting position is (0, 0).