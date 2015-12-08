#!/usr/bin/env python
import os
import re
import sys
import json
import time
import urllib2
import MySQLdb
import smtplib
import datetime
import mechanize
from datetime import date
from HTMLParser import HTMLParser
from email.mime.text import MIMEText
from htmlentitydefs import name2codepoint

checkinAlertMinutes = 15
currentDateTime = datetime.datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")
checkinAlertDateTime = datetime.datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d") + datetime.timedelta(minutes=checkinAlertMinutes)

#####################################################################
## Set directory path and file name for response & results html file
#####################################################################
cwd = os.getcwd()
responseFile = cwd+"/logs/lookup-air-reservation.html"
resultsFile = cwd+"/logs/view-air-reservation.html"
logFile = cwd+"/logs/"+time.strftime("%Y_%m_%d")+"_sw_flight_validator.log"

def main():
	#####################################################################
	## Retrieve list of upcoming reserved flights
	#####################################################################
	db = MySQLdb.connect("127.0.0.1","root","swfarereducer","SWFAREREDUCERDB")
	cursor = db.cursor()
	sql = "SELECT COUNT(*) FROM RESERVED_FLIGHTS WHERE DEPART_DATE_TIME >" % (confirmationNum,firstName,lastName)
	try:
		cursor.execute(sql)
		results = cursor.fetchone()
		if results[0] > 0:
			db.close()
			return 0
	except:
		logF = open(logFile, "a")
		logMessage = "%s ERROR: Unable to check reserved flights [confirmationNum:%s|firstName:%s|lastName:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),confirmationNum,firstName,lastName)
		logF.write(logMessage)
		logF.close()
		db.close()
		sys.exit(1)

# main()