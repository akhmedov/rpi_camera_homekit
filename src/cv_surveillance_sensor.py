import os
import cv2
import requests
import threading
import numpy as np
from datetime import datetime
from video_cap_async import VideoCaptureAsync


def write_png(filepath, image, det_boxes, det_weights):
    print('[II] Writing:', filepath)
    det_boxes = round(float(np.squeeze(sum(det_boxes))), 2)
    image = cv2.putText(image, str(det_weights), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    det_boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in det_boxes])
    for (xA, yA, xB, yB) in det_boxes:
        image = cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)
    cv2.imwrite(filepath, image)


IMAGE_DIR = '/home/rolan/rpi_camera_homekit/detections'

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
cap = VideoCaptureAsync('tcp://127.0.0.1:8000/')

while cap.isOpened():
    _, frame = cap.read()
    # frame = cv2.resize(frame, (640, 480))
    # frame = cv2.transpose(cv2.transpose(cv2.transpose(frame)))
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    boxes, weights = hog.detectMultiScale(gray, winStride=(8, 8))
    if sum(weights) > 1.2:
        response = requests.get('http://127.0.0.1:8080/motion/motion?RPi%20Camera')
        now = datetime.now()
        filename = f'{now:%Y%m%d-%H%M%S}' + '.png'
        filename = os.path.join(IMAGE_DIR, filename)
        cv2.imwrite(filename, frame)
        # write_png(filename, frame, boxes, weights)
        # threading.Thread(target=write_png, args=(filename, frame, boxes, weights)).start()

cap.release()
