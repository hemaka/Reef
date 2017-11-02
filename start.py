import sys
import time
import os
import glob
import RPi.GPIO as GPIO
import json
import dotenv
import settings
from reef import Reef

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

GPIO.setmode(GPIO.BCM)
GPIO.setup(int(os.environ['SWITCH_LIGHT_GPIO']), GPIO.OUT)

reef = Reef()
loopCount = 0
while True:
	reef.pullAction()
	reef.readTemp()
	reef.checkTemp()
	if reef.statusChange:
		reef.sendLog()
	print(reef.temp, reef.lightStatus, reef.heaterStatus, reef.fansStatus)
	loopCount += 1
	if loopCount >= float(os.environ['REFRESH_TIME']):
		reef.sendLog()
		loopCount = 0
	time.sleep(1)