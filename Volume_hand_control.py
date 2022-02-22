import cv2
import time
import numpy as np
import Hand_tracking_module as htm
import math

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

##############################
w_cam, h_cam = 640, 480
##############################

cap = cv2.VideoCapture(0)
cap.set(3, w_cam)
cap.set(4, h_cam)
previous_time = 0

detector = htm.handDetector()

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volume_range = volume.GetVolumeRange()
print(volume_range)
volume.SetMasterVolumeLevel(0, None)

min_volume = volume_range[0]
max_volume = volume_range[1]

while True:
    success, img = cap.read()
    img = detector.find_hands(img)
    lm_list = detector.find_position(img, draw=False)

    if len(lm_list) != 0:
        # print(lm_list)

        x1, y1 = lm_list[4][1], lm_list[4][2]
        x2, y2 = lm_list[8][1], lm_list[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 15, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
        cv2.circle(img, (cx, cy), 12, (255, 0, 0), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        print(length)

        # Hand range 25 - 200
        # Volume range -65 - 0
        vol = np.interp(length, [20, 200], [min_volume, max_volume])
        print(vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length <= 25 or length >= 200:
            cv2.circle(img, (cx, cy), 12, (0, 0, 255), cv2.FILLED)

    current_time = time.time()
    fps = 1 / (current_time - previous_time)
    previous_time = current_time

    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

    cv2.imshow('Img', img)
    cv2.waitKey(1)
