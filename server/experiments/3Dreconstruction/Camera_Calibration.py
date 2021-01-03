import csv
import argparse
import cv2
import numpy as np
import os
import timeout_decorator
import pickle

parser = argparse.ArgumentParser()
parser.add_argument('inputs', type=str, nargs='+')
parser.add_argument('--offset', type=int,default=0,help='time offset from video origin')
parser.add_argument('--output',type=str,default='camparam')
parser.add_argument('n',default=25,type=int,help='number of frames to use for parameter estimation')
parser.add_argument('--timeout',default=.1,type=float,help='time allowed to find checkerboard per frame')
parser.add_argument('--height',default=4,type=int,help='other dimension of the checkerboard')
parser.add_argument('--width',default=6,type=int,help='dimension of the checkerboard')
parser.add_argument('--frameskip',default=0,type=int,help='skip frames to not take redundent data')
parser.add_argument('--failskip',default=5,type=int,help='skip frames when frame times out')

args = parser.parse_args()
dumps = list()

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

@timeout_decorator.timeout(args.timeout)
def findChessboardCorners(frame):
    return cv2.findChessboardCorners(frame,(args.width,args.height),None)

for input in args.inputs:
    cap = cv2.VideoCapture(input)
    [cap.read() for _ in range(args.offset)]
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((6*4,3), np.float32)
    objp[:,:2] = np.mgrid[0:4,0:6].T.reshape(-1,2)

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    framecount = 0
    while framecount < args.n and cap.isOpened() :
        ret, frame = cap.read()
        if ret == True:
            gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            try:
                usefull, corners = findChessboardCorners(gray)
                if usefull:
                    objpoints.append(objp)
                    corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
                    imgpoints.append(corners2)
                    frame = cv2.drawChessboardCorners(frame, (4,6), corners2,usefull)
                    framecount += 1
                    print('{}/{}'.format(framecount,args.n))
                    [cap.read() for _ in range(args.frameskip)]
            except Exception as e:
                [cap.read() for _ in range(args.failskip)]
                # print(e)
                pass
            cv2.imshow('frame',frame)
        else:
            print('Did not find enough frames for input %s' % input)
            exit()

        if mask:= cv2.waitKey(1) & 0xFF:
            if mask == ord('q'):
                break
    cap.release()
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
    dumps.append([input, ret, mtx, dist, rvecs, tvecs])
os.mkdir(args.output)
for input, ret, mtx, dist, rvecs, tvecs in dumps:
    np.savez('{}/{}'.format(args.output,os.path.basename(input)),input=input,ret=ret,mtx=mtx,dist=dist,rvecs=rvecs,tvecs=tvecs)
cv2.destroyAllWindows()
