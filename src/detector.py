import cv2


class PedestrianSVM:
    def __init__(self):
        self._hog = cv2.HOGDescriptor()
        pedestrian = cv2.HOGDescriptor_getDefaultPeopleDetector()
        self._hog.setSVMDetector(pedestrian)

    def call(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        rects, weights = self._hog.detectMultiScale(gray, winStride=(8, 8))
        return rects, None, weights


class MotionDetectorBS:
    def __init__(self, area_threshold, detect_shadows=False):
        self._area_threshold = area_threshold
        self._back_sub = cv2.createBackgroundSubtractorKNN(detectShadows=detect_shadows)

    def call(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        front_ground = self._back_sub.apply(gray)
        # front_ground = cv2.threshold(front_ground, intensity_threshold, 255, cv2.THRESH_BINARY)[1]
        contours, _ = cv2.findContours(front_ground, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]
        rects = [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) > self._area_threshold]
        return rects, None, None


class PedestrianAnimalsTFLite:
    def __init__(self):
        pass

    def call(self, image):
        pass
