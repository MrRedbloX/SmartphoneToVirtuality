import csv
import cv2
import numpy as np
from matplotlib import pyplot as plt
from itertools import *
from more_itertools import *



import argparse
parser = argparse.ArgumentParser(description='Displays tracking data.')
parser.add_argument('file', type=str,)
args = parser.parse_args()

pts = []
with open(args.file, newline='') as csvfile:
    epireader = csv.reader(csvfile, delimiter=',')
    for row in epireader:
        pts.append(list(map(int,row)))

pts = np.array(pts,dtype=np.int32)

print(pts.shape) # (167,6)
compose = np.zeros((360,640,3))

blue,green,red = np.identity(3)
ax,ay,bx,by,cx,cy = pts.T
compose[ax,ay], compose[bx,by], compose[cx,cy] = red, green, blue

while True:
    cv2.imshow('frame',compose)
    if mask:= cv2.waitKey(1) & 0xFF:
        if mask == ord('q'):
            break