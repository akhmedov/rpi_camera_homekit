import cv2
import threading

class VideoCaptureAsync:
    def __init__(self, src):
        self.cap = cv2.VideoCapture(src)
        if not self.cap.isOpened():
            self._reconect_capture(src, total_attempts=10)
        self.grabbed, self.frame = self.cap.read()
        self.started = False
        self.read_lock = threading.Lock()
        self._start()

    def _reconect_capture(self, src, total_attempts):
        print('[WW] Capture not avalible at', src)
        print('[II] Retry...')
        attempts = 0
        while not self.cap.isOpened():
            self.cap = cv2.VideoCapture(src)
            attempts += 1
            if attempts > total_attempts:
                print('[EE] All capture attemption are failed')
                break

    def _start(self):
        if self.started:
            print('[WW] Asynchroneous video capturing has already been started.')
            return None
        self.started = True
        self.thread = threading.Thread(target=self._update, args=())
        self.thread.start()
        return self

    def _stop(self):
        self.started = False
        self.thread.join()

    def _update(self):
        while self.started:
            grabbed, frame = self.cap.read()
            with self.read_lock:
                self.grabbed = grabbed
                self.frame = frame

    def read(self):
        with self.read_lock:
            frame = self.frame.copy()
            grabbed = self.grabbed
        return grabbed, frame

    def get(self, variable):
        return self.cap.get(variable)

    def release(self):
        self._stop()
        self.cap.release()

    def isOpened(self):
        return self.cap.isOpened()
