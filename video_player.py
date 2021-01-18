import cv2 
import numpy as np

# Read the input file 
cap = cv2.VideoCapture('test.mp4') 
   
# Check if the file was opened successfully 
if (cap.isOpened() == False):  
  print("Error opening video file") 
   
# Main playback loop - display each frame of the video until it is complete
while(cap.isOpened()): 
      
  # Capture the next pending frame
  ret, frame = cap.read()
  # Check if the frame was captured successfully
  if ret == True: 
   
    # Display the resulting frame 
    cv2.imshow('Frame', frame) 
   
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