import argparse
parser = argparse.ArgumentParser()
parser.add_argument("input",type=str)
parser.add_argument("output",type=str)
parser.add_argument("frameskip",type=int,default=0)
args = parser.parse_args()

import cv2
cap = cv2.VideoCapture(args.input)

pause = False
data = list()

data.append((args.input,))
f = -1

def register(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        d = (f,x,y)
        print(d)
        data.append(d)
        global pause
        pause = False


ret = True
while cap.isOpened():
    if not pause:
        for i in range(args.frameskip + 1):
            f+=1
            ret,frame = cap.read()
        pause = True
    if ret:
        cv2.imshow('frame',frame)
        cv2.setMouseCallback('frame',register)
    else:
        break
    if mask:= cv2.waitKey(1) & 0xFF:
        if mask == ord('a'):
            pause = False
        if mask == ord('q'):
            break

import csv

with open(args.output, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for point in data:
        writer.writerow(point)
