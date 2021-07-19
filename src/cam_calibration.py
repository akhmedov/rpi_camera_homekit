
import cv2
import time
import glob
import argparse
import numpy as np
import os
import glob
import sys
import re
import sys
from tqdm import tqdm

DISPLAY_RES_SCALE = 0.9
CHESSBOARD_WIDTH = 7
CHESSBOARD_HEIGHT = 9
CALIB_IMG_WILEDCARD = 'calib-img/*.png'
VALIDATION_FRAME = 'calib-img/000008.png'
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((CHESSBOARD_HEIGHT*CHESSBOARD_WIDTH,3), np.float32)
objp[:,:2] = np.mgrid[0:CHESSBOARD_WIDTH,0:CHESSBOARD_HEIGHT].T.reshape(-1,2)

objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

skipped_frames = []

frame_paths = glob.glob(CALIB_IMG_WILEDCARD)
frame_paths.sort()

print('Press (y) to select frame for calibration')
print('Press (n) to drop frame from calibration data')
print('Press (Esc) or (q) for exit')

for path in tqdm(frame_paths):
    frame_bgr = cv2.imread(path)

    frame_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(frame_gray, (CHESSBOARD_WIDTH,CHESSBOARD_HEIGHT), None)
    if ret == True:
        corners2 = cv2.cornerSubPix(frame_gray, corners, (11,11), (-1,-1), criteria)
        cv2.drawChessboardCorners(frame_bgr, (CHESSBOARD_WIDTH, CHESSBOARD_HEIGHT), corners2, ret)

    frame_height, frame_width, _ = frame_bgr.shape
    disp_shape = int(DISPLAY_RES_SCALE * frame_width), int(DISPLAY_RES_SCALE * frame_height)
    frame_bgr = cv2.resize(frame_bgr, disp_shape)

    cv2.imshow(path, frame_bgr)
    pressedKey = cv2.waitKey(0) & 0xFF
    if pressedKey == ord('y'):
        objpoints.append(objp)
        imgpoints.append(corners)
    elif pressedKey == ord('n'):
        skipped_frames.append(path)
    elif pressedKey == ord('q'):
        break
    cv2.destroyAllWindows()

print('Skiped frames:', skipped_frames)

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, (frame_width, frame_height), None, None)
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (frame_width,frame_height), 1, (frame_width,frame_height))

print('CAM_MTX', mtx)
print('CAM_DIST', dist)
print('CAM_NEWMAT', newcameramtx)

# estimage calibration error
mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
    mean_error += error
print( 'Total error: {}'.format(mean_error/len(objpoints)))
