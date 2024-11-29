# random-slideshow-python
A Python script for playing a randomized slideshow from images within a specified directory.

## Setup
```
pip install -r requirements.txt
```

## Usage
```
python slideshow.py [img_directory]
```

## Configuration
- `DURATION` - Time interval, in seconds, between image transitions. Required.
- `IMG_DIRECTORY` - Path to a folder containing image files (.jpg and .png only). By default, images are loaded from the present working directory. Optional.
   NOTE - multiple image paths can be specified. For example:
     IMG_DIRECTORY:
       - directory 1
       - directory 2
- `IMG_SAVE_PATH` - Directory path for saving selected photos. Required.
- `TOPMOST` - Boolean flag to set whether the slideshow is displayed on top of all other windows or not. Required.
- `SIZE_MAX_X`, `SIZE_MAX_Y` - Maxiumum size, in pixels, to display the image at in the horizontal (x) or vertical (y) directions. If no values are specified, the default maximum values are determined by the current display resolution. Optional.
- `POSITION_X`, `POSITION_Y` - Starting position, in pixels, from which the image is displayed relative to the top-left corner of the display, (0, 0). Required.
- `FULLSCREEN` - Flag to indicate whether the slideshow should take up the full screen with black background. Required.
- `RANDOM` - Flag to indicate whether to play the slideshow in random order or not. Required.