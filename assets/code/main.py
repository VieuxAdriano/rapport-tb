# Name: main.py
# Author: Vieux Adriano
# Date: 05.05.2023
# Project: Travail de Bachelor - Détection d'hydrocarbure sur route
# Contient le programme principal de détection et d'action sur
# la télécommande. Le fonctionnement dépend entièrement de la librairie
# detection_lib.py livrée avec le reste du projet.

import detection_lib as det_lib
import matplotlib.pyplot as plt
import threading
import time

distance = 0.8
cam_res = (3500, 500)
run = True

det_lib.init_IO()
picam2 = det_lib.init_camera(cam_res, distance)
t1 = threading.Thread(target=det_lib.speed_timeout, args=(5,))
t1.start()

while run:
	try:
		tic = time.perf_counter()
		img, chrono = det_lib.capture(picam2)
		print(chrono)
		img_bin = det_lib.pretreatment(img, 0, 145)
		bin_treated = det_lib.treatement(img_bin)

		line = bin_treated[cam_res[1]//2,:]&True
		opening_pct = det_lib.zone_detection(line)
		speed = 5 #det_lib.get_speed()
		if speed > 0:
			t2 = threading.Thread(target = det_lib.action_delay(), args=(distance,speed,opening_pct,))
			t2.start()
		toc = time.perf_counter()
		#print(toc-tic)
	except KeyboardInterrupt:
		run = False 

det_lib.clean_IO()
det_lib.end_speed_timeout()