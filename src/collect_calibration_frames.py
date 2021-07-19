import os
import re
import cv2
import glob
from video_capture_async import VideoCaptureAsync

'''
WARNING: calibration can be dependent on camera mode (aka resolution) so use only 
propriate image input like 1440x1080.
'''

SOURCE_VIDEO_STREAM = 'tcp://10.42.0.196:8081'
CALIB_FRAMES_DIR = 'calib_frames'
DISPLAY_RES_SCALE = 0.9
CHESSBOARD_WIDTH = 7
CHESSBOARD_HEIGHT = 9
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


def find_last_frame(frames_dir):
    frame_wildcard = os.path.join(CALIB_FRAMES_DIR, '*.png')
    frame_paths = glob.glob(frame_wildcard)
    if frame_paths:
        frame_paths.sort()
        last_frame = frame_paths[-1]
        last_frame = os.path.splitext(os.path.basename(last_frame))[0]
        last_frame_index = int(re.search(r'\d+', last_frame).group())
        return last_frame_index
    else:
        return 0


# tcp stream must handle frames one by one so we need to "skip" them 
# during the proccessing piplene to prevent "freezing"
cap = VideoCaptureAsync(SOURCE_VIDEO_STREAM).start()
cap_shape = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
disp_shape = int(DISPLAY_RES_SCALE * cap_shape[0]), int(DISPLAY_RES_SCALE * cap_shape[1])
print('Caption frame shape:', cap_shape)
print('Display frame shape:', disp_shape)

index = find_last_frame(CALIB_FRAMES_DIR) + 1
print('Press (s) to save frame')
print('Press (q) to exit')

while True:

    _, frame_bgr = cap.read()
    frame_bgr_orig = frame_bgr.copy()

    frame_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(frame_gray, (CHESSBOARD_WIDTH,CHESSBOARD_HEIGHT), None)
    if ret == True:
        corners2 = cv2.cornerSubPix(frame_gray, corners, (11,11), (-1,-1), criteria)
        cv2.drawChessboardCorners(frame_bgr, (CHESSBOARD_WIDTH, CHESSBOARD_HEIGHT), corners2, ret)

    frame_bgr = cv2.resize(frame_bgr, disp_shape)
    cv2.imshow('image', frame_bgr)

    pressedKey = cv2.waitKey(1) & 0xFF
    if pressedKey == ord('s'):
        frame_name = os.path.join(CALIB_FRAMES_DIR, str(index).zfill(6) + '.png')
        print('Writing image at path %s with index %i' % (frame_name, index))
        cv2.imwrite(frame_name, frame_bgr_orig)
        index += 1
    elif pressedKey == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
