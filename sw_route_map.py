#!/usr/bin/python
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
from datetime import date
from HTMLParser import HTMLParser
from email.mime.text import MIMEText
from htmlentitydefs import name2codepoint

# https://www.southwest.com/flight/request-schedule.html
# https://www.southwest.com/html/air/airport-information.html

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
timestamp = int(time.time())
airportCode = ""
airportCity = ""
airportName = ""
airportTimezone = ""
airportLatitude = 0
airportLongitude = 0

#####################################################################
## Set directory path and file name for response & results html file
#####################################################################
cwd = os.getcwd()
resultsFile = cwd+"/routemap_dyn.html"
logFile = cwd+"/logs/"+time.strftime("%Y_%m_%d")+"_sw_route_map.log"
routeMapUrl = "https://www.southwest.com/flight/routemap_dyn.html"
apiKey1 = "AIzaSyAKjyfvOmXQfzJ0RPdbtNPL5fnzV4njekI"
apiKey2 = "AIzaSyBUJlKSKL0gfyW8xujV6_LXi30C3EK_ov0"

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
	for airportCode,value1 in parsed_json.items():
		for key,value2 in value1.items():
			if "routesServed" == key:
				routesServed = json.dumps(value2)
				if "[]" != routesServed:
					sql = "SELECT COUNT(*),ROUTES_SERVED FROM AIRPORTS WHERE AIRPORT_CODE='%s'" % (airportCode)
					try:
						cursor.execute(sql)
						results = cursor.fetchone()
						routesServed = routesServed.replace('[','')
						routesServed = routesServed.replace(']','')
						routesServed = routesServed.replace('\"','')
						routesServed = routesServed.replace(' ','')
						routesServed = routesServed.strip()
						if results[0] > 0 and routesServed != str(results[1]):
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
						logMessage = "%s ERROR: Unable to check airports - routesServed [airportCode:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
						logF.write(logMessage)
						logF.close()
else:
	logF = open(logFile, "a")
	logMessage = "%s ERROR: Could not locate 'routes' JSON\n" % (time.strftime("%Y-%m-%d %H:%M:%S"))
	logF.write(logMessage)
	logF.close()

# https://www.southwest.com/html/air/airport-information.html
# Get airport name

