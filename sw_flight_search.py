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

global temp
global pointsFlag
global outboundTime
global returnTime
global flightNum
global currentPriceDollars
global currentPricePoints
global departTag
global departTime
global departTime24Hour
global arriveTag
global arriveTime
global arriveTime24Hour
global flightRoute
global upcoming_trips

# def send_mail():
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
# SMTP_USERNAME = "swfarereducer@gmail.com"
# SMTP_PASSWORD = "swfarereducer1"
# EMAIL_FROM = 'swfarereducer@gmail.com'
# EMAIL_TO = ['loj90@sbcglobal.net']
# EMAIL_SUBJECT = "Demo Email : "
# DATE_FORMAT = "%d/%m/%Y"
# EMAIL_SPACE = ", "
# DATA='This is the content of the email.'
# try:
# 	msg = MIMEText(DATA)
# 	msg['Subject'] = EMAIL_SUBJECT + " %s" % (date.today().strftime(DATE_FORMAT))
# 	msg['To'] = EMAIL_SPACE.join(EMAIL_TO)
# 	msg['From'] = EMAIL_FROM
# 	mail = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
# 	mail.starttls()
# 	mail.login(SMTP_USERNAME, SMTP_PASSWORD)
# 	mail.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
# 	mail.quit()
# 	# smtpObj = smtplib.SMTP('localhost')
# 	# smtpObj.sendmail(sender, receivers, message)         
# 	print "Successfully sent email"
# except smtplib.SMTPException:
# 	print "Error: unable to send email"

class MyHTMLParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		global temp
		global flightNum
		global currentPriceDollars
		global departTag
		global departTime
		global departTime24Hour
		global arriveTag
		global arriveTime
		global arriveTime24Hour
		global flightRoute
		global pointsFlag
		if "input" in tag:
			for attr in attrs:
				if "title" in attr[0]:
					result = attr[1].split(' ', 8)
					flightNum = result[2]
					currentPriceDollars = result[3].replace('$','')
					departTime = result[4]
					temp = time.strptime(departTime, "%I:%M%p")
					departTime24Hour = float(temp.tm_hour) + float(float(temp.tm_min) / 60)
					departTag = result[5]
					arriveTime = result[6]
					temp = time.strptime(arriveTime, "%I:%M%p")
					arriveTime24Hour = float(temp.tm_hour) + float(float(temp.tm_min) / 60)
					arriveTag = result[7]
					flightRoute = result[8]
					temp = flightRoute.lower()
		if "label" in tag:
			for attr in attrs:
				if "class" in attr[0] and "product_price" in attr[1]:
					pointsFlag = True
	def handle_data(self, data):
		global currentPricePoints
		global pointsFlag
		if pointsFlag:
			currentPricePoints = data.replace(',','')
			pointsFlag = False

#####################################################################
## Set directory path and file name for response & results html file
#####################################################################
cwd = os.getcwd()
responseFile = cwd+"/logs/southwest_flight_response.html"
resultsFile = cwd+"/logs/southwest_flight_results.html"
logFile = cwd+"/logs/"+time.strftime("%Y_%m_%d")+"_sw_flight_search.log"

#####################################################################
## Set user input variables
#####################################################################
temp = ""
originAirportCode = sys.argv[1]
originAirportName = ""
destinationAirportCode = sys.argv[2]
destinationAirportName = ""

db = MySQLdb.connect("127.0.0.1","root","swfarereducer","SWFAREREDUCERDB")
cursor = db.cursor()
sql = "SELECT a.AIRPORT_NAME AS DEPART_AIRPORT_NAME, b.AIRPORT_NAME AS ARRIVE_AIRPORT_NAME FROM AIRPORTS AS a, AIRPORTS AS b WHERE a.AIRPORT_CODE='%s' AND b.AIRPORT_CODE='%s' ORDER BY a.AIRPORT_CODE ASC" % (originAirportCode,destinationAirportCode)
try:
	cursor.execute(sql)
	results = cursor.fetchone()
	originAirportName = results[0]
	destinationAirportName = results[1]
except:
	db.close()
	logF = open(logFile, "a")
	logMessage = "%s ERROR: Unable to fetch airport name with depart:%s and arrive:%s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),originAirportCode,destinationAirportCode)
	logF.write(logMessage)
	logF.close()
	exit()

departDate = sys.argv[3]
temp = datetime.datetime.strptime(departDate, "%m/%d/%Y")
outboundDay = temp.strftime("%A")
returnDate = sys.argv[4]
temp = datetime.datetime.strptime(returnDate, "%m/%d/%Y")
returnDay = temp.strftime("%A")

pointsFlag = False
currentPriceDollars = "0"
currentPricePoints = "0"
departTag = "depart"
departTime = "12:00AM"
arriveTag = "arrive"
arriveTime = "12:00AM"
flightRoute = "all"
flightNum = "0"
fareType = False

#####################################################################
## Initiate mechanize, set parameters in form, and submit form
#####################################################################
print "\nSearching for flights...\n"
try:
	br = mechanize.Browser()
	br.set_handle_robots(False)
	response = br.open("https://www.southwest.com/flight/")
	responseContent = response.read()
	with open(responseFile, "w") as f:
	    f.write(responseContent)
	br.select_form(name="buildItineraryForm")
	br.find_control(name="originAirport").value = [originAirportCode]
	br.find_control(name="destinationAirport").value = [destinationAirportCode]
	br.form["outboundDateString"] = departDate
	# br.find_control(id="outboundTimeOfDay",name="outboundTimeOfDay").value = ['NOON_TO_6PM']
	br.form["returnDateString"] = returnDate
	br.find_control(id="roundTrip",name="twoWayTrip").value = ['true']
	br.find_control(name="fareType").value = ['POINTS']
	results = br.submit()
	resultsContent = results.read()
	with open(resultsFile, "w") as f:
	    f.write(resultsContent)
