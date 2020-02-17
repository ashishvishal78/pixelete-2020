import cv2
import numpy as np
import cv2.aruco as aruco
import math
import serial
from time import sleep

roi = np.load('roi.npy')
cell_center = []
n = 9

cap = cv2.VideoCapture(1)

# starting serial
ser = serial.Serial('COM5', 9600)
sleep(2)
print("connected")
cap = cv2.VideoCapture(1)


def string_write(rm, lm, f, r):
    ser.write(str.encode(str(rm) + ' ' + str(lm) + ' ' + str(f) + ' ' + str(r) + ' 0\n'))
    hel = ser.readline()
    print("serial_read :", hel)
    pass


def find_boat_centre():
    while (True):
        print("here4")
        ret, img = cap.read()
        img = img[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]
        if (ret == False):
            break
        cv2.imshow('frame', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        arena = img
        # arena = frame[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]
        aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
        parameters = aruco.DetectorParameters_create()
        corners, ids, rejectedImgPoints = aruco.detectMarkers(arena, aruco_dict, parameters=parameters)
        if ids is None:
            continue
        img = cv2.circle(arena, (corners[0][0][0][0], corners[0][0][0][1]), 5, (0, 0, 255), 2)
        # cv2.imshow('img',img)
        # cv2.waitKey(0)
        # cv2.destroyWindow('img')
        print("corners")
        print(corners)
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
            return corners, (xc, yc)


def bot_vector(p, i, j):
    return (p[0][0][i][0] - p[0][0][j][0], p[0][0][i][1] - p[0][0][j][1])


# return direction in which boat have to move
def dirn_of_mov_vector(boat_centre, next_cell):
    # cell_cent=(next_cell)
    # boat_centre[0]-=roi[0]
    # boat_centre[1]-=roi[1]# source of error y and x
    return (next_cell[0] - boat_centre[0], next_cell[1] - boat_centre[1])


# determine angle between boat direction and direction of movemnet
def cross_pro(dirn_of_mov=[1, 1], boat_vector=[0, 1]):
    a = np.array(dirn_of_mov)
    b = np.array(boat_vector)
    # print(np.cross(a, b))
    mag = (math.sqrt(dirn_of_mov[0] ** 2 + dirn_of_mov[1] ** 2)) * (
        math.sqrt(boat_vector[0] ** 2 + boat_vector[1] ** 2))
    # print(math.degrees(math.asin(np.cross(a,b)/mag)))
    return (math.degrees(math.asin(np.cross(a, b) / mag)))


def dot_pro(dirn_of_mov, boat_vector):
    a = np.array(dirn_of_mov)
    b = np.array(boat_vector)
    # print(np.cross(a, b))
    mag = (math.sqrt(dirn_of_mov[0] ** 2 + dirn_of_mov[1] ** 2)) * (
        math.sqrt(boat_vector[0] ** 2 + boat_vector[1] ** 2))
    # print(math.degrees(math.asin(np.cross(a,b)/mag)))
    return (math.degrees(math.acos(np.dot(a, b) / mag)))


def find_dis(boat_centre, next_cell):
    # cell_cent=cell_center[next_cell]
    print("next_cell :", next_cell, boat_centre)
    return math.sqrt(((next_cell[0] - boat_centre[0]) ** 2) + ((next_cell[1] - boat_centre[1]) ** 2))


def return_min_path(path_to_travel, n=9):
    ans = []
    ans.append(path_to_travel[0])
    for i in range(len(path_to_travel) - 2):
        if (abs(path_to_travel[i] - path_to_travel[i + 1]) == abs(path_to_travel[i + 1] - path_to_travel[i + 2])):
            continue
        else:
            ans.append(path_to_travel[i + 1])
    ans.append(path_to_travel[len(path_to_travel) - 1])
    print(ans)
    return ans


KP = 22

KD = 40
KI = 0
MaxSpeedLine = 70
LeftBaseSpeedLine = 55
RightBaseSpeedLine = 48
# Initializatins
prev_error = 0
rightMotorSpeed = 0
leftMotorSpeed = 0
motor_speed = 0
# desired_value=(200,100)# set desired value according to camera
cell_center.append([0, 0])
for i in range(n):
    for j in range(n):
        cell_center.append([(roi[2] // n) * (j + (1 / 2)), (roi[3] // n) * (
                    i + (1 / 2))])  # finding centres of each cells of arena row=r[1] col=col[1]

path_to_travel = [1, 6, 11, 12, 13, 14, 15, 10, 5, 4, 3, 2, 7, 12, 17, 22, 23, 24, 25]
min_path = return_min_path(path_to_travel)
set_point = []
print(min_path)
for i in min_path:
    set_point.append(cell_center[i])

print(set_point)
i = 0

while (True):
    print("set point :", set_point[i])
    min_thresh_dis = roi[2]//(2.5* n)
    p, center_of_bot = find_boat_centre()
    print("here3")
    bv = bot_vector(p, 0, 3)
    dv = dirn_of_mov_vector(center_of_bot, set_point[i])
    angle_sign = cross_pro(dv, bv)
    angle_mag = dot_pro(dv, bv)
    print(angle_mag, angle_sign)
    print("i :", i)
    p, b_c = find_boat_centre()
    dis = find_dis(b_c, set_point[i])
    print(dis)
    # integral = integral_prior + error * iteration_time
    # derivative = (error – prev_error) / iteration_time
    angle_sign = cross_pro(dv, bv)
    angle_mag = dot_pro(dv, bv)

    error = angle_mag
    error = error * 3.14 / 180
    if (int(angle_sign) <= 0):
        error = -error
    print("error :", error)
    motor_speed = KP * error + KD * (error - prev_error)
    motor_speed = int(motor_speed)
    p, b_c = find_boat_centre()
    dis = find_dis(b_c, set_point[i])
    if (dis < min_thresh_dis):
        string_write(0, 0, 0, 0)
        i = i + 1
        continue
    rightMotorSpeed = RightBaseSpeedLine - motor_speed
    leftMotorSpeed = LeftBaseSpeedLine + motor_speed

    if (rightMotorSpeed > MaxSpeedLine): rightMotorSpeed = MaxSpeedLine
    if (leftMotorSpeed > MaxSpeedLine): leftMotorSpeed = MaxSpeedLine
    if (rightMotorSpeed < 0): rightMotorSpeed = 0
    if (leftMotorSpeed < 0): leftMotorSpeed = 0
    print('L:', leftMotorSpeed, 'R:', rightMotorSpeed)
    string_write(leftMotorSpeed, rightMotorSpeed, 1, 1)
    prev_error = error