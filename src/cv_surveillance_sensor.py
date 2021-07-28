import os
import cv2
import argparse
import requests
import threading
import numpy as np
from datetime import datetime
from video_cap_async import VideoCaptureAsync
from detector import PedestrianSVM, MotionDetectorBS, PedestrianAnimalsTFLite

# det_weights = round(float(np.squeeze(sum(det_weights))), 2)
# image = cv2.putText(image, str(det_weights), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)


def draw_detections(image, bounding_boxes, color=(0, 255, 0)):
    for x, y, w, h in bounding_boxes:
        point1 = x, y
        point2 = x + w, y + h
        image = cv2.rectangle(image, point1, point2, color, 2)
    return image


parser = argparse.ArgumentParser(description='')
parser.add_argument('--ip', required=True, help='Streaming IP address')
parser.add_argument('--store', required=False, help='Path for images storage directory')
parser.add_argument('--display', choices=['True', 'False'], required=True, help='Showing stream with detections')
args = parser.parse_args()

cap = VideoCaptureAsync(f'tcp://{args.ip}:8000/')
image_area = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
detector = MotionDetectorBS(area_threshold=image_area/200, detect_shadows=False)

while cap.isOpened():
    _, frame = cap.read()
    # frame = cv2.transpose(cv2.transpose(cv2.transpose(frame)))
    rect, _, _ = detector.call(frame)

    if args.display == 'True':
        frame = draw_detections(frame, rect)
        frame = cv2.resize(frame, (1440, 1080))
        cv2.imshow('Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if rect and args.store:
        response = requests.get(f'http://{args.ip}:8080/motion/motion?RPi%20Camera')
        now = datetime.now()
        filename = f'{now:%Y%m%d-%H%M%S}' + '.png'
        filename = os.path.join(args.store, filename)
        threading.Thread(target=cv2.imwrite, args=(filename, frame)).start()

cap.release()
