import cv2
import numpy as np
import math
import time

def clr_range(LR,UR,arena):
    for i in range(4):
        r = cv2.selectROI(arena)
        col_img = arena[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]
        row, col, hei = col_img.shape
        for r1 in range(row):
            for c in range(col):
                pixe = col_img[r1][c]
                for k in range(3):
                    LR[k] = min(LR[k], max(pixe[k]-26,0))
                    UR[k] = max(UR[k], min(pixe[k]+26,255))
    return LR,UR

def clr_range_green(LR,UR,arena):
    for i in range(4):
        r = cv2.selectROI(arena)
        col_img = arena[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]
        row, col, hei = col_img.shape
        for r1 in range(row):
            for c in range(col):
                pixe = col_img[r1][c]
                for k in range(3):
                    LR[k] = min(LR[k], max(pixe[k]-7,0))
                    UR[k] = max(UR[k], min(pixe[k]+9,255))
    return LR,UR


def recog_col(color_mat,shape_mat,row,col,LRW,URW,arena,num):
    lrw = np.array([LRW])
    urw = np.array([URW])
    mask = cv2.inRange(arena, lrw, urw)
    cv2.imshow('mask', mask)
    cv2.waitKey(0)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # for ignoring small contours
    total_cnt_area = 0
    no_of_cnt = 0
    for cnt in contours:
        total_cnt_area += cv2.contourArea(cnt)
        no_of_cnt += 1

    avg_cnt_area = total_cnt_area / no_of_cnt
    thresh_cnt_area = avg_cnt_area / 3
    for cnt in contours:
        area_of_cnt = cv2.contourArea(cnt)
        if (area_of_cnt > thresh_cnt_area):
            cen = cv2.moments(cnt)
            cenx = int(cen["m10"] / cen["m00"])
            ceny = int(cen["m01"] / cen["m00"])
            cenx = cenx // row
            ceny = ceny // col
            print(ceny,cenx)
            color_mat[ceny][cenx] = num
            # shape recog
            if(num<2):
                rect = cv2.minAreaRect(cnt)# making min_area_rect aroung contours
                area_of_rect=rect[1][0]*rect[1][1]# area of contours
                box = cv2.boxPoints(rect)# recovering 4 point of min_rect
                box = np.int0(box)
                cv2.drawContours(mask, [box], 0, (100,100,255), 2)# drawing rectangle around contours
                #cv2.imshow('area_of',mask)
                #cv2.waitKey(100)
                rat=area_of_cnt/area_of_rect# taking ratio of (area of conotur/area of rectangle)
                if rat>=0.87:
                    print(rat,1)
                    shape_mat[ceny][cenx]=1
                else:
                    print(rat,0)
                    shape_mat[ceny][cenx]=0
