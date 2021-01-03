import cv2
import numpy as np

from math import *

from functools import reduce
from operator import and_
from itertools import *
from more_itertools import *

from time import time

import argparse
parser = argparse.ArgumentParser(description='Track the highest value point in videos.')
parser.add_argument('inputs', type=str, nargs=3,)
parser.add_argument('offsets', type=int,nargs='*',default=[0,0,0])
parser.add_argument('--record',type=str)
parser.add_argument('--length',type=int,default=inf)

args = parser.parse_args()
print(args)

def delta_time():
    return difference(repeatfunc(time),initial=time()) 

if args.record:
    data = []
offsets = args.offsets

caps = [cv2.VideoCapture(cap) for cap in args.inputs]

# Align tracks
for cap,offset in zip(caps,offsets):
    for i in range(offset):
        cap.read()

pause = True
lasts = [None] * len(caps)
frames = [cap.read()[1] for cap in caps] #Reads the first frame to later acquire dimensions

def marker(frame,point,z=0,size=2,value=0):
    x,y = int(point[0]),int(point[1])
    xcord = list(range(x-size,x+size))
    ycord = list(range(y-size,y+size))
    for point in product(xcord,ycord):
        if point[0]>=0 and point[1]>=0 and point[0]<frame.shape[0] and point[1]<frame.shape[1]:
            frame[point]=value
    return frame

def circular_mask(shape,center,radius):
    X, Y = np.ogrid[:shape[0], :shape[1]]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y - center[1])**2)
    mask = dist_from_center <= radius
    return mask

def dist_mask(shape,center):
    X, Y = np.ogrid[:shape[0], :shape[1]]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    hyp = np.max(dist_from_center)
    return dist_from_center/hyp

def register(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_RBUTTONDOWN:
        for box,i in zip(param,range(len(param))):
            a,b,c,d = box
            if a<x<c and b<y<d:
                print(box)
                if event == cv2.EVENT_LBUTTONDOWN:
                    lasts[i] = (y-b,x-a)
                if event == cv2.EVENT_RBUTTONDOWN:
                    lasts[i] = None

def deform(frame):
    frame = np.array(frame,dtype=float)
    frame = frame[:,:,0] + frame[:,:,1] + frame[:,:,2]
    return frame / (255.0 * 3)

def find(frame,last):
    mask = circular_mask(frame.shape,last,16)
    frame[~mask] = 0
    frame -= dist_mask(frame.shape,last)
    return np.unravel_index(frame.argmax(),frame.shape)

while reduce(and_, chain(
            (cap.isOpened() for cap in caps),
            (offset < args.length for offset in offsets) 
        )
    ):
    if not pause:
        frames = [cap.read()[1] for cap in caps]
        offsets = [offset+1 for offset in offsets]

    for frame,last,i in zip(frames,lasts,range(3)):
        if last:
            lasts[i] = find(deform(frame),last)

    displayed = frames
    for frame,last in zip(displayed,lasts):
        if last and not pause:
            marker(frame,last,size=5,value=(255,0,0))

    if args.record and not pause and reduce(lambda a,b : bool(a and b),lasts):
        data.append(list(flatten(list(lasts))))

    q1 = np.hstack((displayed[0],displayed[1]))
    q2 = np.hstack((displayed[2],np.zeros(displayed[0].shape,dtype=displayed[0].dtype)))
    compose = np.vstack( (q1,q2) )

    cv2.imshow('frame',compose)

    # Dirty image hitbox definition
    p0 = np.array([0,0,640,360])
    p1 = np.array([640,0,640*2,360])
    p2 = np.array([0,360,640,360*2])    
    cv2.setMouseCallback('frame',register,param=[p0,p1,p2])

    # For adjusting offsets
    if mask:= cv2.waitKey(1) & 0xFF:
        if mask == ord('a'):
            frames[0] = caps[0].read()[1]
            offsets[0] += 1
        if mask == ord('z'):
            frames[1] = caps[1].read()[1]
            offsets[1] += 1
        if mask == ord('e'):
            frames[2] = caps[2].read()[1]
            offsets[2] += 1

        if mask == ord('p'):
            pause = not pause
        if mask == ord('q'):
            print(offsets)
            break

if args.record:
    import csv
    with open(args.record, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for point in data:
            writer.writerow(point)