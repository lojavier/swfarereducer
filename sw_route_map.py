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
import requests
import mechanize
import googlemaps
from datetime import date
from HTMLParser import HTMLParser
from email.mime.text import MIMEText
from htmlentitydefs import name2codepoint
requests.packages.urllib3.disable_warnings()

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
routeMapUrl = "https://www.southwest.com/flight/routemap_dyn.html"
ApiKey = "AIzaSyAKjyfvOmXQfzJ0RPdbtNPL5fnzV4njekI"
gmaps = googlemaps.Client(key=ApiKey)

#####################################################################
## Initiate mechanize, set parameters in form, and submit form
#####################################################################
print "\nRetrieving flight routes...\n"
try:
	br = mechanize.Browser()
	br.set_handle_robots(False)
	results = br.open(routeMapUrl)
	resultsContent = results.read()
except:
	logF = open(logFile, "a")
	logMessage = "%s ERROR: Unable to retrieve flight routes\n" % (time.strftime("%Y-%m-%d %H:%M:%S"))
	logF.write(logMessage)
	logF.close()
	sys.exit(1)

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
	sys.exit(1)
else:
	with open(resultsFile, "w") as f:
	    f.write(resultsContent)

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
						routesServed = routesServed.replace('[','')
						routesServed = routesServed.replace(']','')
						routesServed = routesServed.replace('\"','')
						routesServed = routesServed.replace(' ','')
						routesServed = routesServed.strip()
						if results[0] > 0 and str(routesServed) != str(results[1]):
							sql = "UPDATE AIRPORTS SET ROUTES_SERVED='%s',UPDATE_TIMESTAMP='%s' WHERE AIRPORT_CODE='%s'" % (routesServed,time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
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
	logF = open(logFile, "a")
	logMessage = "%s ERROR: Could not locate 'routes' JSON\n" % (time.strftime("%Y-%m-%d %H:%M:%S"))
	logF.write(logMessage)
	logF.close()

pos1 = resultsContent.find("var stations_info")
if(pos1 != -1):
	pos2 = resultsContent.find("{", pos1)
	pos3 = resultsContent.find("}}", pos2)
	parsed_json = json.loads(resultsContent[(pos2):(pos3+2)])
	for airportCode,value in parsed_json.items():
		for x in value:
			if "display_name" in x:
				airportCity = (json.dumps(value[x])).replace('\"','')
				if airportCity:
					sql = "SELECT COUNT(*),AIRPORT_CITY,AIRPORT_NAME,AIRPORT_LATITUDE,AIPORT_LONGITUDE FROM AIRPORTS WHERE AIRPORT_CODE='%s'" % (airportCode)
					try:
						cursor.execute(sql)
						results = cursor.fetchone()
						if results[0] > 0 and airportCity != results[1]:
							sql = "UPDATE AIRPORTS SET AIRPORT_CITY='%s',UPDATE_TIMESTAMP='%s' WHERE AIRPORT_CODE='%s'" % (airportCity,time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
							try:
								cursor.execute(sql)
								db.commit()
							except:
								db.rollback()
								logF = open(logFile, "a")
								logMessage = "%s ERROR: Unable to update airport name [airportCity:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),airportCity)
								logF.write(logMessage)
								logF.close()
					except:
						logF = open(logFile, "a")
						logMessage = "%s ERROR: Unable to check airports [airportCode:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
						logF.write(logMessage)
						logF.close()
else:
	print "WARNING: Could not locate airport info json"
	logF = open(logFile, "a")
	logMessage = "%s ERROR: Could not locate 'stations_info' JSON\n" % (time.strftime("%Y-%m-%d %H:%M:%S"))
	logF.write(logMessage)
	logF.close()


sql = "SELECT AIRPORT_CITY,AIRPORT_LATITUDE,AIPORT_LONGITUDE FROM AIRPORTS"
try:
	cursor.execute(sql)
	results = cursor.fetchall()
	for row in results:
		airportCity = row[0]
		geocode_result = gmaps.geocode(airportCity)
		for key1,value1 in geocode_result[0].items():
			if "geometry" == key1:
				geometry = value1
				for key2,value2 in geometry.items():
					if "location" == key2:
						geometry_location = value2
						for key3,value3 in geometry_location.items():
							if "lat" == key3:
								airportLatitude = value3
							if "lng" == key3:
								airportLongitude = value3
			if "address_components" == key1:
				address_components = value1
				for key4,value4 in address_components[0].items():
					if "long_name" == key4 and "port" in value4.lower():
						airportName = value4
						break
					else:
						airportName = None
		print "('%s','%s','%s','%s','%s')," % (airportCode,airportCity,airportName,airportLatitude,airportLongitude)
		
		sql = "UPDATE AIRPORTS SET AIRPORT_CITY='%s',UPDATE_TIMESTAMP='%s' WHERE AIRPORT_CODE='%s'" % (airportCity,time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
		try:
			cursor.execute(sql)
			db.commit()
		except:
			db.rollback()
			logF = open(logFile, "a")
			logMessage = "%s ERROR: Unable to update airport name [airportCity:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),airportCity)
			logF.write(logMessage)
			logF.close()
else:
	print "WARNING: Could not locate airport info json"
	logF = open(logFile, "a")
	logMessage = "%s ERROR: Could not locate 'stations_info' JSON\n" % (time.strftime("%Y-%m-%d %H:%M:%S"))
	logF.write(logMessage)
	logF.close()

db.close()