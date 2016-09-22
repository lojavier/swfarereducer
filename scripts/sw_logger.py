#!/usr/bin/python
import os
import sys
import time
import datetime

debug=True
datetime=""
cwd = os.path.dirname(os.path.realpath(__file__))
logFile = cwd+"/../logs/sys.log"

def LOG_INFO(name,msg):
	global debug
	global logFile
	global datetime
	get_datetime()
	message = "%s info %s: %s" % (datetime,name,msg)
	file = open(logFile, "a")
	file.write(message+"\n")
	file.close()
	if(debug == True):
		print message
	return 0

def LOG_WARNING(name,msg):
	global debug
	global logFile
	global datetime
	get_datetime()
	message = "%s warning %s: %s" % (datetime,name,msg)
	file = open(logFile, "a")
	file.write(message+"\n")
	file.close()
	if(debug == True):
		print message
	return 0

def LOG_ERROR(name,msg):
	global debug
	global logFile
	global datetime
	get_datetime()
	message = "%s error %s: %s" % (datetime,name,msg)
	file = open(logFile, "a")
	file.write(message+"\n")
	file.close()
	if(debug == True):
		print message
	return 0

def LOG_DEBUG(name,msg):
	global debug
	global logFile
	global datetime
	if(debug == True):
		get_datetime()
		message = "%s debug %s: %s" % (datetime,name,msg)
		file = open(logFile, "a")
		file.write(message+"\n")
		file.close()
		print message
	return 0

def get_datetime():
	global datetime
	datetime = time.strftime("%Y-%m-%d %H:%M:%S")
	return 0
