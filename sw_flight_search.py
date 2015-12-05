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
flightUrl = "https://www.southwest.com/flight/"

#####################################################################
## Setup global variables
#####################################################################
temp = ""
departAirportCode = ""
arriveAirportCode = ""
departDate = ""
returnDate = ""
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
routesServed = []
inProgressFlightSearch = []
completedFlightSearch = []
flightSearchDone = False

db = MySQLdb.connect("127.0.0.1","root","swfarereducer","SWFAREREDUCERDB")
cursor = db.cursor()

print "\nSearching for flights...\n"
if len(sys.argv) > 3:
	daysAdvance = 1
else:
	daysAdvance = 60

for dayCount in range(0,daysAdvance):
	#####################################################################
	## Select all airports and their routes served
	#####################################################################
	if len(sys.argv) > 1 and sys.argv[1] != "ALL" and sys.argv[2] != "ALL":
		departAirportCode = sys.argv[1]
		arriveAirportCode = sys.argv[2]
		sql = "SELECT AIRPORT_CODE,ROUTES_SERVED FROM AIRPORTS WHERE AIRPORT_CODE='%s' AND ROUTES_SERVED LIKE '%%%s%%'" % (departAirportCode,arriveAirportCode)
	elif len(sys.argv) > 1 and sys.argv[1] != "ALL" and sys.argv[2] == "ALL":
		departAirportCode = sys.argv[1]
		sql = "SELECT AIRPORT_CODE,ROUTES_SERVED FROM AIRPORTS WHERE AIRPORT_CODE='%s'" % (departAirportCode)
	else:
		sql = "SELECT AIRPORT_CODE,ROUTES_SERVED FROM AIRPORTS"
	try:
		cursor.execute(sql)
		results = cursor.fetchall()
		for row in results:
			time.sleep(1)
			if len(sys.argv) > 1 and sys.argv[2] != "ALL":
				routesServed.append(arriveAirportCode)
			else:
				routesServed = row[1].split(',')
			for arriveAirportCode in routesServed:
				departAirportCode = row[0]

				if len(sys.argv) > 3:
					departDate = datetime.datetime.strptime(sys.argv[3], "%Y-%m-%d")
					returnDate = datetime.datetime.strptime(sys.argv[4], "%Y-%m-%d")
				else:
					departDate = datetime.datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d") + datetime.timedelta(days=dayCount+1)
					returnDate = datetime.datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d") + datetime.timedelta(days=dayCount+2)
				#####################################################################
				## Compare the in progress depart and arrive flight and depart date
				## with the completed flight searches
				#####################################################################
				inProgressFlightSearch = []
				inProgressFlightSearch.append([departAirportCode,arriveAirportCode,departDate.strftime("%Y-%m-%d")])
				# completedFlightSearch.append(['SJC','ONT','2015-12-04'])
				for x in range(0,len(completedFlightSearch)):
					if inProgressFlightSearch[0] == completedFlightSearch[x]:
						flightSearchDone = True
						break
					else:
						flightSearchDone = False

				if not flightSearchDone:
					#####################################################################
					## Select one of the airports from routes served to cross check a 
					## return flight
					#####################################################################
					sql = "SELECT COUNT(*) FROM AIRPORTS WHERE AIRPORT_CODE='%s' AND ROUTES_SERVED LIKE '%%%s%%'" % (arriveAirportCode,departAirportCode)
					try:
						cursor.execute(sql)
						results = cursor.fetchone()
						if results[0] > 0:
							#####################################################################
							## Initiate mechanize, set parameters in form, and submit form
							#####################################################################
							try:
								br = mechanize.Browser()
								br.set_handle_robots(False)
								response = br.open(flightUrl)
								responseContent = response.read()
								with open(responseFile, "w") as f:
								    f.write(responseContent)
								br.select_form(name="buildItineraryForm")
								br.find_control(name="originAirport").value = [departAirportCode]
								br.find_control(name="destinationAirport").value = [arriveAirportCode]
								br.form["outboundDateString"] = departDate.strftime("%m/%d/%Y")
								# br.find_control(id="outboundTimeOfDay",name="outboundTimeOfDay").value = ['NOON_TO_6PM']
								br.form["returnDateString"] = returnDate.strftime("%m/%d/%Y")
								br.find_control(id="roundTrip",name="twoWayTrip").value = ['true']
								br.find_control(name="fareType").value = ['POINTS']
								results = br.submit()
								resultsContent = results.read()
								with open(resultsFile, "w") as f:
								    f.write(resultsContent)
							except:
								logF = open(logFile, "a")
								logMessage = "%s ERROR: Unable to search flights via %s [depart:%s|arrive:%s|date:%s|return:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),flightUrl,departAirportCode,arriveAirportCode,departDate,returnDate)
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
								logF.write(logMessage)
								logF.close()
								errorMessage = ""
							
							#####################################################################
							## Search results string for flights
							#####################################################################
							departDay = departDate.strftime("%A") # temp
							departDate = departDate.strftime("%Y-%m-%d")
							returnDate = returnDate.strftime("%Y-%m-%d")
							parser = MyHTMLParser()
							print "%s ---> %s [ %s, %s ]" % (departAirportCode,arriveAirportCode,departDay,departDate)
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
							completedFlightSearch.append([departAirportCode,arriveAirportCode,departDate])
							print ""
							
							departDate = returnDate
							temp = departAirportCode
							departAirportCode = arriveAirportCode
							arriveAirportCode = temp
							departDate = datetime.datetime.strptime(departDate, "%Y-%m-%d") # temp
							departDay = departDate.strftime("%A") # temp
							departDate = departDate.strftime("%Y-%m-%d") # temp
							print "%s ---> %s [ %s, %s ]" % (departAirportCode,arriveAirportCode,departDay,departDate)
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
							completedFlightSearch.append([departAirportCode,arriveAirportCode,departDate])
							print ""
					except:
						logF = open(logFile, "a")
						logMessage = "%s ERROR: Unable to search return route [depart:%s|arrive:%s|date:%s|return:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),departAirportCode,arriveAirportCode,departDate,returnDate)
						logF.write(logMessage)
						logF.close()
						sys.exit(1)
	except:
		logF = open(logFile, "a")
		logMessage = "%s ERROR: Unable to retrieve airport routes\n" % (time.strftime("%Y-%m-%d %H:%M:%S"))
		logF.write(logMessage)
		logF.close()
		db.close()
		sys.exit(1)

db.close()