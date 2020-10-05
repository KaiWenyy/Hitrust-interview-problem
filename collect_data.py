from selenium import webdriver
import time
import urllib
import urllib.request
import os
import cv2, imutils
from imutils import contours
from skimage import measure
import numpy as np



img_url = "https://www.etax.nat.gov.tw/cbes/front/Common/CBEScaptcha/CAPTCHA_SESSION:174ebfe1d71000006cb5686b09dd11ef"

for _ in range(200):
	print('process', _)
	urllib.request.urlretrieve(img_url, 'img/full/'+str(_)+'.png' )
	image = cv2.imread('img/full/'+str(_)+'.png')
	#image = cv2.imread('img/full/8.png')
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	#blurred = cv2.GaussianBlur(gray, (11, 11), 0)
	#cv2.imwrite("blurred.png", blurred)
	thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
	#print(thresh.shape)
	thresh = thresh[2:-2, 2:-2]
	#print(thresh.shape) 
	#cv2.imwrite("thresholding.png", thresh)

	labels = measure.label(thresh, connectivity=1, background=255)
	mask = np.zeros(thresh.shape, dtype="uint8")
	for label in np.unique(labels):
		if label == 0:
			continue
		labelMask = np.zeros(thresh.shape, dtype="uint8")
		labelMask[labels == label] = 255
		numPixels = cv2.countNonZero(labelMask)
		if numPixels > 10:
			mask = cv2.add(mask, labelMask)
			#cv2.imwrite("img/" + str(label)+ ".png", labelMask)
	#cv2.imwrite("img/mask/" + str(_)+ ".png", mask)
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	cnts = contours.sort_contours(cnts)[0]
	rects = []
	for (i, c) in enumerate(cnts):
		# draw the bright spot on the image
		(x, y, w, h) = cv2.boundingRect(c)
		print(x, y, w, h, w/h)
		# handle "j"
		if w*h < 30:
			prev_coord = rects.pop()
			x, w, h = prev_coord[0], x+w - prev_coord[0], prev_coord[1]+prev_coord[3]-y

		rects.append((x, y, w, h))
	output_image = np.ones(thresh.shape, dtype="uint8")*255
	output_image[mask == 255] = 0
	i = 0
	for coord in rects:
		out = output_image[coord[1]:coord[1]+coord[3], coord[0]:coord[0]+coord[2]]
		# handle connected letter
		if coord[2]/coord[3] > 1.5:
			cv2.imwrite("img/seg/" + str(_)+ "_" + str(i) + ".png", out[:, 0:int(coord[2]*0.6)])
			i += 1
			cv2.imwrite("img/seg/" + str(_)+ "_" + str(i) + ".png", out[:, int(coord[2]*0.6):])
		else:
			cv2.imwrite("img/seg/" + str(_)+ "_" + str(i) + ".png", out)
		i += 1

