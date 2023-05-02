# Name: detection_lib.py
# Author: Vieux Adriano
# Date: 05.05.2023
# Project: Travail de Bachelor - Détection d'hydrocarbure sur route
# Contient La librairie de fonction nécessaire au fonctionnemnt
# du programme principal.

import picamera2
from libcamera import controls
import time
import numpy as np 
import cv2
import threading
import RPi.GPIO as GPIO

speed_mutex = threading.Lock()

#callback d'interruption de mesure de vitesse
#Retourne None
def speed_calculation_callback(channel):
	#taille de la roue en [m]
	wheel_diameter = 0.7
	t_new = time.time()
	t = t_new - speed_calculation_callback.t_old
	
	speed_mutex.acquire()
	speed_calculation_callback.speed = wheel_diameter*np.pi/t
	speed_mutex.release()
	print(speed_calculation_callback.speed)
	
	speed_calculation_callback.t_old = t_new
#initialisation de la variable de fonction
speed_calculation_callback.t_old = time.time()
speed_calculation_callback.speed = 0.0

#Fonction de vérification de la vitesse
def speed_timeout(timeout):
	while (speed_timeout.run):
		time.sleep(timeout)
		if(time.time()-speed_calculation_callback.t_old > timeout):
			speed_calculation_callback.speed=0.0
			action_delay(0,1,[0,0,0])
speed_timeout.run = True

#Fonction arrêtant la boucle de vérification de vitesse
def end_speed_timeout():
	speed_timeout.run = False

#Initialisation des entrées/sorties
#retourne None
def init_IO():
	interrupt_pin = 16
	#mode de pinning BCM
	GPIO.setmode(GPIO.BCM)
	#sorties
	GPIO.setup(17, GPIO.OUT)
	GPIO.setup(18, GPIO.OUT)
	GPIO.setup(19, GPIO.OUT)
	GPIO.setup(20, GPIO.OUT)
	GPIO.setup(21, GPIO.OUT)
	GPIO.setup(22, GPIO.OUT)
	#Entrée d'interruption et sa routine
	GPIO.setup(interrupt_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.add_event_detect(interrupt_pin,
							GPIO.RISING,
							callback=speed_calculation_callback,
							bouncetime=100)

#a mettre en fin de programme
def clean_IO():
	GPIO.cleanup()

#retourne la vitesse mesurée
def get_speed():
	speed_mutex.acquire()
	speed = speed_calculation_callback.speed
	speed_mutex.release()
	return speed
	 
#commande d'une section du semoir
#à utiliser dans un thread
#retourne None
def action_command(opening_id, opening_pct):
	#temps total d'ouverture 0-100% [s]
	tot_opening_time = 0.5
	if opening_pct != 0.0:
		if opening_pct < 0.0:
			opening_id += 1
		GPIO.output(opening_id, GPIO.HIGH)
		time.sleep(tot_opening_time*abs(opening_pct)/100)
		GPIO.output(opening_id, GPIO.LOW)
		
#Fonction d'attente avant l'action sur les boutons
#à mettre dans un thread
#param: opening_state est une liste des pct d'ouverture
#retourne None		
def action_delay(distance, speed, opening_state):
	time.sleep(distance/speed)

	shift_left = opening_state[0] - action_delay.left
	shift_center = opening_state[1] - action_delay.center
	shift_right = opening_state[2] - action_delay.right
	
	th_op_left = threading.Thread(target=action_command,
									args=(17, shift_left,))
	th_op_center = threading.Thread(target=action_command,
									args=(19, shift_center,))
	th_op_right = threading.Thread(target=action_command,
									args=(21, shift_right,))
	
	th_op_left.start()
	th_op_center.start()
	th_op_right.start()
	
	th_op_left.join()
	th_op_center.join()
	th_op_right.join()
	
	action_delay.left = opening_state[0]
	action_delay.center = opening_state[1]
	action_delay.right = opening_state[2]
	
action_delay.left = 0.0
action_delay.center = 0.0
action_delay.right = 0.0

#Initialisation de la camera
#retourne la caméra
def init_camera(cam_res, distance):
	picam2 = picamera2.Picamera2()
	camera_config = picam2.create_still_configuration(main={"size": (cam_res[0], cam_res[1])}, display = "main")
	picam2.configure(camera_config)
	picam2.set_controls({"ExposureTime":1080,
						"AnalogueGain":1.65,"AwbEnable":False,
						"AfMode": controls.AfModeEnum.Manual,
						"LensPosition": (1/distance),
						"ColourGains":(0.9,1.4)})
	picam2.start()
	return picam2

#Routine de capture
#retourne l'image et le temps de capture
def capture(picam2):
	tic = time.perf_counter()
	data = picam2.capture_array("main")
	tac = time.perf_counter()
	time_capture = tac-tic
	return data, time_capture

#Prétraitement - isolation des infos nécessaire
#retourne une image binarisée
def pretreatment(capture, layer, threshold):
	out = ((capture[:,:,layer]>threshold)*255).astype('uint8')
	return out

#Détection des zones de présence d'hydrocarbure
#retourne une image binaire ressortant la présence d'hydrocarbure
def treatement(binarised):
	kernel_dilate = np.ones((6,6), np.uint8)
	kernel_erode =  np.ones((4,4), np.uint8)
	
	dilated = cv2.dilate(binarised, kernel_dilate)
	opened = cv2.erode(dilated, kernel_erode)
	eroded = cv2.erode(opened,kernel_erode)
	return eroded

#Param: ligne de pixel binarisée, hydrocarbure = T, route = F
#retourne une liste des pct d'ouvert. de chaque section
def zone_detection(line):
	section_size = len(line)//3
	limit_2 = 2*len(line)//3
	
	section_1 = np.where(line[:section_size]==True)
	
	section_2 = np.where(line[section_size:limit_2]==True)
	section_2 = [x + section_size for x in section_2]
	
	section_3 = np.where(line[limit_2:]==True)
	section_3 = [x + limit_2 for x in section_3]
	
	section_1_opening = 0
	section_2_opening = 0
	section_3_opening = 0
	#100px est le seuil minimal d'actionnement des ouvertures.
	if len(section_1[0]) > 100:
		section_1_opening = 100*len(section_1[0])/section_size
	if len(section_2[0]) > 100:
		section_2_opening = 100*len(section_2[0])/section_size
	if len(section_3[0]) > 100:
		section_3_opening = 100*len(section_3[0])/section_size
	return [section_1_opening, section_2_opening, section_3_opening]
