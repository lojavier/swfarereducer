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
import mechanize
from datetime import date
from HTMLParser import HTMLParser
from email.mime.text import MIMEText
from htmlentitydefs import name2codepoint
from sw_logger import LOG_INFO,LOG_ERROR,LOG_WARNING,LOG_DEBUG

#####################################################################
## Setup global variables
#####################################################################
temp = ""
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
db = MySQLdb.connect("127.0.0.1","root","swfarereducer","SWFAREREDUCERDB")
cwd = os.path.dirname(os.path.realpath(__file__))
responseFile = cwd+"/../docs/sw_flight_response.html"
resultsFile = cwd+"/../docs/sw_flight_results.html"
flightUrl = "https://www.southwest.com/flight/"

###########
## main
###########
def main():
	global db
	global responseFile
	global resultsFile
	global logFile
	global flightUrl
	routesServed = []
	inProgressFlightSearch = []
	completedFlightSearch = []
	flightSearchDone = False
	departAirportCode = ""
	arriveAirportCode = ""
	departDate = ""
	returnDate = ""
	global departTag
	global departTime
	global arriveTag
	global arriveTime
	global flightRoute
	global flightNum
	global fareType
	global farePriceDollars
	global farePricePoints
	global pointsFlag
	global errorFlag
	global errorMessageFlag
	global errorMessage

	cursor = db.cursor()

	if len(sys.argv) > 3:
		daysAdvance = 1
	else:
		daysAdvance = 90

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
									# with open(responseFile, "w") as f:
									#     f.write(responseContent)
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
									# with open(resultsFile, "w") as f:
									#     f.write(resultsContent)
								except:
									LOG_ERROR(os.path.basename(__file__),"Failed to search flights via %s [depart:%s|arrive:%s|date:%s|return:%s]" % flightUrl,departAirportCode,arriveAirportCode,departDate.strftime("%Y-%m-%d"),returnDate.strftime("%Y-%m-%d"))
									return 1

								#####################################################################
								## Search results string for errors
								#####################################################################
								parser = MyHTMLParserErrors()
								parser.feed(resultsContent)
								if errorMessage:
									endPos = errorMessage.rfind(".")
									errorMessage = errorMessage[:endPos+1]
									LOG_ERROR(os.path.basename(__file__),errorMessage)
									errorMessage = ""
								
								#####################################################################
								## Search results string for departing flights
								#####################################################################
								departDay = departDate.strftime("%A")
								departDate = departDate.strftime("%Y-%m-%d")
								returnDate = returnDate.strftime("%Y-%m-%d")
								parser = MyHTMLParser()
								LOG_DEBUG(os.path.basename(__file__), "\n%s ---> %s [ %s, %s ]" % (departAirportCode,arriveAirportCode,departDay,departDate))
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
										LOG_DEBUG(os.path.basename(__file__),"$%s (%s)\t%s %s %s %s (Flight # %s) %s %s" % (farePriceDollars,farePricePoints,departTime,departTag,arriveTime,arriveTag,flightNum,flightRoute,fareType))
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
														LOG_ERROR(os.path.basename(__file__),"Failed to update price [depart:%s|arrive:%s|date:%s %s|flight:%s|dollars:%s|points:%s]" % departAirportCode,arriveAirportCode,departDate,departTime,flightNum,farePriceDollars,farePricePoints)
											else:
												sql = "INSERT INTO UPCOMING_FLIGHTS (DEPART_AIRPORT_CODE,ARRIVE_AIRPORT_CODE,DEPART_DATE_TIME,ARRIVE_DATE_TIME,FLIGHT_NUM,FLIGHT_ROUTE,FARE_PRICE_DOLLARS,FARE_PRICE_POINTS,FARE_TYPE,UPDATE_TIMESTAMP) VALUES ('%s','%s','%s %s','%s %s','%s','%s','%s','%s','%s','%s')" % (departAirportCode,arriveAirportCode,departDate,departTime,departDate,arriveTime,flightNum,flightRoute,farePriceDollars,farePricePoints,fareType,time.strftime("%Y-%m-%d %H:%M:%S"))
												try:
													cursor.execute(sql)
													db.commit()
												except:
													db.rollback()
													LOG_ERROR(os.path.basename(__file__),"Failed to insert flight [depart:%s|arrive:%s|date:%s %s|flight:%s|dollars:%s|points:%s]" % departAirportCode,arriveAirportCode,departDate,departTime,flightNum,farePriceDollars,farePricePoints)
										except:
											LOG_ERROR(os.path.basename(__file__),"Failed to check flight [depart:%s|arrive:%s|date:%s %s|flight:%s]" % departAirportCode,arriveAirportCode,departDate,departTime,flightNum)

								completedFlightSearch.append([departAirportCode,arriveAirportCode,departDate])
								
								#####################################################################
								## Search results string for return flights
								#####################################################################
								departDate = returnDate
								temp = departAirportCode
								departAirportCode = arriveAirportCode
								arriveAirportCode = temp
								departDate = datetime.datetime.strptime(departDate, "%Y-%m-%d") # temp
								departDay = departDate.strftime("%A") # temp
								departDate = departDate.strftime("%Y-%m-%d") # temp
								LOG_DEBUG(os.path.basename(__file__), "\n%s ---> %s [ %s, %s ]" % (departAirportCode,arriveAirportCode,departDay,departDate))
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
										LOG_DEBUG(os.path.basename(__file__),"$%s (%s)\t%s %s %s %s (Flight # %s) %s %s" % (farePriceDollars,farePricePoints,departTime,departTag,arriveTime,arriveTag,flightNum,flightRoute,fareType))
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
														LOG_ERROR(os.path.basename(__file__),"Failed to update price [depart:%s|arrive:%s|date:%s %s|flight:%s|dollars:%s|points:%s]" % departAirportCode,arriveAirportCode,departDate,departTime,flightNum,farePriceDollars,farePricePoints)
											else:
												sql = "INSERT INTO UPCOMING_FLIGHTS (DEPART_AIRPORT_CODE,ARRIVE_AIRPORT_CODE,DEPART_DATE_TIME,ARRIVE_DATE_TIME,FLIGHT_NUM,FLIGHT_ROUTE,FARE_PRICE_DOLLARS,FARE_PRICE_POINTS,FARE_TYPE,UPDATE_TIMESTAMP) VALUES ('%s','%s','%s %s','%s %s','%s','%s','%s','%s','%s','%s')" % (departAirportCode,arriveAirportCode,departDate,departTime,departDate,arriveTime,flightNum,flightRoute,farePriceDollars,farePricePoints,fareType,time.strftime("%Y-%m-%d %H:%M:%S"))
												try:
													cursor.execute(sql)
													db.commit()
												except:
													db.rollback()
													LOG_ERROR(os.path.basename(__file__),"Failed to insert flight [depart:%s|arrive:%s|date:%s %s|flight:%s|dollars:%s|points:%s]" % (departAirportCode,arriveAirportCode,departDate,departTime,flightNum,farePriceDollars,farePricePoints))
										except:
											LOG_ERROR(os.path.basename(__file__),"Failed to check flight [depart:%s|arrive:%s|date:%s %s|flight:%s]" % (departAirportCode,arriveAirportCode,departDate,departTime,flightNum))
								completedFlightSearch.append([departAirportCode,arriveAirportCode,departDate])
						except:
							LOG_ERROR(os.path.basename(__file__),"Failed to search return route [depart:%s|arrive:%s|date:%s|return:%s]" % (departAirportCode,arriveAirportCode,departDate,returnDate))
							return 1
		except:
			LOG_ERROR(os.path.basename(__file__),"Failed to retrieve airport routes")
			db.close()
			return 1

	db.close()
	return 0

main()