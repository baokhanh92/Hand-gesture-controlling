import copy
import cv2
import numpy as np
from keras.models import load_model
import pygame
import time
import math

prediction = ''
action = ''
score = 0
img_counter = 0

class Volume(object):
    def __init__(self):
        self.level = .5

    def increase(self, amount):
        self.level += amount
        print(f'New level is: {self.level}')

    def decrease(self, amount):
        self.level -= amount
        print(f'New level is: {self.level}')


vol = Volume()

save_images = False
smart_home = True

gesture_names = {0: 'Fist',
                 1: 'L',
                 2: 'Okay',
                 3: 'Palm'}

model = load_model('models/fine_tune.h5')

def predict_rgb_image(img):
    result = gesture_names[model.predict_classes(img)[0]]
    print(result)
    return (result)

def predict_rgb_image_vgg(image):
    image = np.array(image, dtype='float32')
    image /= 255
    pred_array = model.predict(image)
    print(f'pred_array: {pred_array}')
    result = gesture_names[np.argmax(pred_array)]
    print(f'Result: {result}')
    print(max(pred_array[0]))
    score = float("%0.2f" % (max(pred_array[0]) * 100))
    print(result)
    return result, score

# parameters
cap_region_x_begin = 0.5  # start point/total width
cap_region_y_end = 0.8  # start point/total width
threshold = 60  # binary threshold
blurValue = 41  # GaussianBlur parameter
bgSubThreshold = 50
learningRate = 0

# variableslt
isBgCaptured = 1  # bool, whether the background captured
triggerSwitch = False  # if true, keyboard simulator works

def remove_background(frame):
    backSub = cv2.createBackgroundSubtractorMOG2()
    fgmask = backSub.apply(frame)
    kernel = np.ones((3, 3), np.uint8)
    fgmask = cv2.erode(fgmask, kernel, iterations=1)
    res = cv2.bitwise_and(frame, frame, mask=fgmask)
    return res

def predict(thresh):
# elif k == 32:
    # If space bar pressed
    # cv2.imshow('original', frame)
    # copies 1 channel BW image to all 3 RGB channels
    target = np.stack((thresh,) * 3, axis=-1)
    target = cv2.resize(target, (224, 224))
    target = target.reshape(1, 224, 224, 3)
    prediction, score = predict_rgb_image_vgg(target)

    
    if prediction == 'Palm' and score > 0.9:
        try:
            action = "Music on"

            # sonos.play()
            pygame.mixer.music.unpause()
        # Turn off smart home actions if devices are not responding
        except ConnectionError:
            pass

    elif prediction == 'Fist' and score > 0.9:
        try:
            action = 'Music off'
            # b.set_light(6, off_command)
            # sonos.pause()
            pygame.mixer.music.pause()
        except ConnectionError:
            pass

    elif prediction == 'L' and score > 0.9:
        try:
            action = 'Volume down'
            # sonos.volume -= 15
            vol.decrease(0.2)
            pygame.mixer.music.set_volume(vol.level)
        except ConnectionError:
            pass

    elif prediction == 'Okay' and score > 0.9:
        try:
            action = 'Volume up'
            # sonos.volume += 15
            vol.increase(0.2)
            pygame.mixer.music.set_volume(vol.level)
        except ConnectionError:
            pass


    return prediction, score

# Set music
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('music/yeah.mp3')
pygame.mixer.music.set_volume(vol.level)
pygame.mixer.music.play()
pygame.mixer.music.set_pos(50)
pygame.mixer.music.pause()

# Camera
camera = cv2.VideoCapture(0)
camera.set(10, 200)
frameRate = camera.get(5) #frame rate
i = 1
thresh = None
while camera.isOpened():
    frameId = camera.get(1) #current frame number
    ret, frame = camera.read()
    frame = cv2.bilateralFilter(frame, 5, 50, 100)  # smoothing filter
    frame = cv2.flip(frame, 1)  # flip the frame horizontally
    cv2.rectangle(frame, (int(cap_region_x_begin * frame.shape[1]), 0),
                    (frame.shape[1], int(cap_region_y_end * frame.shape[0])), (255, 0, 0), 2)

    
    i += 1
    if (ret != True):
        continue
    if i % 60 == 0:
        # Keyboard OP
        img = remove_background(frame)
        img = img[0:int(cap_region_y_end * frame.shape[0]),
              int(cap_region_x_begin * frame.shape[1]):frame.shape[1]]  # clip the ROI
        # convert the image into binary image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (blurValue, blurValue), 0)
        # cv2.imshow('blur', blur)
        ret, thresh = cv2.threshold(blur, threshold, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if ret:
            prediction, score = predict(thresh)
        cv2.putText(thresh, f"Prediction: {prediction} ({score}%)", (50, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 255))
        cv2.putText(thresh, f"Action: {action}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 255))  # Draw the text

    if thresh is not None:
        cv2.imshow('ori', thresh)
    cv2.imshow('original', frame)
    k = cv2.waitKey(10)
    if k == 27:  # press ESC to exit all windows at any time
        cv2.destroyAllWindows()
        camera.release()
    

    # elif k == ord('t'):

    #     print('Tracker turned on.')

    #     cap = cv2.VideoCapture(0)
    #     ret, frame = cap.read()

    #     # Select Region of Interest (ROI)
    #     r = cv2.selectROI(frame)

    #     # Crop image
    #     imCrop = frame[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]

    #     # setup initial location of window
    #     r, h, c, w = 250, 400, 400, 400
    #     track_window = (c, r, w, h)
    #     # set up the ROI for tracking
    #     roi = imCrop
    #     hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    #     mask = cv2.inRange(hsv_roi, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
    #     roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
    #     cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
    #     # Setup the termination criteria, either 10 iteration or move by at least 1 pt
    #     term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
    #     while (1):
    #         ret, frame = cap.read()
    #         if ret == True:
    #             hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #             dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)
    #             # apply meanshift to get the new location
    #             ret, track_window = cv2.CamShift(dst, track_window, term_crit)
    #             # Draw it on image
    #             pts = cv2.boxPoints(ret)
    #             pts = np.int0(pts)
    #             img2 = cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
    #             cv2.imshow('img2', img2)
    #             k = cv2.waitKey(60) & 0xff
    #             if k == 27:  # if ESC key
    #                 break
    #             else:
    #                 cv2.imwrite(chr(k) + ".jpg", img2)
    #         else:
    #             break
    