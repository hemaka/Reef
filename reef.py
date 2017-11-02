import os
import sys
import time
import glob
import json
import RPi.GPIO as GPIO

import requests

class Reef():
	def __init__(self):
		self.temp = 0.0
		self.fansStatus = 'off'
		self.lightStatus = 'off'
		self.heaterStatus = 'off'
		self.statusChange = False
		self.action = False
		base_dir = '/sys/bus/w1/devices/'
		device_folder = glob.glob(base_dir + '28*')[0]
		self.device_file = device_folder + '/w1_slave'

	def read_temp_raw(self):
	    f = open(self.device_file, 'r')
	    lines = f.readlines()
	    f.close()
	    return lines

	def readTemp(self):
		lines = self.read_temp_raw()
		while lines[0].strip()[-3:] != 'YES':
			time.sleep(0.2)
			lines = self.read_temp_raw()
		equals_pos = lines[1].find('t=')
		if equals_pos != -1:
			temp_string = lines[1][equals_pos+2:]
			temp_c = float(temp_string) / 1000.0
			self.temp = temp_c
			return
		self.temp = 0
		return

	def checkTemp(self):
		if self.temp < float(os.environ['HEATER_TEMP']):
			self.switchHeater('on')
		else:
			self.switchHeater('off')
		if self.temp > float(os.environ['FANS_TEMP']):
			self.switchFans('on')
		else:
			self.switchFans('off')
		if self.temp > float(os.environ['HEATER_TEMP']) and self.temp < float(os.environ['FANS_TEMP']):
			self.switchHeater('off')
			self.switchFans('off')

	def switchFans(self,val):
		if self.fansStatus == val:
			return val
		self.fansStatus = val
		self.statusChange = True
		return val

	def switchHeater(self, val):
		if self.heaterStatus == val:
			return val
		self.heaterStatus = val
		self.statusChange = True
		return val

	def switchLight(self,val):
		if self.lightStatus == val:
			return val
		self.lightStatus = val
		self.statusChange = True
		if self.lightStatus == 'on':
			GPIO.output(int(os.environ['SWITCH_LIGHT_GPIO']), GPIO.HIGH)
		else:
			GPIO.output(int(os.environ['SWITCH_LIGHT_GPIO']), GPIO.LOW)
		return val
	
	def pullAction(self):
		r = requests.get(os.environ['SERVER_PULL_ACTIONS'])
		actions = json.loads(r.text)
		for action in actions['data']:
			if action['device'] == 'fans':
				self.switchFans(action['value'])
			elif action['device'] == 'light':
				self.switchLight(action['value'])
			elif action['device'] == 'heater':
				self.switchHeater(action['value'])
			r = requests.get(os.environ['SERVER_PUSH_ACTION'] + str(action['id']))
			print(action['device'], action['value'], os.environ['SERVER_PUSH_ACTION'] + str(action['id']))

		if self.statusChange:
			self.action = True
			self.sendLog()

		print('pull action')

	def sendLog(self):
		note = 'm' if self.action else 'auto'
		self.action = False
		log = {'temp': self.temp, 'fans': self.fansStatus, 'light': self.lightStatus, 'heater': self.heaterStatus, 'note': note}
		r = requests.get(os.environ['SERVER_PUSH_LOG'], params={'data':json.dumps(log)})
		self.statusChange = False
		print('send log')