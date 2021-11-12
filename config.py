# config.py

# ----- Settings -----
# duration = 6
# img_directory = '.'
# image_save_path = '.'
# topmost = False
# size_max_x = 96
# size_max_y = 96
# position_x = 0
# position_y = 0
# fullscreen = True
# montage_mode = True
# montage_size = 10
# video_player_enable = True
# random = False
# cursor_enable = True
# mouse_nudge = False

# ----- Description of settings -----
# duration - time, in seconds, between image transitions. If no value is specified, the default duration is 4 seconds.
# img_directory - path to a folder containing image files (.jpg and .png only). If no path is specified, the default image directory is the present working directory.
# image_save_path - directory path for saving selected photos
# topmost - boolean flag to set whether the slideshow is displayed on top of all other windows or not
# size_max_x, size_max_y - maxiumum size, in pixels, to display the image at in the horizontal (x) or vertical (y) directions. If no values are specified, the default maximum values are determined by the current display resolution.
# position_x, position_y - starting position, in pixels, from which the image is displayed relative to the top-left corner of the display, (0, 0). If no values are specified, the default starting position is (0, 0).
# fullscreen - flag to indicate whether the slideshow should take up the full screen with black background
# montage_mode - flag to indicate if montage mode is activated (several tiled images)
# montage_size - number of photos to use in each montage when montage mode is activated
# video_player_enable - flag to indicate if the slideshow is in video mode
# random - flag to indicate whether to play the slideshow in random order or not
# cursor_enable - flag to indicate whether the mouse cursor should be shown on top of the slideshow or not
# mouse_nudge - flag to indicate whether to nudge the mouse cursor every time the slideshow advances (to keep the screensaver from activating)