pos1 = resultsContent.find("var stations_info")
if(pos1 != -1):
	pos2 = resultsContent.find("{", pos1)
	pos3 = resultsContent.find("}}", pos2)
	parsed_json = json.loads(resultsContent[(pos2):(pos3+2)])
	for airportCode,value1 in parsed_json.items():
		for key,value2 in value1.items():
			if "display_name" in key:
				airportCity = value2
				airportName = ""
				airportLatitude = ""
				airportLongitude = ""
				airportTimezone = ""
				sql = "SELECT COUNT(*),AIRPORT_CITY,AIRPORT_NAME,AIRPORT_LATITUDE,AIRPORT_LONGITUDE,AIRPORT_TIMEZONE FROM AIRPORTS WHERE AIRPORT_CODE='%s' AND (AIRPORT_CITY IS NULL OR AIRPORT_NAME IS NULL OR AIRPORT_LATITUDE IS NULL OR AIRPORT_LONGITUDE IS NULL OR AIRPORT_TIMEZONE IS NULL)" % (airportCode)
				try:
					cursor.execute(sql)
					results = cursor.fetchone()
					if results[0] > 0:
						if str(results[3]) == "None" and str(results[4]) == "None":
							try:
								googleAddress = airportCity.replace(" - ",' ')
								googleAddress = googleAddress.replace('/',' ')
								googleAddress = googleAddress.replace('(','')
								googleAddress = googleAddress.replace(')','')
								googleAddress = googleAddress.replace(' ','+')
								geocodeApiUrl = "https://maps.googleapis.com/maps/api/geocode/json?address=%s+Airport&key=%s" % (googleAddress,apiKey1)
								apiResponse = requests.get(geocodeApiUrl)
								geocodeApiJson = apiResponse.json()
								for key1,value1 in geocodeApiJson.items():
									if "results" == key1:
										for key2,value2 in value1[0].items():
											if "geometry" == key2:
												geometry = value2
												for key3,value3 in geometry.items():
													if "location" == key3:
														geometry_location = value3
														for key4,value4 in geometry_location.items():
															if "lat" == key4:
																airportLatitude = value4
															elif "lng" == key4:
																airportLongitude = value4
											if "address_components" == key2:
												address_components = value2
												for key5,value5 in address_components[0].items():
													if "long_name" == key5 and "port" in value5.lower() and not airportName:
														airportName = value5
														break
													elif "short_name" == key5 and "port" in value5.lower() and not airportName:
														airportName = value5
														break
													elif "long_name" == key5 or "short_name" == key5:
														airportName = value5
							except:
								logF = open(logFile, "a")
								logMessage = "%s ERROR: Unable to retrieve latitude/longitude [airportCode:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
								logF.write(logMessage)
								logF.close()
						else:
							airportLatitude = results[3]
							airportLongitude = results[4]
						
						if str(results[5]) == "None" and airportLatitude and airportLongitude:
							try:
								timezoneApiUrl = "https://maps.googleapis.com/maps/api/timezone/json?location=%s,%s&timestamp=%s&key=%s" % (airportLatitude,airportLongitude,timestamp,apiKey1)
								apiResponse = requests.get(timezoneApiUrl)
								timezoneApiJson = apiResponse.json()
								for key,value in timezoneApiJson.items():
									if "timeZoneName" == key:
										airportTimezone = value
										break
							except:
								logF = open(logFile, "a")
								logMessage = "%s ERROR: Unable to retrieve timezone [airportCode:%s|apiResponse:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),airportCode,apiResponse)
								logF.write(logMessage)
								logF.close()

						if airportName and airportLatitude and airportLongitude and airportTimezone:
							sql = "UPDATE AIRPORTS SET AIRPORT_CITY='%s',AIRPORT_NAME='%s',AIRPORT_LATITUDE='%s',AIRPORT_LONGITUDE='%s',AIRPORT_TIMEZONE='%s',UPDATE_TIMESTAMP='%s' WHERE AIRPORT_CODE='%s'" % (airportCity,airportName,airportLatitude,airportLongitude,airportTimezone,time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
						elif airportName and airportLatitude and airportLongitude and not airportTimezone:
							sql = "UPDATE AIRPORTS SET AIRPORT_CITY='%s',AIRPORT_NAME='%s',AIRPORT_LATITUDE='%s',AIRPORT_LONGITUDE='%s',UPDATE_TIMESTAMP='%s' WHERE AIRPORT_CODE='%s'" % (airportCity,airportName,airportLatitude,airportLongitude,time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
						elif airportName and not airportLatitude and not airportLongitude and not airportTimezone:
							sql = "UPDATE AIRPORTS SET AIRPORT_CITY='%s',AIRPORT_NAME='%s',UPDATE_TIMESTAMP='%s' WHERE AIRPORT_CODE='%s'" % (airportCity,airportName,time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
						elif not airportName and not airportLatitude and not airportLongitude and not airportTimezone:
							sql = "UPDATE AIRPORTS SET AIRPORT_CITY='%s',UPDATE_TIMESTAMP='%s' WHERE AIRPORT_CODE='%s'" % (airportCity,time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
						else:
							sql = "UPDATE AIRPORTS SET AIRPORT_CITY='%s',UPDATE_TIMESTAMP='%s' WHERE AIRPORT_CODE='%s'" % (airportCity,time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
						try:
							cursor.execute(sql)
							db.commit()
						except:
							db.rollback()
							logF = open(logFile, "a")
							logMessage = "%s ERROR: Unable to update airport info [airportCode:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
							logF.write(logMessage)
							logF.close()
				except:
					logF = open(logFile, "a")
					logMessage = "%s ERROR: Unable to check airports [airportCode:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),airportCode)
					logF.write(logMessage)
					logF.close()
else:
	logF = open(logFile, "a")
	logMessage = "%s ERROR: Could not locate 'stations_info' JSON\n" % (time.strftime("%Y-%m-%d %H:%M:%S"))
	logF.write(logMessage)
	logF.close()

# sql = "SELECT AIRPORT_CODE,AIRPORT_CITY,AIRPORT_NAME,AIRPORT_LATITUDE,AIRPORT_LONGITUDE,AIRPORT_TIMEZONE,ROUTES_SERVED FROM AIRPORTS ORDER BY AIRPORT_CITY ASC"
# cursor.execute(sql)
# results = cursor.fetchall()
# for row in results:
# 	print "('%s','%s','%s','%s','%s','%s','%s','%s')," % (row[0],row[1],row[2],row[3],row[4],row[5],row[6],(time.strftime("%Y-%m-%d %H:%M:%S")))

db.close()