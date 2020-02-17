import cv2
import numpy as np
import all_func as af
import time
import math
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
    #take ROI
    r = cv2.selectROI(img)  # return x,y,w,h
    np.save('roi', r)
    print("roi :",r)
    #r=np.load('roi.npy')
    arena = img[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]

    n = 9
    LRR = [255, 255, 255]
    URR = [0, 0, 0]
    LRG = [255, 255, 255]
    URG = [0, 0, 0]
    LRB = [255, 255, 255]
    URB = [0, 0, 0]
    LRY = [255, 255, 255]
    URY = [0, 0, 0]
    LRW = [255, 255, 255]
    URW = [0, 0, 0]

    # range for lower and upper red
    LRR, URR = af.clr_range(LRR, URR, arena)
    print(LRR)
    print(URR)
    np.save('lrr', LRR)
    np.save('urr', URR)
    # range for lower and upper yellow
    LRY, URY = af.clr_range(LRY, URY, arena)
    print(LRY)
    print(URY)
    np.save('lry', LRY)
    np.save('ury', URY)
    # range for lower and upper blue
    LRB, URB = af.clr_range(LRB, URB, arena)
    print(LRB)
    print(URB)
    np.save('lrb', LRB)
    np.save('urb', URB)
    # range for lower and upper green
    LRG, URG = af.clr_range_green(LRG, URG, arena)
    print(LRG)
    print(URG)
    np.save('lrg', LRG)
    np.save('urg', URG)
    # range for lower and upper white
    LRW, URW = af.clr_range(LRW, URW, arena)
    print(LRW)
    print(URW)
    np.save('lrw', LRW)
    np.save('urw', URW)
    low = [LRR, LRY, LRB, LRW, LRG]
    high = [URR, URY, URB, URW, URG]

    # taking each square box separately
    leng = arena.shape
    row = math.ceil(leng[0] / n)
    col = math.ceil(leng[1] / n)
    #print(row)
    #print(col)
    '''
    LRR = np.load('lrr.npy')
    URR = np.load('urr.npy')
    LRY = np.load('lry.npy')
    URY= np.load('ury.npy')
    LRB= np.load('lrb.npy')
    URB= np.load('urb.npy')
    LRG= np.load('lrg.npy')
    URG= np.load('urg.npy')
    LRW= np.load('lrw.npy')
    URW= np.load('urw.npy')
    '''
    # numpy array declaration
    shape_mat = np.full((n, n),-1)  # for shape
    color_mat = np.full((n, n),2)  # for color
    white_mat=np.full((n,n),-1)
    # color recognise and shape detect
    af.recog_col(color_mat, shape_mat, row, col, LRR, URR, arena, 0)
    af.recog_col(color_mat, shape_mat, row, col, LRY, URY, arena, 1)

    af.recog_col(color_mat, shape_mat, row, col, LRW, URW, arena, 5)
    af.recog_col(color_mat, shape_mat, row, col, LRG, URG, arena, 3)
    af.recog_col(color_mat, shape_mat, row, col, LRB, URB, arena, 2)
    af.recog_col(white_mat, shape_mat, row, col, LRW, URW, arena, 10)

    print(color_mat)
    print(shape_mat)
    print(white_mat)
    np.save('color_mat.npy',color_mat)
    np.save('shape_mat.npy', shape_mat)
    np.save('white_mat.npy', white_mat)
    cap.release()
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    break