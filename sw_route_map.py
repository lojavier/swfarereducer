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

global errorFlag
global errorMessageFlag
global errorMessage

class MyHTMLParserErrors(HTMLParser):
	def handle_starttag(self, tag, attrs):
		global errorFlag
		global errorMessageFlag
		if "div" in tag:
			for attr in attrs:
				if "class" in attr[0].lower() and "errors" in attr[1].lower():
					errorFlag = True
		if errorFlag and "p" in tag:
			errorMessageFlag = True
	def handle_endtag(self, tag):
		global errorFlag
		global errorMessageFlag
		if "p" in tag and errorFlag and errorMessageFlag:
			errorFlag = False
			errorMessageFlag = False
	def handle_data(self, data):
		global errorFlag
		global errorMessageFlag
		global errorMessage
		if errorFlag and errorMessageFlag:
			errorMessage = errorMessage+data

errorFlag = False
errorMessageFlag = False
errorMessage = ""

#####################################################################
## Set directory path and file name for response & results html file
#####################################################################
cwd = os.getcwd()
resultsFile = cwd+"/routemap_dyn.html"
logFile = cwd+"/logs/"+time.strftime("%Y_%m_%d")+"_sw_route_map.log"

#####################################################################
## Initiate mechanize, set parameters in form, and submit form
#####################################################################
print "\nRetrieving flight routes...\n"
# try:
# 	br = mechanize.Browser()
# 	br.set_handle_robots(False)
# 	results = br.open("https://www.southwest.com/flight/routemap_dyn.html")
# 	resultsContent = results.read()
# except:
# 	logF = open(logFile, "a")
# 	logMessage = "%s ERROR: Unable to retrieve flight routes\n" % (time.strftime("%Y-%m-%d %H:%M:%S"))
# 	logF.write(logMessage)
# 	logF.close()
# 	exit()

with open(resultsFile,"r") as f:
	resultsContent = f.read()

#####################################################################
## Search results string for errors
#####################################################################
parser = MyHTMLParserErrors()
parser.feed(resultsContent)
if errorMessage:
	endPos = errorMessage.rfind(".")
	errorMessage = errorMessage[:endPos+1]
	logF = open(logFile, "a")
	logMessage = "%s ERROR: %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),errorMessage)
	print logMessage
	logF.write(logMessage)
	logF.close()
	exit()
# else:
# 	with open(resultsFile, "w") as f:
# 	    f.write(resultsContent)

db = MySQLdb.connect("127.0.0.1","root","swfarereducer","SWFAREREDUCERDB")
cursor = db.cursor()
pos1 = resultsContent.find("var routes")
if(pos1 != -1):
	pos2 = resultsContent.find("{", pos1)
	pos3 = resultsContent.find("}}", pos2)
	parsed_json = json.loads(resultsContent[(pos2):(pos3+2)])
	for airportCode,value in parsed_json.items():
		for x in value:
			if "routesServed" in x:
				routesServed = json.dumps(value[x])
				if "[]" not in routesServed:
					sql = "SELECT COUNT(*),ROUTES_SERVED FROM AIRPORTS WHERE AIRPORT_CODE='%s'" % (airportCode)
					try:
						cursor.execute(sql)
						results = cursor.fetchone()
						if results[0] > 0 and routesServed != results[1]:
							sql = "UPDATE AIRPORTS SET ROUTES_SERVED='%s',UPDATE_TIMESTAMP='%s' WHERE AIRPORT_CODE='%s'" % (json.dumps(values[x]),time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
							try:
								cursor.execute(sql)
								db.commit()
							except:
								db.rollback()
								logF = open(logFile, "a")
								logMessage = "%s ERROR: Unable to update routesServed [airportCode:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
								logF.write(logMessage)
								logF.close()
						elif results[0] == 0:
							print "%s %s" % (results[0],results[1])
							sql = "INSERT INTO AIRPORTS (AIRPORT_CODE,ROUTES_SERVED,UPDATE_TIMESTAMP) VALUES ('%s','%s','%s')" % (airportCode,routesServed,time.strftime("%Y-%m-%d %H:%M:%S"))
							try:
								cursor.execute(sql)
								db.commit()
							except:
								db.rollback()
								logF = open(logFile, "a")
								logMessage = "%s ERROR: Unable to insert airport [airportCode:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
								logF.write(logMessage)
								logF.close()
					except:
						logF = open(logFile, "a")
						logMessage = "%s ERROR: Unable to check airports [airportCode:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
						logF.write(logMessage)
						logF.close()
else:
	print "WARNING: Could not locate routes served json."


pos1 = resultsContent.find("var stations_info")
if(pos1 != -1):
	pos2 = resultsContent.find("{", pos1)
	pos3 = resultsContent.find("}}", pos2)
	parsed_json = json.loads(resultsContent[(pos2):(pos3+2)])
	for airportCode,value in parsed_json.items():
		for x in value:
			if "display_name" in x:
				airportName = (json.dumps(value[x])).replace('\"','')
				print airportCode,airportName
				if airportName:
					sql = "SELECT COUNT(*) FROM AIRPORTS WHERE AIRPORT_CODE='%s'" % (airportCode)
					try:
						cursor.execute(sql)
						results = cursor.fetchone()
						# print results[0]
						# if results[0] > 0 and routesServed != results[1]:
						# 	sql = "UPDATE AIRPORTS SET ROUTES_SERVED='%s',UPDATE_TIMESTAMP='%s' WHERE AIRPORT_CODE='%s'" % (json.dumps(values[x]),time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
						# 	try:
						# 		cursor.execute(sql)
						# 		db.commit()
						# 	except:
						# 		db.rollback()
						# 		logF = open(logFile, "a")
						# 		logMessage = "%s ERROR: Unable to update routesServed [airportCode:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
						# 		logF.write(logMessage)
						# 		logF.close()
						# elif results[0] == 0:
						# 	print "%s %s" % (results[0],results[1])
						# 	sql = "INSERT INTO AIRPORTS (AIRPORT_CODE,ROUTES_SERVED,UPDATE_TIMESTAMP) VALUES ('%s','%s','%s')" % (airportCode,routesServed,time.strftime("%Y-%m-%d %H:%M:%S"))
						# 	try:
						# 		cursor.execute(sql)
						# 		db.commit()
						# 	except:
						# 		db.rollback()
						# 		logF = open(logFile, "a")
						# 		logMessage = "%s ERROR: Unable to insert airport [airportCode:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
						# 		logF.write(logMessage)
						# 		logF.close()
					except:
						logF = open(logFile, "a")
						logMessage = "%s ERROR: Unable to check airports [airportCode:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
						logF.write(logMessage)
						logF.close()
else:
	print "WARNING: Could not locate airport info json."