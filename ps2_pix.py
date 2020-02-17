import numpy as np
import cv2
import cv2.aruco as aruco
import serial
import heapq
import math
import time
from time import sleep

# loading caliberataed things
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
shape_mat = np.load('shape_mat.npy')
color_mat = np.load('color_mat.npy')
white_mat = np.load('white_mat.npy')
roi = np.load('roi.npy')
qwerty1=roi[0]
qwerty2=roi[1]
qwerty3=roi[2]
qwerty4=roi[3]
print(roi)
# taking padding across arena
roi[0]-=0
roi[1]-=0
roi[2]+=0
roi[3]+=0
print("everything loaded")
print(color_mat)
print(shape_mat)
print(white_mat)
print("roi :",roi)
roi_1=[qwerty1,qwerty2,qwerty3,qwerty4]
print("roi_1 :",roi_1)

print(color_mat)
print(shape_mat)
print(white_mat)
#color_mat[3][2]=0
#shape_mat[3][2]=0

#print(qwerty1,qwerty2,qwerty3,qwerty4)
# starting serial
ser = serial.Serial('COM5', 9600)
sleep(1)
print("connected")
cap = cv2.VideoCapture(1)
# variable declaration
global box_grabbed
box_grabbed=False# for box grabbing
cols = 1
n = 9
rows = n * n + 1
total_cells = n * n + 1


cell_adj = [[0 for i in range(1)] for j in range(rows)]
cell_wei = [[0 for i in range(1)] for j in range(rows)]
cell_center = []  # for storing center of cell
cell_center.append([0, 0])
# numpy array declaration
cell_cord = []
cell_cord.append((0, 0))  # as 0 is not numbering of any cell
cell_num = np.zeros((n, n), dtype=np.int16)
weight_mat = np.zeros((n, n), dtype=np.int16)  # for no of corners
cnt = 1
ret,frame=cap.read()
cv2.rectangle(frame,(roi[0],roi[1]),(roi[0]+roi[2],roi[1]+roi[3]),(255,255,255),2)
cv2.rectangle(frame,(roi_1[0],roi_1[1]),(roi_1[0]+roi_1[2],roi_1[1]+roi_1[3]),(255,255,255),2)
cv2.imshow('frame',frame)
#cv2.waitKey(0)

