# @file main.py
# @brief Used to test shapes recognition

# Author : Ackermann Gawen
# Last update : 10.06.2021

import numpy as np
import cv2

def nothing(x):
    pass

# import the picture
input_img = cv2.imread("signs.png")
# convert to gray in order to use it as a mask
img_grey = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
input_threshold = cv2.createTrackbar('trbThreshold', 'Shapes recognition', 140, 255, nothing)

# _ is a variable that won't be used because the threshold returns 2 variables
_, threshold = cv2.threshold(img_grey, 150, 255, cv2.THRESH_BINARY)
# contours will be a list of all the contours in the image (each contour are numpy arrays of points such as (x,y))
contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

for contour in contours:
    epsilon = 0.01
    approximation = cv2.approxPolyDP(contour, epsilon * cv2.arcLength(contour, True), True)
    cv2.drawContours(input_img, [approximation], 0, (0, 0, 0), 3)
    x = approximation.ravel()[0]
    y = approximation.ravel()[1]

cv2.imshow("Shapes recognition", input_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
