#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import the necessary packages
from Transform.transform import four_point_transform
from skimage.filters import threshold_local
from PIL import Image
import pytesseract
import numpy as np
import argparse
import os, sys
import imutils
import cv2
import re

if sys.stdout.encoding == None:
    os.putenv("PYTHONIOENCODING",'UTF-8')
    os.execv(sys.executable,['python']+sys.argv)
 
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True,
	help = "Path to the image to be scanned")
args = vars(ap.parse_args())


def imageProcesser(imagePath):

	# Taking a matrix of size 5 as the kernel
	kernel = np.ones((2,2), np.uint8)

	# load the image
	image 	= cv2.imread(imagePath)
	ratio 	= image.shape[0] / 500.0
	orig 	= image.copy()
	image 	= imutils.resize(image, height = 500)


	# convert image to grayscale
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# apply gaussian blur
	gray = cv2.GaussianBlur(gray, (5, 5), 0)

	# Find edges in image using Canny algo
	edged = cv2.Canny(gray, 75, 200)

	# find the contours in the edged image, keeping only the
	# largest ones, and initialize the screen contour
	cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]
	cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]
	 
	# loop over the contours
	for c in cnts:
		# approximate the contour
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.02 * peri, True)
	 
		# if our approximated contour has four points, then we
		# can assume that we have found our screen
		if len(approx) == 4:
			screenCnt = approx
			break
	 
	# show the contour (outline) of the piece of paper
	cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 2)

	# apply the four point transform to obtain a top-down
	# view of the original image
	warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
	 
	# convert the warped image to grayscale, then threshold it
	# to give it that 'black and white' paper effect
	warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
	T = threshold_local(warped, 191, offset = 20, method = "gaussian")
	warped = (warped > T).astype("uint8") * 255
	gray = cv2.erode(warped, kernel, iterations=2)
	gray = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
	

	# write the grayscale image to disk as a temporary file so we can
	# apply OCR to it
	filename = "{}.png".format(os.getpid())
	cv2.imwrite(filename, gray)

	# show the output images
	cv2.imshow("Original", 	imutils.resize(orig, 	height = 650))
	cv2.imshow("Output", 	imutils.resize(gray,	height = 650))

	# Waits for a key insert to close images.
	cv2.waitKey(0)
	cv2.destroyAllWindows()

	return filename

def imageOcr(filename):

	# load the image, apply OCR, and then delete the temporary file
	text = pytesseract.image_to_string(Image.open(filename), lang = "tur")
	os.remove(filename)

	textList = text.split('\n')

	# Regex for parsing Date, Receipt No and Amount 
	date_Regex 		 = re.compile(".*\d{2}(\/|\.|\-|\—)\d{2}.*(\/|\.|\-|\—).*\d{2,4}.*")
	receipt_No_Regex = re.compile(".*(fi\ş|fis|fış|fıs){1}.*(NO|no|No){1}.*")
	amount_Regex 	 = re.compile(".*(toplam|TOP|top|TUP|TOP|Kredi|kredi|KREDI){1}.*\*.*\d*\,\d*")


	data = {

		"Amount": [],
		"Date": [],
		"Receipt Number": [],
		"Place":[]
	}

	counter = 0
	for x in textList:

		x = x.lower()
		print(x)
		if counter == 0:
			data["Place"].append(x)

		if date_Regex.match(x):
			data.Date.append(x)

		if amount_Regex.match(x):
			data.Amount.append(x)

		if receipt_No_Regex.match(x):
			data['Receipt Number'].append(x)

		counter += 1
	return data

 
if __name__ == '__main__':

	filename = imageProcesser(args["image"])
	print(imageOcr(filename))





