# import pygame
# import pyautogui
# import time
# print('please type here')
# a = str(input( ))
# if a == 'yes':
#     pygame.init()
#     pygame.mixer.init()
#     pygame.mixer.music.load('yeah.mp3')
#     # pygame.mixer.music.set_volume(1)
#     pygame.mixer.music.play()

#     while pygame.mixer.music.get_busy(): 
#         pygame.time.Clock().tick(10)
# else:
#     print('nothing')

import cv2

cam = cv2.VideoCapture(0)

cv2.namedWindow("test")

img_counter = 0

while True:
    ret, frame = cam.read()
    cv2.imshow("test", frame)
    if not ret:
        break
    k = cv2.waitKey(1)

    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    
    elif k%256 == 32:
        # SPACE pressed
        img_name = "opencv_frame_{}.png".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1

cam.release()

cv2.destroyAllWindows()