import os
import cv2
import requests
from datetime import datetime
from video_cap_async import VideoCaptureAsync

IMAGE_DIR = 'detections'

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

cap = VideoCaptureAsync('tcp://127.0.0.1:8000/')

while cap.isOpened():
    _, frame = cap.read()
    frame = cv2.resize(frame, (640, 480))
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    boxes, weights = hog.detectMultiScale(frame, winStride=(8, 8))
    if boxes:
        response = requests.get('http://127.0.0.1:8080/motion/motion?RPi%20Camera')
        now = datetime.now()
        filename = f'{now:%Y-%m-%d--%H-%M-%S}' + '.png'
        filename = os.path.join(IMAGE_DIR, filename)
        cv2.imwrite(filename, frame)

cap.release()
