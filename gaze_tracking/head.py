import math
import numpy as np
import cv2
from .pupil import Pupil


class Head(object):
    """
    This class creates a new frame to isolate the eye and
    initiates the pupil detection.
    """

    head = [2, 27, 14, 8]

    def __init__(self, original_frame, landmarks):
        self.middle_eye = None
        self.left_side = None
        self.right_side = None
        self.chin = None

        self._analyze(landmarks)

    def _analyze(self, landmarks):
        """Detects and isolates the eye in a new frame, sends data to the calibration
        and initializes Pupil object.

        Arguments:
            original_frame (numpy.ndarray): Frame passed by the user
            landmarks (dlib.full_object_detection): Facial landmarks for the face region
            side: Indicates whether it's the left eye (0) or the right eye (1)
            calibration (calibration.Calibration): Manages the binarization threshold value
        """
        self.middle_eye = (landmarks.part(33).x, landmarks.part(33).y)
        self.left_side = (landmarks.part(2).x, landmarks.part(2).y)
        self.right_side = (landmarks.part(14).x, landmarks.part(14).y)
        self.chin = (landmarks.part(8).x, landmarks.part(8).y)

    def distance(self, first, second):
        x, y = first
        x1, y1 = second
        return math.sqrt((x - x1) ** 2 + (y - y1) ** 2)

    def left_distance(self):
        return (self.distance(self.middle_eye, self.left_side)
                + self.distance(self.chin, self.left_side))

    def right_distance(self):
        return self.distance(self.middle_eye, self.right_side) + self.distance(self.chin, self.right_side)