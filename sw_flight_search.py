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
		global farePriceDollars
		global departTag
		global departTime
		global arriveTag
		global arriveTime
		global flightRoute
		global pointsFlag
		if "input" in tag:
			for attr in attrs:
				if "title" in attr[0]:
					result = attr[1].split(' ', 8)
					flightNum = result[2]
					farePriceDollars = result[3].replace('$','')
					temp = datetime.datetime.strptime(result[4], "%I:%M%p")
					departTime = temp.strftime("%H:%M:%S")
					departTag = result[5]
					temp = datetime.datetime.strptime(result[6], "%I:%M%p")
					arriveTime = temp.strftime("%H:%M:%S")
					arriveTag = result[7]
					flightRoute = result[8]
					temp = flightRoute.lower()
		if "label" in tag:
			for attr in attrs:
				if "class" in attr[0] and "product_price" in attr[1]:
					pointsFlag = True
	def handle_data(self, data):
		global farePricePoints
		global pointsFlag
		if pointsFlag:
			farePricePoints = data.replace(',','')
			pointsFlag = False

class MyHTMLParserErrors(HTMLParser):
	def handle_starttag(self, tag, attrs):
		global errorFlag
		global errorMessageFlag
		if "div" in tag:
			for attr in attrs:
				if "class" in attr[0].lower() and "oopserror" in attr[1].lower():
					errorFlag = True
		if errorFlag and "li" in tag:
			errorMessageFlag = True
	def handle_endtag(self, tag):
		global errorFlag
		global errorMessageFlag
		if "li" in tag and errorFlag and errorMessageFlag:
			errorFlag = False
			errorMessageFlag = False
	def handle_data(self, data):
		global errorFlag
		global errorMessageFlag
		global errorMessage
		if errorFlag and errorMessageFlag:
			errorMessage = errorMessage+data

#####################################################################
## Set directory path and file name for response & results html file
#####################################################################
cwd = os.getcwd()
responseFile = cwd+"/logs/sw_flight_response.html"
resultsFile = cwd+"/logs/sw_flight_results.html"
logFile = cwd+"/logs/"+time.strftime("%Y_%m_%d")+"_sw_flight_search.log"

#####################################################################
## Set user input variables
#####################################################################
temp = ""
departAirportCode = sys.argv[1]
departAirportName = ""
arriveAirportCode = sys.argv[2]
arriveAirportName = ""

db = MySQLdb.connect("127.0.0.1","root","swfarereducer","SWFAREREDUCERDB")
cursor = db.cursor()
sql = "SELECT a.AIRPORT_NAME AS DEPART_AIRPORT_NAME, b.AIRPORT_NAME AS ARRIVE_AIRPORT_NAME FROM AIRPORTS AS a, AIRPORTS AS b WHERE a.AIRPORT_CODE='%s' AND b.AIRPORT_CODE='%s' ORDER BY a.AIRPORT_CODE ASC" % (departAirportCode,arriveAirportCode)
print sql
try:
	cursor.execute(sql)
	results = cursor.fetchone()
	departAirportName = results[0]
	arriveAirportName = results[1]
except:
	db.close()
	logF = open(logFile, "a")
	logMessage = "%s ERROR: Unable to select airport name [depart:%s|arrive:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),departAirportCode,arriveAirportCode)
	logF.write(logMessage)
	logF.close()
	sys.exit(1)

departDate = sys.argv[3]
temp = datetime.datetime.strptime(departDate, "%m/%d/%Y")
departDay = temp.strftime("%A")
returnDate = sys.argv[4]
temp = datetime.datetime.strptime(returnDate, "%m/%d/%Y")
returnDay = temp.strftime("%A")

departTag = "depart"
departTime = "12:00AM"
arriveTag = "arrive"
arriveTime = "12:00AM"
flightRoute = ""
flightNum = "0"
fareType = ""
farePriceDollars = "0"
farePricePoints = "0"
pointsFlag = False
errorFlag = False
errorMessageFlag = False
errorMessage = ""

