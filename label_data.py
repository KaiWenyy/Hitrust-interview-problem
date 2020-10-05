import os
import cv2
from os import listdir


SEG_IMG_DIR = 'img/seg'
LABEL_FILE = 'labels.txt'
OUTPUT_FOLDER = 'img/letter_image'
counts = {}

# parse target
labels = []
with open(LABEL_FILE, 'r') as f:
	lines = f.readlines()
	for line in lines:
		splited = line.strip().split()
		labels = labels + splited

if not os.path.exists(OUTPUT_FOLDER):
	os.makedirs(OUTPUT_FOLDER)

try:
	for i in range(200):
		for j in range(6):
			img_name = os.path.join(SEG_IMG_DIR, str(i)+"_"+str(j)+".png")
			letter_image = cv2.imread(img_name)
			letter_text = labels[i*6+j]
			if letter_text.isupper():
				save_path = os.path.join(OUTPUT_FOLDER, "big_"+letter_text.lower())
			else:
				save_path = os.path.join(OUTPUT_FOLDER, letter_text.lower())

			# if the output directory does not exist, create it
			if not os.path.exists(save_path):
				os.makedirs(save_path)

			# write the letter image to a file
			count = counts.get(letter_text, 1)
			p = os.path.join(save_path, "{}.png".format(str(count)))
			cv2.imwrite(p, letter_image)
			# increment the count for the current key
			counts[letter_text] = count + 1
except:
	print("have not collect data yet!")