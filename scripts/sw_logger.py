#!/usr/bin/python
import os
import sys
import time
import datetime

debug=0
datetime=""
cwd = os.getcwd()
logFile = cwd+"/logs/sys.log"

def LOG_INFO(name,msg):
	global debug
	global logFile
	global datetime
	get_datetime()
	message = "%s info %s: %s\n" % (datetime,name,msg)
	file = open(logFile, "a")
	file.write(message)
	file.close()
	if(debug == 1):
		print message
	return 0

def LOG_WARNING(name,msg):
	global debug
	global logFile
	global datetime
	get_datetime()
	message = "%s warning %s: %s\n" % (datetime,name,msg)
	file = open(logFile, "a")
	file.write(message)
	file.close()
	if(debug == 1):
		print message
	return 0

def LOG_ERROR(name,msg):
	global debug
	global logFile
	global datetime
	get_datetime()
	message = "%s error %s: %s\n" % (datetime,name,msg)
	file = open(logFile, "a")
	file.write(message)
	file.close()
	if(debug == 1):
		print message
	return 0

def LOG_DEBUG(name,msg):
	global debug
	global logFile
	global datetime
	if(debug == 1):
		get_datetime()
		message = "%s debug %s: %s\n" % (datetime,name,msg)
		file = open(logFile, "a")
		file.write(message)
		file.close()
		print message
	return 0

def get_datetime():
	global datetime
	datetime = time.strftime("%Y-%m-%d %H:%M:%S")
	return 0
