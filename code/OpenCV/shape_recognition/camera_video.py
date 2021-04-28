# Pour la caméra
from picamera.array import PiRGBArray
from picamera import PiCamera
# Pour OpenCV
import cv2
# Pour gérer le temps
import time

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
# allow the camera to warmup
time.sleep(0.1)
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    input_img = frame.array
# convert to gray in order to use it as a mask
    img_grey = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
    # _ is a variable that won't be used because the threshold returns 2 variables
    _, threshold = cv2.threshold(img_grey, 100, 255, cv2.THRESH_BINARY)
    # contours will be a list of all the contours in the image (each contour are numpy arrays of points such as (x,y))
    _, contours, _ = cv2.findContours(
        threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)


    for contour in contours:
        epsilon = 0.01
        approximation = cv2.approxPolyDP(
            contour, epsilon * cv2.arcLength(contour, True), True)
        cv2.drawContours(input_img, [approximation], 0, (0, 0, 0), 3)
        x = approximation.ravel()[0]
        y = approximation.ravel()[1]

        key = cv2.waitKey(1) & 0xFF
        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
        
    # show the frame
    cv2.imshow("Frame", input_img)
    


def nothing(x):
    pass
