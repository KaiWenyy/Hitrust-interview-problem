from selenium import webdriver
import urllib
import urllib.request
import os, pickle
from helper import extract_letter_image, resize_to_fit, get_captcha
from keras.models import load_model
import numpy as np
import cv2
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--id", help="Business ID number", type = str, default="16313302")
args = parser.parse_args()


MODEL_FILENAME = "captcha_model.hdf5"
MODEL_LABELS_FILENAME = "model_labels.dat"


# 爬取頁面網址 
URL = "https://www.etax.nat.gov.tw/cbes/web/CBES113W1"
#"https://www.etax.nat.gov.tw/cbes/web/CBES113W1_1"
# 目標元素的xpath
XPATH = '//*[@id="captchaImg"]'
# 啟動chrome瀏覽器
chromeDriver = "./chromedriver" # chromedriver檔案放的位置
driver = webdriver.Chrome(chromeDriver) 
# 最大化窗口，因為每一次爬取只能看到視窗内的圖片 
driver.maximize_window()  
# 瀏覽器打開爬取頁面
driver.get(URL)  
# 找到 "依營業人統一編號查詢" 並點擊
driver.find_element_by_xpath('/html/body/div[6]/div/div[2]/div[4]/ul[2]/li[1]/a').click()
# 輸入 公司營業地址
company_inputs = driver.find_element_by_xpath('//*[@id="vatId"]')
company_inputs.send_keys(args.id)

# Load up the model labels (so we can translate model predictions to actual letters)
with open(MODEL_LABELS_FILENAME, "rb") as f:
    lb = pickle.load(f)
# Load the trained neural network
model = load_model(MODEL_FILENAME)

for element in driver.find_elements_by_xpath(XPATH):#[driver.find_element_by_id("captchaImg")]:
    letter_images = []
    predicted_code = ''
    try:
        get_captcha(driver, element, "captcha.png")
        #driver.save_screenshot('current.png')
        letter_images = extract_letter_image("captcha.png")
        #i = 0
        for letter_image in letter_images:
            #cv2.imwrite(str(i)+".png", letter_image)
            letter_image = resize_to_fit(letter_image, 30, 30)/ 255.0

            # Turn the single image into a 4d list of images to make Keras happy
            letter_image = np.expand_dims(letter_image, axis=2)
            letter_image = np.expand_dims(letter_image, axis=0)

            # Ask the neural network to make a prediction
            prediction = model.predict(letter_image)

            # Convert the one-hot-encoded prediction back to a normal letter
            letter = lb.inverse_transform(prediction)[0]
            if letter.split('_')[0] == 'big':
                letter = letter.split("_")[-1].upper()
            predicted_code = predicted_code + letter
            #i += 1

        # 輸入驗證碼
        captcha_inputs = driver.find_element_by_xpath('//*[@id="captcha"]')
        captcha_inputs.send_keys(predicted_code)
        #driver.save_screenshot('current1.png')  
    
    except OSError:
        print('發生OSError!')
        break;


# 點擊確認鍵
driver.find_element_by_xpath('//*[@id="tablet01"]/table/tbody/tr[3]/td/div/div[1]/input').click()
# 儲存目前頁面
driver.save_screenshot('final_screen.png')
print("================================================")
print('business ID:', args.id)
print("predicted code:", predicted_code)
try:
    driver.find_element_by_xpath('//*[@id="address"]')
    address = driver.find_element_by_xpath('//*[@id="address"]').text
    print('address:', address)
except:
    print('verification failed!!')

print("================================================")
driver.close()