# Name: cap_img_ref.py
# Author: Vieux Adriano
# Date: 05.05.2023
# Project: Travail de Bachelor - Détection d'hydrocarbure sur route
# Contient le programme de capture d'image de référence. Fait varier la 
# configuration de la caméra: exposition, gains et balances des blancs.
# 3 captures sont faites par configuration.
import picamera2
from libcamera import controls
import time
import numpy as np
import matplotlib.pyplot as plt
import datetime

exposureTimeList = np.arange(500, 1500, 200).tolist()
gainList = np.arange(1.5, 2.0, 0.15).tolist()
gainRList = np.arange(0.6, 1.0, 0.1).tolist()
gainBList =  np.arange(1.2, 1.5, 0.1).tolist()

myCam = picamera2.Picamera2()
cam_res = (2500, 700)
camera_config = myCam.create_still_configuration(main={"size": (cam_res[0], cam_res[1])}, display = "main")
myCam.configure(camera_config)

distance = 0.80#[m] #picamera2 doc chap 5.2.3
myCam.set_controls({"ExposureTime":500,"AnalogueGain":1.0,"AwbEnable":False, "AfMode": controls.AfModeEnum.Manual, "LensPosition": (1/distance)})
for exposureTime in exposureTimeList:
	j=0
	myCam.set_controls({"ExposureTime":exposureTime})
	for gain in gainList:
		myCam.set_controls({"AnalogueGain":gain})
		for gainR in gainRList:
			for gainB in gainBList:
				myCam.set_controls({"ColourGains":(gainR,gainB)})	
				myCam.start()		
				for i in range(0,3):
					print("check")
					metadata = myCam.capture_metadata()
					tic = time.perf_counter()
					tac = time.perf_counter()
					cap_time = tac-tic
					datastamp = " Ex" + str(metadata["ExposureTime"]) + "LP" + str(metadata["LensPosition"])[:4] + "AG" + str(metadata["AnalogueGain"])[:5] + "CG" + str(metadata["ColourGains"])
					savefile = "reference/"+datetime.datetime.now().strftime("%Y%m%d %H%M%S")+ datastamp + ".png"
					myCam.capture_file(savefile)
					print("Succes ", j)
					j += 1
				myCam.stop()