import argparse
import pandas
import numpy as np
import cv2

parser = argparse.ArgumentParser()
parser.add_argument("input",type=str) #Input csv file path
parser.add_argument("cam_1",type=int) # The main camera for the reconstruction
parser.add_argument("cam_2",type=int) # The second camera for the reconstruction
parser.add_argument("output",type=str) # Output 3D reconstruction position file name
args = parser.parse_args()

#CSV reading
df = pandas.read_csv(args.input)

cam1 = df.loc[:,"x1":"y1"]
cam2 = df.loc[:,"x2":"y2"]
cam3 = df.loc[:,"x3":"y3"]

# Reshaping the datas for the following process
cam1_np = cam1.to_numpy()
cam2_np = cam2.to_numpy()
cam3_np = cam3.to_numpy()

pts1Reshaped = cam1_np.reshape(cam1_np.shape[0],1,cam1_np.shape[1])
pts1Reshaped = np.array(pts1Reshaped,dtype=np.float32)
pts2Reshaped = cam2_np.reshape(cam2_np.shape[0],1,cam2_np.shape[1])
pts2Reshaped = np.array(pts2Reshaped,dtype=np.float32)
pts3Reshaped = cam2_np.reshape(cam3_np.shape[0],1,cam3_np.shape[1])
pts3Reshaped = np.array(pts3Reshaped,dtype=np.float32)

#Loading of all the cameras parameters
with np.load('matrix_dist_rvecs_tvecs_A.npz') as X:
    mtxA, distA, rvecsA, tvecsA = [X[i] for i in ('mtxA','distA','rvecsA','tvecsA')] #Camera 1 in our setup

with np.load('matrix_dist_rvecs_tvecs_E.npz') as X:
    mtxE, distE, rvecsE, tvecsE = [X[i] for i in ('mtxE','distE','rvecsE','tvecsE')] #Camera 2 in our setup

with np.load('matrix_dist_rvecs_tvecs_Z.npz') as X:
    mtxZ, distZ, rvecsZ, tvecsZ = [X[i] for i in ('mtxZ','distZ','rvecsZ','tvecsZ')] #Camera 3 in our setup

pts1Undistort = None
pts2Undistort = None
ProjectionMatrix1 = None
ProjectionMatrix2 = None
#Check if the same camera wasn't given two times
if args.cam_1 != args.cam_2:
	#Get the correct parameters for each camera
	if args.cam_1 == 1:
		pts1Undistort = cv2.undistortPoints(pts1Reshaped,mtxA,distA)
		ProjectionMatrix1 = np.column_stack((cv2.Rodrigues(rvecsA[0])[0],tvecsA[0]))
	elif args.cam_1 == 2:
		pts1Undistort = cv2.undistortPoints(pts2Reshaped,mtxE,distE)
		ProjectionMatrix1 = np.column_stack((cv2.Rodrigues(rvecsE[0])[0],tvecsE[0]))
	else:
		pts1Undistort = cv2.undistortPoints(pts3Reshaped,mtxZ,distZ)
		ProjectionMatrix1 = np.column_stack((cv2.Rodrigues(rvecsZ[0])[0],tvecsZ[0]))

	if args.cam_2 == 1:
		pts2Undistort = cv2.undistortPoints(pts1Reshaped,mtxA,distA)
		ProjectionMatrix2 = np.column_stack((cv2.Rodrigues(rvecsA[0])[0],tvecsA[0]))
	elif args.cam_2 == 2:
		pts2Undistort = cv2.undistortPoints(pts2Reshaped,mtxE,distE)
		ProjectionMatrix2 = np.column_stack((cv2.Rodrigues(rvecsE[0])[0],tvecsE[0]))
	else:
		pts2Undistort = cv2.undistortPoints(pts3Reshaped,mtxZ,distZ)
		ProjectionMatrix2 = np.column_stack((cv2.Rodrigues(rvecsZ[0])[0],tvecsZ[0]))
	
	#Reconstruct 3D Homogeneouse points from camera parameters and 2D points
	points4D = cv2.triangulatePoints(ProjectionMatrix1, ProjectionMatrix2, pts1Undistort,pts2Undistort).T
	
	#Convert 3D Homogeneouse points to 3D points
	points3d = cv2.convertPointsFromHomogeneous(points4D)
	points3d = points3d.tolist()
	points3d = list(map(lambda array: array[0],points3d))
		
	#Write an output file containing the coordinate of each points.
	f = open(args.output,"w")
	f.write(str(len(points3d)) + "\n")
	for i in range(len(points3d)):
		f.write(str(points3d[i][0]).replace(".",",") + " " + str(points3d[i][1]).replace(".",",") + " " + str(points3d[i][2]).replace(".",",") + "\n")
	f.close()
else:
	print("The same camera was given for cam1 and cam2")
	print("Args : pathToCSVFile mainCamNumber secondCamNumber outputFileName")

