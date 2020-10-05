import imutils
import cv2
from imutils import contours
from skimage import measure
import numpy as np
from PIL import Image
from io import BytesIO

# crop captcha from the screenshot 
def get_captcha(driver, element, path):
    image = driver.get_screenshot_as_png()
    size = element.size
    location = element.location 
    image = Image.open(BytesIO(image))
    #print('screen shape', image.size)
    #print(location, size)
    window_size = driver.get_window_size()
    screen_size = image.size
    #browser_navigation_panel_height = driver.execute_script('return window.outerHeight - window.innerHeight;')
    ratio_w = screen_size[0]/window_size["width"]
    ratio_h = screen_size[1]/window_size["height"]

    left = int(location['x']*ratio_w)
    top = int(location['y']*ratio_h) + 150 #browser_navigation_panel_height
    right = int((location['x'] + size['width'])*ratio_w)
    bottom = int((location['y'] + size['height'])*ratio_h) + 152 #browser_navigation_panel_height
    #print((left, top, right, bottom))

    image = image.crop((left, top, right, bottom))
    image.save(path, 'png')

def resize_to_fit(image, width, height):
    image = cv2.resize(image, (width, height))
    return image

# extract letter images 
# return letter image list in captcha
def extract_letter_image(captcha_image_filename):
    image = cv2.imread(captcha_image_filename)
    image = cv2.resize(image, (150, 35))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
    thresh = thresh[2:-2, 2:-2]

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
    #cv2.imwrite("mask.png", mask)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = contours.sort_contours(cnts)[0]
    rects = []
    for (i, c) in enumerate(cnts):
        # draw the bright spot on the image
        (x, y, w, h) = cv2.boundingRect(c)
        #print(x, y, w, h, w/h)
        # handle "j"
        if w*h < 30:
            prev_coord = rects.pop()
            x, w, h = prev_coord[0], x+w - prev_coord[0], prev_coord[1]+prev_coord[3]-y

        rects.append((x, y, w, h))
    
    output_image = np.ones(thresh.shape, dtype="uint8")*255
    output_image[mask == 255] = 0
    output_letter_images = []

    for coord in rects:
        out = output_image[coord[1]:coord[1]+coord[3], coord[0]:coord[0]+coord[2]]
        # handle connected letter
        if coord[2]/coord[3] > 1.5:
            output_letter_images.append(out[:, 0:int(coord[2]*0.6)])
            output_letter_images.append(out[:, int(coord[2]*0.6):])
        else:
            output_letter_images.append(out)
    return output_letter_images


