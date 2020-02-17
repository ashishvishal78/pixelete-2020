import time
import math
import cv2
import numpy as np


lr = np.load('lrr.npy')
ur = np.load('urr.npy')
ly = np.load('lry.npy')
uy = np.load('ury.npy')
lb = np.load('lrb.npy')
ub = np.load('urb.npy')
lg = np.load('lrg.npy')
ug = np.load('urg.npy')
lw = np.load('lrw.npy')
uw = np.load('urw.npy')
roi = np.load('roi.npy')

cap=cv2.VideoCapture(1)


while(True):
    #time.sleep(2)
    ret, img = cap.read()
    #img = cv2.GaussianBlur(img, (5, 5), 0)
    if (ret == False):
        break
    cv2.imshow('frame', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # cv2.imshow('resize',res_img)
    # take ROI
    arena = img[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]
    im1=cv2.inRange(arena,lr,ur)
    im2 = cv2.inRange(arena, ly, uy)
    im3 = cv2.inRange(arena, lb, ub)
    im4 = cv2.inRange(arena, lg, ug)
    im5 = cv2.inRange(arena, lw, uw)
    cv2.imshow('im1',im1)
    cv2.imshow('im2',im2)
    cv2.imshow('im3',im3)
    cv2.imshow('im4',im4)
    cv2.imshow('im5',im5)
cap.release()
cv2.destroyAllWindows()

