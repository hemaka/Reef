import sys
import time
import RPi.GPIO as GPIO
import json
from Reef import reef

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

reef = Reef()
loopCount = 0
while True:
	temp = reef.readTemp()
	print(temp)
	time.sleep(1)
	# if(temp < 25.5)
	# 	if(heaterStatus == 'off')
	# 		switchHeater('on')
	# 	if(fansStatus == 'on')
	# 		switchFans('off')
	# if(temp > 25.8)
	# 	if(heaterStatus == 'on')
	# 		switchHeater('off')
	# 	if(fansStatus == 'off')
	# 		switchFans('on')
	# getAction()
 #    loopCount += 1
 #    if(loopCount >= 60)
 #    	postLog()
    