print "\nSearching for flights...\n"
sql = "SELECT AIRPORT_CODE,ROUTES_SERVED FROM AIRPORTS WHERE AIRPORT_CODE='SJC'"
try:
	cursor.execute(sql)
	results = cursor.fetchall()
	for row in results:
		routesServed = row[1].split(',')
		print routesServed
		for arriveAirportCode in routesServed:
			departAirportCode = row[0]
			departDate = sys.argv[3]
			temp = datetime.datetime.strptime(departDate, "%m/%d/%Y")
			departDay = temp.strftime("%A")
			returnDate = sys.argv[4]
			temp = datetime.datetime.strptime(returnDate, "%m/%d/%Y")
			returnDay = temp.strftime("%A")

			#####################################################################
			## Initiate mechanize, set parameters in form, and submit form
			#####################################################################
			try:
				br = mechanize.Browser()
				br.set_handle_robots(False)
				response = br.open("https://www.southwest.com/flight/")
				responseContent = response.read()
				with open(responseFile, "w") as f:
				    f.write(responseContent)
				br.select_form(name="buildItineraryForm")
				br.find_control(name="originAirport").value = [departAirportCode]
				br.find_control(name="destinationAirport").value = [arriveAirportCode]
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
				logMessage = "%s ERROR: Unable to search flights [depart:%s|arrive:%s|date:%s|return:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),departAirportCode,arriveAirportCode,departDate,returnDate)
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
				errorMessage = ""

			#####################################################################
			## Search results string for flights
			#####################################################################
			parser = MyHTMLParser()
			temp = datetime.datetime.strptime(departDate, "%m/%d/%Y")
			departDate = temp.strftime("%Y-%m-%d")
			print departAirportCode+" ---> "+arriveAirportCode+" [ "+departDay+", "+departDate+" ]"
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
					print "$%s (%s)\t%s %s %s %s (Flight # %s) %s %s" % (farePriceDollars,farePricePoints,departTime,departTag,arriveTime,arriveTag,flightNum,flightRoute,fareType)
					sql = "SELECT COUNT(*),FARE_PRICE_DOLLARS,FARE_PRICE_POINTS FROM UPCOMING_FLIGHTS WHERE DEPART_AIRPORT_CODE='%s' AND ARRIVE_AIRPORT_CODE='%s' AND DEPART_DATE_TIME='%s %s' AND FLIGHT_NUM='%s'" % (departAirportCode,arriveAirportCode,departDate,departTime,flightNum)
					try:
						cursor.execute(sql)
						results = cursor.fetchone()
						if results[0] > 0:
							if results[1] != int(farePriceDollars) or results[2] != int(farePricePoints):
								sql = "UPDATE UPCOMING_FLIGHTS SET FARE_PRICE_DOLLARS='%s',FARE_PRICE_POINTS='%s',FARE_TYPE='%s',UPDATE_TIMESTAMP='%s' WHERE DEPART_AIRPORT_CODE='%s' AND ARRIVE_AIRPORT_CODE='%s' AND DEPART_DATE_TIME='%s %s' AND FLIGHT_NUM='%s'" % (farePriceDollars,farePricePoints,fareType,time.strftime("%Y-%m-%d %H:%M:%S"),departAirportCode,arriveAirportCode,departDate,departTime,flightNum)
								try:
									cursor.execute(sql)
									db.commit()
								except:
									db.rollback()
									logF = open(logFile, "a")
									logMessage = "%s ERROR: Unable to update price [depart:%s|arrive:%s|date:%s %s|flight:%s|dollars:%s|points:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),departAirportCode,arriveAirportCode,departDate,departTime,flightNum,farePriceDollars,farePricePoints)
									logF.write(logMessage)
									logF.close()
						else:
							sql = "INSERT INTO UPCOMING_FLIGHTS (DEPART_AIRPORT_CODE,ARRIVE_AIRPORT_CODE,DEPART_DATE_TIME,ARRIVE_DATE_TIME,FLIGHT_NUM,FLIGHT_ROUTE,FARE_PRICE_DOLLARS,FARE_PRICE_POINTS,FARE_TYPE,UPDATE_TIMESTAMP) VALUES ('%s','%s','%s %s','%s %s','%s','%s','%s','%s','%s','%s')" % (departAirportCode,arriveAirportCode,departDate,departTime,departDate,arriveTime,flightNum,flightRoute,farePriceDollars,farePricePoints,fareType,time.strftime("%Y-%m-%d %H:%M:%S"))
							try:
								cursor.execute(sql)
								db.commit()
							except:
								db.rollback()
								logF = open(logFile, "a")
								logMessage = "%s ERROR: Unable to insert flight [depart:%s|arrive:%s|date:%s %s|flight:%s|dollars:%s|points:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),departAirportCode,arriveAirportCode,departDate,departTime,flightNum,farePriceDollars,farePricePoints)
								logF.write(logMessage)
								logF.close()
					except:
						logF = open(logFile, "a")
						logMessage = "%s ERROR: Unable to check flight [depart:%s|arrive:%s|date:%s %s|flight:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),departAirportCode,arriveAirportCode,departDate,departTime,flightNum)
						logF.write(logMessage)
						logF.close()

			print ""

			departDate = returnDate
			departDay = returnDay
			temp = departAirportCode
			departAirportCode = arriveAirportCode
			arriveAirportCode = temp
			temp = departAirportCode
			departAirportCode = arriveAirportCode
			arriveAirportCode = temp
			temp = datetime.datetime.strptime(departDate, "%m/%d/%Y")
			departDate = temp.strftime("%Y-%m-%d")
			print departAirportCode+" ---> "+arriveAirportCode+" [ "+departDay+", "+departDate+" ]"
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
					print "$%s (%s)\t%s %s %s %s (Flight # %s) %s %s" % (farePriceDollars,farePricePoints,departTime,departTag,arriveTime,arriveTag,flightNum,flightRoute,fareType)
					sql = "SELECT COUNT(*),FARE_PRICE_DOLLARS,FARE_PRICE_POINTS FROM UPCOMING_FLIGHTS WHERE DEPART_AIRPORT_CODE='%s' AND ARRIVE_AIRPORT_CODE='%s' AND DEPART_DATE_TIME='%s %s' AND FLIGHT_NUM='%s'" % (departAirportCode,arriveAirportCode,departDate,departTime,flightNum)
					try:
						cursor.execute(sql)
						results = cursor.fetchone()
						if results[0] > 0:
							if results[1] != int(farePriceDollars) or results[2] != int(farePricePoints):
								sql = "UPDATE UPCOMING_FLIGHTS SET FARE_PRICE_DOLLARS='%s',FARE_PRICE_POINTS='%s',FARE_TYPE='%s',UPDATE_TIMESTAMP='%s' WHERE DEPART_AIRPORT_CODE='%s' AND ARRIVE_AIRPORT_CODE='%s' AND DEPART_DATE_TIME='%s %s' AND FLIGHT_NUM='%s'" % (farePriceDollars,farePricePoints,fareType,time.strftime("%Y-%m-%d %H:%M:%S"),departAirportCode,arriveAirportCode,departDate,departTime,flightNum)
								try:
									cursor.execute(sql)
									db.commit()
								except:
									db.rollback()
									logF = open(logFile, "a")
									logMessage = "%s ERROR: Unable to update price [depart:%s|arrive:%s|date:%s %s|flight:%s|dollars:%s|points:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),departAirportCode,arriveAirportCode,departDate,departTime,flightNum,farePriceDollars,farePricePoints)
									logF.write(logMessage)
									logF.close()
						else:
							sql = "INSERT INTO UPCOMING_FLIGHTS (DEPART_AIRPORT_CODE,ARRIVE_AIRPORT_CODE,DEPART_DATE_TIME,ARRIVE_DATE_TIME,FLIGHT_NUM,FLIGHT_ROUTE,FARE_PRICE_DOLLARS,FARE_PRICE_POINTS,FARE_TYPE,UPDATE_TIMESTAMP) VALUES ('%s','%s','%s %s','%s %s','%s','%s','%s','%s','%s','%s')" % (departAirportCode,arriveAirportCode,departDate,departTime,departDate,arriveTime,flightNum,flightRoute,farePriceDollars,farePricePoints,fareType,time.strftime("%Y-%m-%d %H:%M:%S"))
							try:
								cursor.execute(sql)
								db.commit()
							except:
								db.rollback()
								logF = open(logFile, "a")
								logMessage = "%s ERROR: Unable to insert flight [depart:%s|arrive:%s|date:%s %s|flight:%s|dollars:%s|points:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),departAirportCode,arriveAirportCode,departDate,departTime,flightNum,farePriceDollars,farePricePoints)
								logF.write(logMessage)
								logF.close()
					except:
						logF = open(logFile, "a")
						logMessage = "%s ERROR: Unable to check flight [depart:%s|arrive:%s|date:%s %s|flight:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),departAirportCode,arriveAirportCode,departDate,departTime,flightNum)
						logF.write(logMessage)
						logF.close()
except:
	logF = open(logFile, "a")
	logMessage = "%s ERROR: Unable to retrieve airport routes\n" % (time.strftime("%Y-%m-%d %H:%M:%S"))
	logF.write(logMessage)
	logF.close()
	db.close()
	sys.exit(1)

db.close()

print ""