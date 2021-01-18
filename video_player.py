import cv2 
import numpy as np
import screeninfo

# Read the input file 
cap = cv2.VideoCapture('test.mp4') 
   
# Check if the file was opened successfully 
if (cap.isOpened() == False):  
  print("Error opening video file")

# Get display dimensions, in pixels
display = screeninfo.get_monitors()[0]
display_width, display_height = display.width, display.height
print('Display dimensions: ({0}, {1})'.format(display_width, display_height))

# Get video dimensions, in pixels
video_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print('Video dimensions: ({0}, {1})'.format(video_width, video_height))

# Main playback loop - display each frame of the video until it is complete
while(cap.isOpened()): 
      
  # Capture the next pending frame
  ret, frame = cap.read()
  # Check if the frame was captured successfully
  if ret == True: 
    # Resize the frame to fit the display
    window_name = 'Frame'
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.moveWindow(window_name, display.x - 1, display.y - 1)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,
                          cv2.WINDOW_FULLSCREEN)
    # Display the frame
    cv2.imshow(window_name, frame)
   
    # At any point, press 'q' on the keyboard to exit
    if cv2.waitKey(25) & 0xFF == ord('q'): 
      break
   
  # Break the loop if no frame was captured (end of video)
  else:  
    break
   
# When playback is complete, release the video capture object 
cap.release() 
   
# Close the window
cv2.destroyAllWindows()