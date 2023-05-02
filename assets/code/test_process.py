# Name: test_process.py
# Author: Vieux Adriano
# Date: 05.05.2023
# Project: Travail de Bachelor - Détection d'hydrocarbure sur route
# Script permettant de tester les captures dans différents modes paramètrables.
import picamera2
from libcamera import controls
import time
import numpy as np
import matplotlib.pyplot as plt
import datetime

myCam = picamera2.Picamera2()
cam_res = (2500, 700)
#cam_res=(1024,768)
#cam_res = (4608, 500)
camera_config = myCam.create_still_configuration(main={"size": (cam_res[0], cam_res[1])}, display = "main")
myCam.configure(camera_config)
distance = 0.37#[m] #picamera2 doc chap 5.2.3
myCam.set_controls({"ExposureTime":5000, "AfMode": controls.AfModeEnum.Manual, "LensPosition": (1/distance)})
myCam.start()
metadata = myCam.capture_metadata()
mode = 1
while True:
	try:
		if mode == 0:
			tic = time.perf_counter()
			data = myCam.capture_array("main")
			tac = time.perf_counter()
			if (tac - tic) < 0.025:
				time.sleep(0.025 - tac + tic)
			toc = time.perf_counter()
			print(f"temps: {toc-tic:0.4f}")
		elif mode == 1:
			tic = time.perf_counter()
			data = myCam.capture_array("main")
			tac = time.perf_counter()
			print(tac-tic)
			print(metadata["ColourGains"])
			plt.title("ExpTime : "+ str(metadata["ExposureTime"]) + " Lens_pos : " + str(metadata["LensPosition"])[:5] + " AG: " + str(metadata["AnalogueGain"])[:5])
			plt.imshow(data)
			savefile = "capture/"+datetime.datetime.now().strftime("%Y%m%d %H%M%S")+".png"
			plt.savefig(savefile, dpi=300)
			plt.show()
			input("next")
		elif mode == 2:
			for balance in range(1,8):
				myCam.stop()
				myCam.set_controls({"AwbEnable":True, "AwbMode":balance})
				myCam.start()
				tic = time.perf_counter()
				data = myCam.capture_array("main")
				tac = time.perf_counter()
				print(tac-tic)
				plt.title("ExpTime : "+ str(metadata["ExposureTime"]) + " Lens_pos : " + str(metadata["LensPosition"])[:5] + " AG: " + str(metadata["AnalogueGain"])[:5] + " WhiteBalance: " + str(balance))
				plt.imshow(data)
				savefile = "capture/"+datetime.datetime.now().strftime("%Y%m%d %H%M%S")+".png"
				plt.savefig(savefile, dpi=300)
				#plt.show()
				print("check")
			print("out")
	except KeyboardInterrupt:
		break
