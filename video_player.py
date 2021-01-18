import cv2 
import numpy as np
import screeninfo
import sys
import os

def load_videos(directory):
  video_list = []
  for root, dirs, files in os.walk(directory):
    for f in files:
        if f.endswith(".mp4"):
            video_path = os.path.join(root, f)
            video_list.append(video_path)

  return video_list

def get_display_dimensions():
  # Get display dimensions, in pixels
  display = screeninfo.get_monitors()[0]
  display_width, display_height = display.width, display.height

  return display_width, display_height

def show_video(video_path):
  # Read the input file
  vid = cv2.VideoCapture(video_path) 
   
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
      cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
      cv2.moveWindow(window_name, 0, 0)
      cv2.setWindowProperty(window_name, cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)

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

if __name__ == '__main__':
  video_list = load_videos(sys.argv[1])         # Load videos from directory in argument
  display_dimensions = get_display_dimensions() # Get dimensions of the display

  # Main loop - display each video
  for video in video_list:
    show_video(video)