except:
	logF = open(logFile, "a")
	logMessage = "%s ERROR: Could not submit flight search form with depart:%s %s and arrive:%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),originAirportCode,departDate,destinationAirportCode,returnDate)
	logF.write(logMessage)
	logF.close()
	exit()

parser = MyHTMLParser()

print originAirportName+" ---> "+destinationAirportName+" [ "+outboundDay+", "+departDate+" ]"
for x in range(1,30):
	inputPosBeg = resultsContent.find("<input id=\"Out"+str(x)+"C\"")
	if(inputPosBeg != -1):
		inputPosEnd = resultsContent.find("</label>", inputPosBeg)
		outboundFlightResult = resultsContent[(inputPosBeg):(inputPosEnd+8)]
		parser.feed(outboundFlightResult)
		fareType="Wanna Get Away"
	else:
		inputPosBeg = resultsContent.find("<input id=\"Out"+str(x)+"B\"")
		if(inputPosBeg != -1):
			inputPosEnd = resultsContent.find("</label>", inputPosBeg)
			outboundFlightResult = resultsContent[(inputPosBeg):(inputPosEnd+8)]
			parser.feed(outboundFlightResult)
			fareType="Anytime"
		else:
			inputPosBeg = resultsContent.find("<input id=\"Out"+str(x)+"A\"")
			if(inputPosBeg != -1):
				inputPosEnd = resultsContent.find("</label>", inputPosBeg)
				outboundFlightResult = resultsContent[(inputPosBeg):(inputPosEnd+8)]
				parser.feed(outboundFlightResult)
				fareType="Business Select"
			else:
				fareType = False
	if fareType:
		print "$%s (%s)\t%s\t%s\t%s\t%s\t(Flight # %s) %s %s" % (currentPriceDollars,currentPricePoints,departTime,departTag,arriveTime,arriveTag,flightNum,flightRoute,fareType)
		sql = "INSERT INTO UPCOMING_FLIGHTS (DEPART_AIRPORT_CODE,ARRIVE_AIRPORT_CODE,DEPART_DATE,DEPART_TIME,ARRIVE_TIME,FLIGHT_NUM,FLIGHT_ROUTE,FARE_PRICE_DOLLARS,FARE_PRICE_POINTS,FARE_TYPE) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (originAirportCode,destinationAirportCode,departDate,departTime,arriveTime,flightNum,flightRoute,currentPriceDollars,currentPricePoints,fareType)
		try:
			cursor.execute(sql)
			db.commit()
		except:
			db.rollback()
			logF = open(logFile, "a")
			logMessage = "%s ERROR: Unable to insert flight info with depart:%s and arrive:%s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),originAirportCode,destinationAirportCode)
			logF.write(logMessage)
			logF.close()

print ""

print destinationAirportName+" ---> "+originAirportName+" [ "+returnDay+", "+returnDate+" ]"
for x in range(1,30):
	inputPosBeg = resultsContent.find("<input id=\"In"+str(x)+"C\"")
	if(inputPosBeg != -1):
		inputPosEnd = resultsContent.find("</label>", inputPosBeg)
		outboundFlightResult = resultsContent[(inputPosBeg):(inputPosEnd+8)]
		parser.feed(outboundFlightResult)
		fareType="Wanna Get Away"
	else:
		inputPosBeg = resultsContent.find("<input id=\"In"+str(x)+"B\"")
		if(inputPosBeg != -1):
			inputPosEnd = resultsContent.find("</label>", inputPosBeg)
			outboundFlightResult = resultsContent[(inputPosBeg):(inputPosEnd+8)]
			parser.feed(outboundFlightResult)
			fareType="Anytime"
		else:
			inputPosBeg = resultsContent.find("<input id=\"In"+str(x)+"A\"")
			if(inputPosBeg != -1):
				inputPosEnd = resultsContent.find("</label>", inputPosBeg)
				outboundFlightResult = resultsContent[(inputPosBeg):(inputPosEnd+8)]
				parser.feed(outboundFlightResult)
				fareType="Business Select"
			else:
				fareType = False
	if fareType:
		print "$%s (%s)\t%s\t%s\t%s\t%s\t(Flight # %s) %s %s" % (currentPriceDollars,currentPricePoints,departTime,departTag,arriveTime,arriveTag,flightNum,flightRoute,fareType)
		sql = "INSERT INTO UPCOMING_FLIGHTS (DEPART_AIRPORT_CODE,ARRIVE_AIRPORT_CODE,DEPART_DATE,DEPART_TIME,ARRIVE_TIME,FLIGHT_NUM,FLIGHT_ROUTE,FARE_PRICE_DOLLARS,FARE_PRICE_POINTS,FARE_TYPE) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (destinationAirportCode,originAirportCode,returnDate,departTime,arriveTime,flightNum,flightRoute,currentPriceDollars,currentPricePoints,fareType)
		try:
			cursor.execute(sql)
			db.commit()
		except:
			db.rollback()
			logF = open(logFile, "a")
			logMessage = "%s ERROR: Unable to insert flight info with depart:%s and arrive:%s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),originAirportCode,destinationAirportCode)
			logF.write(logMessage)
			logF.close()

print ""

db.close()