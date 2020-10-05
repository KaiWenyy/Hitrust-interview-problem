# Hitrust-interview-problem
Web crawler with captcha
## Setup
* Environment 
> python=3.8.5
* Install packages
> pip install -r requirements.txt
* Check your chrome version and download *Webdriver* from [here](https://chromedriver.chromium.org/downloads)
* Move *Webdriver for chrome* to the current folder 
* Download [model](https://drive.google.com/file/d/1xOy02BaAeRnaHmeNH5hTV7F7ZyhtdoyX/view?usp=sharing) to the current folder 
## Run 
*  `python test.py --id <businessID>`
> businessID: 16313302 as default
## Train model from scratch
* Train with the labeled data
	* unzip *img.zip* and run `python train.py`
* Train with data collected by your own
	* Run `python collect_data.py` to collect captcha data from [website](https://www.etax.nat.gov.tw/cbes/web/CBES113W1_1) 
	* Label data and save as the following format with filename `labels.txt`
	
	![labels](https://drive.google.com/uc?export=view&id=1xBlRNAeqvGD-mrNyylLo9cjNs0yk0Xx4)

	* Run `python label_data.py` to pack the same letter images in a folder
	* Train the model `python train.py` and save as `captcha_model.hdf5`
## Details
### Extract letter images from captcha
* Thresholding and finding the contours of letters to segment the captcha
* Additional processing for letter `j` and conjoined letters
### Training details
* optimizer = "sgd"
* epochs = 50
* Model total params 1.2M
## Demo
[link](https://youtu.be/9gLoRUzGpxs)
