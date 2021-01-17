random-slideshow-python

A python script for playing a randomized slideshow from images within a specified directory.

Usage: `python slideshow.py [img_directory]`

In the `config.py` file, the following settings can be modified: 
- `duration` - time, in seconds, between photo transitions
- `img_directory` - path to a folder containing image files (.jpg and .png). If no `img_directory` argument is specified, the default image directory is the present working directory.
- `topmost` - boolean flag to set whether the slideshow is on top of all other windows or not