# numbering of cells of arena box
for i in range(n):
    for j in range(n):
        cell_num[i][j] = cnt  # cell numbering
        cnt += 1
        cell_cord.append((i, j))  # storing value of rows and columns in cell_id
        cell_center.append([((roi_1[2] // n) * (j + (1 / 2)))+0, ((roi_1[3] // n) * (i + (1 / 2)))+0])
        #ret,frame=cap.read()
        #cv2.circle(frame,((int((roi_1[2] // n) * (j + (1 / 2)))+50, int((roi_1[3] // n) * (i + (1 / 2)))+50)),3,(255,255,255),2)
        #cv2.imshow('frame',frame)
        #cv2.waitKey(0)
        # finding centres of each cells of arena row=r[1] col=col[1]

print(cell_num)
print(cell_cord)
print(cell_center)

# finding cordinate of any cell
def return_cord(cell_id, n=9):
    for i in range(n):
        for j in range(n):
            if (cell_num[i][j] == cell_id):
                return (i, j)

# updating color of horcurex and jail
def update_color_shape(cell_id, lwr, upr, num):
    ret, frame = cap.read()
    arena = frame[int(roi_1[1]):int(roi_1[1] + roi_1[3]), int(roi_1[0]):int(roi_1[0] + roi_1[2])]
    mask = cv2.inRange(arena, lwr, upr)
    cv2.imshow('mask', mask)
    kernel = np.ones((5, 5), np.uint8)
    #mask = cv2.dilate(mask, kernel, iterations=4)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)# removing small noise in mask
    cv2.imshow('mask1',mask)
    #cv2.waitKey(0)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.destroyWindow('mask')
    # for ignoring small contours
    total_cnt_area = 0
    no_of_cnt = 0
    for cnt in contours:
        total_cnt_area += cv2.contourArea(cnt)
        no_of_cnt += 1

    avg_cnt_area = total_cnt_area / no_of_cnt
    thresh_cnt_area = avg_cnt_area / 4
    for cnt in contours:
        area_of_cnt = cv2.contourArea(cnt)
        if (area_of_cnt > thresh_cnt_area):
            cen = cv2.moments(cnt)
            cenx = int(cen["m10"] / cen["m00"])
            ceny = int(cen["m01"] / cen["m00"])
            cenx = cenx // col
            ceny = ceny // row
            print("ceny cenx ",ceny,cenx)
            print("cell id : ,cell_num ",cell_id,cell_num[ceny][cenx])
            if (cell_id == cell_num[ceny][cenx]):
                color_mat[ceny][cenx] = num
                # shape recog
                rect = cv2.minAreaRect(cnt)  # making min_area_rect aroung contours
                area_of_rect = rect[1][0] * rect[1][1]  # area of contours
                box = cv2.boxPoints(rect)  # recovering 4 point of min_rect
                box = np.int0(box)
                cv2.drawContours(mask, [box], 0, (0, 255, 0), 2)  # drawing rectangle around contours
                cv2.imshow('area_of',mask)
                #cv2.waitKey(0)
                rat = area_of_cnt / area_of_rect  # taking ratio of (area of conotur/area of rectangle)
                if rat >= 0.83:
                    print(rat, 1)
                    shape_mat[ceny][cenx] = 1
                else:
                    '''(x, y), radius = cv2.minEnclosingCircle(cnt)
                    center = (int(x), int(y))
                    radius = int(radius)
                    #cv2.circle(arena, center, radius, (0, 255, 0), 2)
                    area_of_circle=3.14*(radius**2)
                    rat_cir=area_of_cnt/area_of_circle
                    print(rat, 0)
                    if(rat_cir>rat):
                        shape_mat[ceny][cenx] = 0
                    else:
                        shape_mat[ceny][cenx]=1'''
                    print(rat,0)
                    shape_mat[ceny][cenx]=0
                return True
    return False

def find_boat_centre():
    while (True):
        print("aruco not detected")
        ret, img = cap.read()
        if (ret == False):
            break
        cv2.imshow('frame', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        arena = img[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]
        # zcv2.imshow('arena',arena)
        aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
        parameters = aruco.DetectorParameters_create()
        corners, ids, rejectedImgPoints = aruco.detectMarkers(arena, aruco_dict, parameters=parameters)
        if ids is None:
            ser.write(b's')
            continue
        #img = cv2.circle(arena, (corners[0][0][0][0], corners[0][0][0][1]), 5, (0, 0, 255), 2)
        #cv2.imshow('img', img)
        #cv2.waitKey(10)
        #cv2.destroyWindow('img')
        # print("corners")
        # print(corners)
        for x in range(0, ids.shape[0]):
            p1 = max(corners[x][0][0][0], corners[x][0][1][0],
                     corners[x][0][2][0], corners[x][0][3][0])
            p2 = min(corners[x][0][0][0], corners[x][0][1][0],
                     corners[x][0][2][0], corners[x][0][3][0])
            q1 = max(corners[x][0][0][1], corners[x][0][1][1],
                     corners[x][0][2][1], corners[x][0][3][1])
            q2 = min(corners[x][0][0][1], corners[x][0][1][1],
                     corners[x][0][2][1], corners[x][0][3][1])
            xc = int(p2 + abs(p1 - p2) / 2)
            yc = int(q2 + abs(q1 - q2) / 2)
            return corners, [xc, yc]

# for update of weights of which is decided by color and shape of weapons
def update_weight(var_cell_wei, shape, color, n=9):
    u_range = n * n + 1  # 82 in case of n=9
    for i in range(1, u_range, 1):
        r,c=return_cord(i)
        if(color_mat[r][c]==2 or color_mat[r][c]==3 or color_mat[r][c]==5):
            for num in cell_adj[i]:
                if(num!=0):
                    var_cell_wei[i].append(1000)
        else:
            for num in cell_adj[i]:
                print(num)
                if (num == 0):
                    continue
                r, c = return_cord(num)
                if(color_mat[r][c]==2 or color_mat[r][c]==3 or color_mat[r][c]==5):# source of error
                        var_cell_wei[i].append(1000)
                else:
                    r, c = return_cord(num)
                    if (color_mat[r][c] == color and shape_mat[r][c] == shape):
                        var_cell_wei[i].append(0)  # putting 0 for same color and shape
                    else:
                        var_cell_wei[i].append(1)  # putting 1 for different shape or color
    return var_cell_wei


def path(source, destination, wei=cell_wei, n=9):
    path = []
    par = []
    dis = []
    vis = []
    nodes = n * n + 1
    for i in range(nodes):
        dis.append(1000000)
        vis.append(False)
        par.append(-1)
    dis[source] = 0
    par[source] = 0
    q = []
    heapq.heappush(q, (0, source))
    while q:
        next_item = heapq.heappop(q)
        node = next_item[1]
        # print(node)
        if vis[node]:
            continue
        vis[node] = True
        i = 1
        flag = False
        for item in cell_adj[node]:
            if item != 0:
                if (dis[item]>(dis[node] + wei[node][i])):
                    dis[item] = dis[node] + wei[node][i]
                    par[item] = node
                    heapq.heappush(q, (dis[item], item))
                i = i + 1
    # print("parent")
    # print(destination)
    if (par[destination] == -1):
        return path
    path.append(destination)
    while (par[destination] != 0):
        # print(par[destination])
        path.append(par[destination])
        destination = par[destination]
    path.reverse()
    # print(path)
    return path

# to connect a cell to its four neighbour whichever exists
def connect_edges(cell_id):
    r, c = return_cord(cell_id)
    upx = r - 1
    dwx = r + 1
    lefy = c - 1
    ry = c + 1
    if (upx >= 0):
        cell_adj[cell_id].append(cell_num[upx][c])
        cell_wei[cell_id].append(1)
    if (dwx < n):
        cell_adj[cell_id].append(cell_num[dwx][c])
        cell_wei[cell_id].append(1)
    if (lefy >= 0):
        cell_adj[cell_id].append(cell_num[r][lefy])
        cell_wei[cell_id].append(1)
    if (ry < n):
        cell_adj[cell_id].append(cell_num[r][ry])
        cell_wei[cell_id].append(1)

# to checj if jail is enclosed by weapons
def check(prison):
    r, c = return_cord(prison)
    upx = r - 1
    dwx = r + 1
    lefy = c - 1
    ry = c + 1
    if (upx >= 0):
        if (color_mat[upx][c] <2 and color_mat[upx][c] >= 0):
            return True
    if (dwx < n):
        if (color_mat[dwx][c] <2 and color_mat[dwx][c] >= 0):
            return True
    if (lefy >= 0):
        if (color_mat[r][lefy] <2 and color_mat[r][lefy] >= 0):
            return True
    if (ry < n):
        if (color_mat[r][ry] <2 and color_mat[dwx][c] >= 0):
            return True
    return False

def remove_edges(cell_id):
    if cell_adj[cell_id] is None:
        return
    while (len(cell_adj[cell_id]) > 1):
        cell_adj[cell_id].pop()
        cell_wei[cell_id].pop()
    '''
    for i in range(len(cell_wei[cell_id])):
        if (i != 0):
            cell_wei[cell_id][i]=1000'''
# return front direction of boat
def bot_vector(p, i, j):
    return (p[0][0][i][0] - p[0][0][j][0], p[0][0][i][1] - p[0][0][j][1])

# return direction in which boat have to move
def dirn_of_mov_vector(boat_centre, next_cell):
    return (next_cell[0] - boat_centre[0], next_cell[1] - boat_centre[1])

# return distance between boat_centre and cell_cent
def find_dis(boat_centre, next_cell):
    print("next_cell :", next_cell, boat_centre)
    return math.sqrt(((next_cell[0] - boat_centre[0]) ** 2) + ((next_cell[1] - boat_centre[1]) ** 2))

# determine angle between boat direction and direction of movemnet
def cross_pro(dirn_of_mov=[1, 1], boat_vector=[0, 1]):
    a = np.array(dirn_of_mov)
    b = np.array(boat_vector)
    # print(np.cross(a, b))
    mag = (math.sqrt(dirn_of_mov[0] ** 2 + dirn_of_mov[1] ** 2))*(math.sqrt(boat_vector[0] ** 2 + boat_vector[1] ** 2))
    # print(math.degrees(math.asin(np.cross(a,b)/mag)))
    value=np.cross(a, b)/mag
    if(int(value)>=1):
        value=1
    if(int(value)<=-1):
        value=-1
    return (math.degrees(math.asin(value)))

# determining measure of angle to turn
def dot_pro(dirn_of_mov, boat_vector):
    a = np.array(dirn_of_mov)
    b = np.array(boat_vector)
    # print(np.cross(a, b))
    mag = (math.sqrt(dirn_of_mov[0] ** 2 + dirn_of_mov[1] ** 2)) * (math.sqrt(boat_vector[0] ** 2 + boat_vector[1] ** 2))
    # print(math.degrees(math.asin(np.cross(a,b)/mag)))
    value = np.dot(a, b) / mag
    if (int(value) >= 1):
        value = 1
    if (int(value) <= -1):
        value = -1
    return (math.degrees(math.acos(value)))

def one_box_prev(go_path,box_grabbed):
    for box in go_path:
        print("visiting :", box)
        dis = 10000
        min_thres_dis = roi[2]//(3*n)
        destination = cell_center[box]
        print("box :", box)
        while (dis > min_thres_dis):  # threshold distance by calibertaion
            # ret,frame=cap.read()
            print("dis :", dis)
            p, b_c = find_boat_centre()
            bv = bot_vector(p, 0, 3)
            dv = dirn_of_mov_vector(b_c, destination)
            angle_sign = cross_pro(dv,bv)
            angle_mag = dot_pro(dv, bv)
            # print("ang :", angle)
            while (int(angle_mag) > 6 or int(angle_mag) < -6):
                print("ang :", angle_mag)
                print("box_grab:",box_grabbed)
                if (int(angle_sign) <= 0):  # small right turn
                    if (box_grabbed):
                        ser.write(b'R')
                        sleep(.2)
                    else:
                        ser.write(b'r')
                        # sleep(.2)
                elif (int(angle_sign) > 0):
                    if (box_grabbed):
                        ser.write(b'L')
                        sleep(.2)
                    else:
                        ser.write(b'l')
                        # sleep(.2)
                p, b_c = find_boat_centre()
                dis = find_dis(b_c, destination)
                if (dis < min_thres_dis):
                    break
                bv = bot_vector(p, 0, 3)
                dv = dirn_of_mov_vector(b_c, destination)
                angle_sign = cross_pro(dv, bv)
                angle_mag = dot_pro(dv, bv)
            ser.write(b's')
            sleep(0.1)
            # arduino code to move forward little bit
            ser.write(b'f')
            sleep(.30)
            ser.write(b's')
            sleep(.05)
            p, b_c = find_boat_centre()
            # print("bc :",b_c)
            dis = find_dis(b_c, destination)

# locomaion of boat
def bot_movement(go_path,box_grabbed):
    flag2 = False  # if true then to move hoop down that is next cell is green
    flag = False  # if true then move hoop up to that is next cell is blue
    for box in go_path:
        print("visiting :", box)
        dis = 10000
        if (box == go_path[0]):
            continue
        min_thres_dis = roi_1[2]/(2.1*n)  # distance is less than length_of_one_side/3
        # print("min_threshold_dis :",min_thres_dis)
        destination = cell_center[box]
        print("box :", box)
        # print("destinstion :",destination)
        if (box == go_path[len(go_path) - 1]):
            r, c = return_cord(box)
            ceny=destination[1]
            cenx=destination[0]
            # find centre of white box and making it as a destination
            ret, img = cap.read()
            arena = img[int(roi_1[1]):int(roi_1[1] + roi_1[3]), int(roi_1[0]):int(roi_1[0] + roi_1[2])]
            mask_w = cv2.inRange(arena, lw, uw)
            contours, _ = cv2.findContours(mask_w, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            # removing aruco white mask
            #p,bc=find_boat_centre()
            #dis_of_aruco=find_dis(bc,p[0][0][0])
            # for ignoring small contours
            total_cnt_area = 0
            no_of_cnt = 0
            for cnt in contours:
                total_cnt_area += cv2.contourArea(cnt)
                no_of_cnt += 1
            avg_cnt_area = total_cnt_area / no_of_cnt
            thresh_cnt_area = avg_cnt_area / 4

            for cnt in contours:
                area_of_cnt = cv2.contourArea(cnt)
                if (area_of_cnt > thresh_cnt_area):
                    cen = cv2.moments(cnt)
                    cenx = int(cen["m10"] / cen["m00"])
                    ceny = int(cen["m01"] / cen["m00"])
                    c1 = cenx // col
                    r1 = ceny // row
                    print("on box prev :",r1,c1)
                    if (r1 == r and c1 == c):
                        print("matched white box")
                        cenx+=0
                        ceny+=0
                        #flag = True
                        break
            if (color_mat[r][c] == 2):
                flag2 = False
                flag = True
            elif(color_mat[r][c]==3 or color_mat[r][c]==5):
                flag=False
                flag2=True
                destination = np.array([cenx, ceny])
            min_thres_dis = (roi_1[2]//(1.6*n))
            #if flag2 == True:
             #   destination = np.array([cenx,ceny])
        while (dis > min_thres_dis):  # threshold distance by calibertaion
            print("dis :", dis)
            p, b_c = find_boat_centre()
            bv = bot_vector(p, 0, 3)
            dv = dirn_of_mov_vector(b_c, destination)
            angle_sign = cross_pro(dv,bv)
            angle_mag = dot_pro(dv, bv)
            #print("ang :", angle)
            while (int(angle_mag) > 6 or int(angle_mag) < -6):
                #print("ang :", angle_mag)
                print("box_grabbed:",box_grabbed)
                if (int(angle_sign) <= 0):  # small right turn
                    if(box_grabbed):
                        ser.write(b'R')
                        #sleep(.2)
                    else:
                        ser.write(b'r')
                        #sleep(.2)
                elif (int(angle_sign) >0):
                    if (box_grabbed):
                        ser.write(b'L')
                        #sleep(.2)
                    else:
                        ser.write(b'l')
                        #sleep(.2)
                p, b_c = find_boat_centre()
                bv = bot_vector(p, 0, 3)
                dv = dirn_of_mov_vector(b_c, destination)
                angle_sign = cross_pro(dv, bv)
                angle_mag = dot_pro(dv, bv)
            ser.write(b's')
            sleep(0.1)
            # arduino code to move forward little bit
            ser.write(b'f')
            sleep(.32)
            ser.write(b's')
            sleep(.05)
            p, b_c = find_boat_centre()
            # print("bc :",b_c)
            dis = find_dis(b_c, destination)
    print(flag)
    print(flag2)
    if(flag2):
        box_grabbed = True
        ser.write(b'D')
        sleep(1)
    elif(flag):
        box_grabbed = False
        ser.write(b'U')
        sleep(1)
    print("box_grabbed:",box_grabbed)
    return box_grabbed

# finding horcurex and jail
horcruxes = []
green_cell= []
free_jail = []  # 3 jail together
closed_jail = []  # 1 jail closed
azkaban_prison = []
weapons = []

for i in range(n):
    for j in range(n):
        print(color_mat[i][j])
        if (color_mat[i][j] == 3 and white_mat[i][j]==10):  # white present on horcruex
            horcruxes.append(cell_num[i][j])
        if (color_mat[i][j] == 2 and white_mat[i][j]==-1):  # jail
            print(check(cell_num[i][j]))
            if (check(cell_num[i][j])):
                free_jail.append(cell_num[i][j])
            else:
                closed_jail.append(cell_num[i][j])
        if (color_mat[i][j] == 5):  # weapons
            weapons.append(cell_num[i][j])
        if (color_mat[i][j] == 3):
            green_cell.append(cell_num[i][j])

print("horcurex :", horcruxes)
print("free_jail :", free_jail)
print('closed_jail :', closed_jail)
print("green_cell", green_cell)
print("weapons :", weapons)

# making cell_wei and cell_adj
for i in range(n):
    for j in range(n):
        upx = i - 1
        dwx = i + 1
        lefy = j - 1
        ry = j + 1
        if (color_mat[i][j] < 2):
            if (upx >= 0):
                cell_adj[cell_num[i][j]].append(cell_num[upx][j])
                cell_wei[cell_num[i][j]].append(1)
            if (dwx < n):
                cell_adj[cell_num[i][j]].append(cell_num[dwx][j])
                cell_wei[cell_num[i][j]].append(1)
            if (lefy >= 0):
                cell_adj[cell_num[i][j]].append(cell_num[i][lefy])
                cell_wei[cell_num[i][j]].append(1)
            if (ry < n):
                cell_adj[cell_num[i][j]].append(cell_num[i][ry])
                cell_wei[cell_num[i][j]].append(1)
        if (color_mat[i][j] ==2 or color_mat[i][j]==3 or color_mat[i][j]==5):
            if (upx >= 0):
                cell_adj[cell_num[i][j]].append(cell_num[upx][j])
                cell_wei[cell_num[i][j]].append(1000)
            if (dwx < n):
                cell_adj[cell_num[i][j]].append(cell_num[dwx][j])
                cell_wei[cell_num[i][j]].append(1000)
            if (lefy >= 0):
                cell_adj[cell_num[i][j]].append(cell_num[i][lefy])
                cell_wei[cell_num[i][j]].append(1000)
            if (ry < n):
                cell_adj[cell_num[i][j]].append(cell_num[i][ry])
                cell_wei[cell_num[i][j]].append(1000)
print(cell_adj)

horcruex_counter = 0
jail_counter = 0
weapons_counter = 0
empty_jail = []
occupied_jail=[]
left_horcruex = []
left_weapons = []
vis_horcruex = [] # bool var to maintain visited of horcruex
vis_weapons = []
for i in range(n * n + 1):
    vis_horcruex.append(False)
    vis_weapons.append(False)


row = math.ceil(roi_1[3] / n)
col = math.ceil(roi_1[2] / n)
print(row, col)
print(roi[2])

for boxes in (horcruxes):
    p, bc = find_boat_centre()
    print(bc)
    bc[0]-=0
    bc[1]-=0
    cellid = cell_num[int(bc[1] // row)][int(bc[0] // col)]
    print(cellid)
    # print()
    print(cell_num[(bc[1] // row)][(bc[0] // col)], boxes)
    path_to_horcruex = path(cell_num[(bc[1] // row)][(bc[0] // col)], boxes)
    print("path_to_horcurex :", path_to_horcruex)
    box_grabbed=bot_movement(path_to_horcruex,box_grabbed)
    ser.write(b's')
    #connect_edges(boxes)
    time.sleep(1)

    p, bc = find_boat_centre()
    bc[0] -= 0
    bc[1] -= 0
    cellid = cell_num[int(bc[1] // row)][int(bc[0] // col)]
    print(cellid)
    path_to_jail = path(cell_num[(bc[1] // row)][(bc[0] // col)],free_jail[jail_counter])  # path from horcruex to jail
    print("path_to_jail :", path_to_jail)
    box_grabbed=bot_movement(path_to_jail,box_grabbed)
    ser.write(b's')
    sleep(0.4)
    ser.write(b'N')
    sleep(2)
    ser.write(b'F')
    sleep(0.2)
    ser.write(b's')
    sleep(0.4)
    new_go_path=[]
    if(len(path_to_jail)>=3):
        new_go_path.append(path_to_jail[len(path_to_jail)-3])# modify later for main ps value of -3
    else:
        new_go_path.append(path_to_jail[len(path_to_jail) - 2])
    print("back path :", new_go_path)
    one_box_prev(new_go_path,box_grabbed)
    #ser.write(b'b')
    #sleep(1.8)
    ser.write(b's')
    sleep(0.2)
    jail_counter += 1
    horcruex_counter += 1
    if (jail_counter == len(free_jail)):
        break
    if (horcruex_counter == len(horcruxes)):
        break
    #remove_edges(free_jail[jail_counter])

sleep(8)
for i in range(len(green_cell)):
    if(update_color_shape(green_cell[i],lr,ur,0)):
        continue
    elif(update_color_shape(green_cell[i],ly,uy,1)):
        continue
print("updated after 4 horcruex")
print("color and shape mat")
print(color_mat,shape_mat)

for weap in weapons:
    p, bc = find_boat_centre()
    bc[0] -= 0
    bc[1] -= 0
    cellid = cell_num[int(bc[1] // row)][int(bc[0] // col)]
    print(cellid)
    path_to_weapons=path(cell_num[(bc[1] // row)][(bc[0] // col)],weap)
    print("path_to_weapons",path_to_weapons)
    box_grabbed=bot_movement(path_to_weapons,box_grabbed)
    ser.write(b's')
    sleep(2)
    ser.write(b'G')
    sleep(2)
    ser.write(b'g')
    sleep(0.2)
    back_path=[]
    if (len(path_to_weapons) >= 3):
        back_path.append(path_to_weapons[len(path_to_weapons) - 3])  # modify later for main ps value of -3
    else:
        back_path.append(path_to_weapons[len(path_to_weapons) - 2])
    #back_path.append(path_to_weapons[len(path_to_weapons)-2])
    print("back_path", back_path)
    one_box_prev(back_path,box_grabbed)
    ser.write(b's')
    sleep(8)
    if(update_color_shape(weap,lr,ur,0)):
        print("red matched")
    elif(update_color_shape(weap,ly,uy,1)):
        print("yellow_matched")
    print(color_mat,shape_mat)

    p, bc = find_boat_centre()
    bc[0] -= 0
    bc[1] -= 0
    cellid = cell_num[int(bc[1] // row)][int(bc[0] // col)]
    print(cellid)
    path_to_weapons = path(cell_num[(bc[1] // row)][(bc[0] // col)], weap)
    box_grabbed = bot_movement(path_to_weapons, box_grabbed)
    ser.write(b's')
    matched=False
    print("color_mat")
    print(color_mat)
    print("shape_mat")
    print(shape_mat)
    for boxes in green_cell:
        r,c=return_cord(boxes)
        r1,c1=return_cord(weap)
        print("r1,c1",r1,c1)
        print("r c", r, c)
        print("matching", vis_horcruex)
        if((color_mat[r][c]==color_mat[r1][c1] and shape_mat[r][c]==shape_mat[r1][c1])):
            if(vis_horcruex[boxes]==False):
                print("matched")
                matched=True
                weapons_counter+=1
                vis_horcruex[boxes]=True
                vis_weapons[weap]=True
                var_cell_wei = [[0 for i in range(1)] for j in range(rows)]
                var_cell_wei=update_weight(var_cell_wei,shape_mat[r1][c1],color_mat[r1][c1])
                print("var_cell_wei",var_cell_wei)
                path_to_horcruex=path(weap,boxes,wei=var_cell_wei)
                print("path_to_horcruex", path_to_horcruex)
                box_grabbed=bot_movement(path_to_horcruex,box_grabbed)
                ser.write(b's')
                sleep(0.2)
                ser.write(b'E')
                sleep(2)
                ser.write(b'e')
                sleep(0.2)
                # changing color of horcruex
                color_mat[r][c]=3
                # update wei of weapons
                ser.write(b'U')
                box_grabbed=False
                sleep(1)
                break
        else:
            print("debug")
            print(color_mat[r][c],color_mat[r1][c1])
            print(shape_mat[r][c],shape_mat[r1][c1])
    if(matched):
        print("matched")
        continue
    else:
        ser.write(b'U')
        box_grabbed = False
        r1, c1 = return_cord(weap)
        color_mat[r1][c1] = 5
        one_box_prev(back_path, box_grabbed)
        ser.write(b's')
        print("not_matched")
        left_weapons.append(weap)
        weapons.append(weap)


ser.write(b'U')
sleep(2)
ser.write(b'N')
sleep(4)
ser.write(b'F')
sleep(0.2)
cap.release()
cv2.destroyAllWindows()