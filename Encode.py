# May The Force Be With You

# Team FARFASA

# CMD Args

# Laptop/Desktop(slower, more accurate):
# python3 Encode.py --dataset dataset --encodings encodings.pickle --detection-method cnn

# Edge Device (faster, less accurate):
# python3 Encode.py --dataset dataset --encodings encodings.pickle --detection-method hog
# ----------------------------------------------------------------------------

from imutils import paths
import farfasa as farfasa
import argparse
import pickle
import cv2
import os
import time

# Argument Parser and Arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--dataset", required=True,
	help="path to input directory of faces + images")
ap.add_argument("-e", "--encodings", required=True,
	help="path to serialized db of facial encodings")
ap.add_argument("-d", "--detection-method", type=str, default="cnn",
	help="face detection model to use: either `hog` or `cnn`")
args = vars(ap.parse_args())


# Path to input images in dataset folder
print("quantifying faces")
imagePaths = list(paths.list_images(args["dataset"]))

# Initialize the list of known encodings and known names
knownEncodings = []
knownNames = []
print("begin counter")
T = time.perf_counter()
# Loop over the image paths
for (i, imagePath) in enumerate(imagePaths):
	# Extract the person name from the image path
	print("[INFO] processing image {}/{}".format(i + 1,
		len(imagePaths)))
	name = imagePath.split(os.path.sep)[-2]

	# Load the input image and convert it from RGB (OpenCV ordering) to RGB (dlib ordering)
	image = cv2.imread(imagePath)
	rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	print("{} loaded at {} . now detecting face".format(i + 1, (time.perf_counter()-T)))
	# Detect the (x, y)-coordinates of the bounding boxes corresponding to each face in the input image
	boxes = farfasa.faceLocations(rgb, model=args["detection_method"])
	print("{} detected at {} . now encoding".format(i+1, (time.perf_counter()-T)))
	# Compute the facial embedding for the face
	encodings = farfasa.faceEncodings(rgb, boxes)
	print("encoding {} finished at {}".format(i+1, (time.perf_counter()-T)))
	# Loop over the encodings
	for encoding in encodings:
		# Add each [encoding + name] to our set of known names and encodings
		knownEncodings.append(encoding)
		knownNames.append(name)
	print(" done {}. time is {}".format(i+1, (time.perf_counter()-T)))
# Dump the facial encodings + names to disk as a pickle file
print("[INFO] serializing encodings...")
data = {"encodings": knownEncodings, "names": knownNames}

f = open(args["encodings"], "wb")
f.write(pickle.dumps(data))
f.close()
