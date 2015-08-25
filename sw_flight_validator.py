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
# http://www.blog.pythonlibrary.org/2012/06/08/python-101-how-to-submit-a-web-form/
# http://www.thetaranights.com/fill-online-form-using-python/
# http://wwwsearch.sourceforge.net/mechanize/download.html
# http://readwrite.com/2014/06/27/raspberry-pi-web-server-website-hosting
global temp
global outboundTime
global returnTime
global flightNum
global currentDollarsPrice
global currentPointsPrice
global departTag
global departTime
global departTime24Hour
global arriveTag
global arriveTime
global arriveTime24Hour
global route
global upcoming_trips
global paidPrice
global confirmationNum
global firstName
global lastName
global notificationAddress
global outboundArriveTime
global outboundFlightNum
global paidDollarsPrice
global paidPointsPrice

# print "TEST\n\n"
# sys.exit(1)

class MyHTMLParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		# print "Start tag:", tag
		# for attr in attrs:
		# 	print "     attr:", attr
		global departureDateFlag
		global departureCityFlag
		global departureTimeFlag
		global arrivalCityFlag
		global arrivalTimeFlag
		global strongFlag
		global tdFlag
		global fareTypeFlag
		if "span" in tag:
			for attr in attrs:
				if "class" in attr[0] and "summary-travel-date" in attr[1]:
					departureDateFlag = True
				if "class" in attr[0] and "nowrap" in attr[1] and "nextDayContainer" not in attr[1]:
					departureTimeFlag = True
				if "class" in attr[0] and "nextDayContainer" in attr[1]:
					arrivalTimeFlag = True
		elif "strong" in tag:
			strongFlag = True
		elif "td" in tag:
			tdFlag = True
		elif "div" in tag:
			for attr in attrs:
				if "class" in attr[0] and "fareProductName" in attr[1]:
					fareTypeFlag = True
		else:
			strongFlag = False
			tdFlag = False
	def handle_data(self, data):
		global roundTripFlag
		global departureCityCode1
		global departureCity1
		global departureDate1
		global departureTime1
		global departureCityCode2
		global departureCity2
		global departureDate2
		global departureTime2
		global departureCityFlag
		global departureDateFlag
		global departureTimeFlag
		global arrivalCityCode1
		global arrivalCity1
		global arrivalTime1
		global arrivalCityCode2
		global arrivalCity2
		global arrivalTime2
		global arrivalCityFlag
		global arrivalTimeFlag
		global flightNum1
		global flightNum2
		global fareType1
		global fareType2
		global flightNumFlag
		global strongFlag
		global tdFlag
		global fareTypeFlag
		data = data.strip()
		if data:
			# print "Data     :", data
			# Departure of 1st flight (city)
			if departureCityFlag and strongFlag and not roundTripFlag:
				pos1 = data.find("(")
				pos2 = data.find(")", pos1)
				departureCityCode1 = data[(pos1+1):(pos2)]
				departureCity1 = data.replace("(","- ")
				departureCity1 = departureCity1.strip(')')
				departureCityFlag = False
			# Departure of 1st flight (date)
			elif departureDateFlag and tdFlag and not roundTripFlag:
				departureDate1 = data
				departureDateFlag = False
			# Departure of 1st flight (time)
			elif departureTimeFlag and strongFlag and not roundTripFlag:
				departureTime1 = data
				departureTimeFlag = False
			# Arrival of 1st flight (city)
			elif arrivalCityFlag and strongFlag and not roundTripFlag:
				pos1 = data.find("(")
				pos2 = data.find(")", pos1)
				arrivalCityCode1 = data[(pos1+1):(pos2)]
				arrivalCity1 = data.replace("(","- ")
				arrivalCity1 = arrivalCity1.strip(')')
				arrivalCityFlag = False
			# Arrival of 1st flight (time)
			elif arrivalTimeFlag and strongFlag and not roundTripFlag:
				arrivalTime1 = data
				arrivalTimeFlag = False
			# Flight number of 1st flight
			elif flightNumFlag and strongFlag and not roundTripFlag:
				flightNum1 = data.strip('#')
				flightNumFlag = False
			# Departure of 2nd flight (city)
			elif departureCityFlag and strongFlag and roundTripFlag:
				pos1 = data.find("(")
				pos2 = data.find(")", pos1)
				departureCityCode2 = data[(pos1+1):(pos2)]
				departureCity2 = data.replace("(","- ")
				departureCity2 = departureCity2.strip(')')
				departureCityFlag = False
			# Departure of 2nd flight (date)
			elif departureDateFlag and tdFlag and roundTripFlag:
				departureDate2 = data
				departureDateFlag = False
			# Departure of 2nd flight (date)
			elif departureTimeFlag and strongFlag and roundTripFlag:
				departureTime2 = data
				departureTimeFlag = False
			# Arrival of 2nd flight (city)
			elif arrivalCityFlag and strongFlag and roundTripFlag:
				pos1 = data.find("(")
				pos2 = data.find(")", pos1)
				arrivalCityCode2 = data[(pos1+1):(pos2)]
				arrivalCity2 = data.replace("(","- ")
				arrivalCity2 = arrivalCity2.strip(')')
				arrivalCityFlag = False
			# Arrival of 2nd flight (time)
			elif arrivalTimeFlag and strongFlag and roundTripFlag:
				arrivalTime2 = data
				arrivalTimeFlag = False
			# Flight number of 2nd flight
			elif flightNumFlag and strongFlag and roundTripFlag:
				flightNum2 = data.strip('#')
				flightNumFlag = False
			elif "Depart" in data:
				departureCityFlag = True
			elif "Arrive in" in data:
				arrivalCityFlag = True
			elif "Flight" in data:
				flightNumFlag = True
			elif fareTypeFlag and not roundTripFlag:
				fareType1 = data
				fareTypeFlag = False
				roundTripFlag = True
			elif fareTypeFlag and roundTripFlag:
				fareTypeFlag = False
				fareType2 = data
			elif "errors" in data:
				errorFlag = True
			else:
				departureCityFlag = False
				departureDateFlag = False
				departureTimeFlag = False
				arrivalCityFlag = False
				arrivalTimeFlag = False
				flightNumFlag = False

#####################################################################
## Set user input variables
#####################################################################
# try:
confirmationNum = sys.argv[1]
firstName = sys.argv[2]
lastName = sys.argv[3]

print "%s\n%s\n%s\n" % (confirmationNum,firstName,lastName)
# except:
#     print "ERROR"
#     sys.exit(1)

# # Generate some data to send to PHP
# result = {'status': 'Yes!'}

# # Send it to stdout (to PHP)
# print json.dumps(result)

departureDate1 = ""
departureCity1 = ""
departureTime1 = ""
departureDate2 = ""
departureCity2 = ""
departureTime2 = ""
arrivalCity1 = ""
arrivalTime1 = ""
arrivalCity2 = ""
arrivalTime2 = ""
flightNum1 = ""
flightNum2 = ""
fareType1 = ""
fareType2 = ""
currentDollarsPrice = ""
currentPointsPrice = ""
departureCityCode1 = ""
departureCityCode2 = ""
arrivalCityCode1 = ""
arrivalCityCode2 = ""
departureDateFlag = False
departureCityFlag = False
departureTimeFlag = False
arrivalCityFlag = False
arrivalTimeFlag = False
flightNumFlag = False
strongFlag = False
tdFlag = False
fareTypeFlag = False
roundTripFlag = False
errorFlag = False
existFlag = False

#####################################################################
## Initiate mechanize, set parameters in form, and submit form
#####################################################################
cwd = os.getcwd()
resultsFile = cwd+"/southwest_conf_results.html"
responseFile = cwd+"/southwest_conf_response.html"

#####################################################################
## Check if flight information exists in DB
#####################################################################
db = MySQLdb.connect("127.0.0.1","root","swfarereducer","SWFAREREDUCERDB")
cursor = db.cursor()
sql = "SELECT * FROM SWFAREREDUCERDB.UPCOMING_FLIGHTS WHERE CONFIRMATION_NUM='%s' AND FIRST_NAME='%s' AND LAST_NAME='%s' ORDER BY DEPART_DATE ASC" % (confirmationNum,firstName,lastName)
try:
	cursor.execute(sql)
	if cursor.rowcount > 0:
		existFlag = True
	else:
		existFlag = False
except:
	print "ERROR: Unable to fetch flight info with Conf #, first & last name"

db.close()

####################################################################
# If flight information does not exist in DB, retrieve flight 
# information
####################################################################
# if not existFlag:
try:
	# proxy = urllib2.ProxyHandler({'http': '127.0.0.1'})
	# opener = urllib2.build_opener(proxy)
	# urllib2.install_opener(opener)
	# urllib2.urlopen('https://www.southwest.com/flight/change-air-reservation.html')
	br = mechanize.Browser()
	br.set_handle_robots(False)
	response = br.open("https://www.southwest.com/flight/change-air-reservation.html")
	# content = response.read()
	# with open(responseFile, "w") as f:
	#     f.write(content)
	br.select_form(predicate=lambda f: f.attrs.get('id', None) == 'reservationLookupCriteria')
	br.find_control(name="confirmationNumber").value = confirmationNum
	br.find_control(name="firstName").value = firstName
	br.find_control(name="lastName").value = lastName
	try:
		result = br.submit()
		southwest_conf_results_string = result.read()
		# with open(resultsFile, "w") as f:
		# 	f.write(southwest_conf_results_string)
	except:
		print "ERROR: Could not submit information "
		sys.exit(1)
# except mechanize.URLError as e:
# 	# print e.code
# 	print e
# 	print "ERROR: Could not connect to browser\n"
# 	sys.exit(1)

except mechanize.HTTPError as e:
	print "ERROR: Could not connect to browser\n"
	print e.code
	print e.reason.args
	sys.exit(1)

# print "2"
# with open(resultsFile, "r") as f:
# 	southwest_conf_results_string = f.read()
parser = MyHTMLParser()
parser.feed(southwest_conf_results_string)
# print "3"

if departureCity1:
	temp = datetime.datetime.strptime(departureDate1, "%A, %B %d, %Y")
	departureDate1 = temp.strftime("%m/%d/%Y")
	print "Departure Code: " + departureCityCode1
	print "Departure City: " + departureCity1
	print "Arrival Code  : " + arrivalCityCode1
	print "Arrival City  : " + arrivalCity1
	print "Departure Date: " + departureDate1
	print "Departure Time: " + departureTime1
	print "Arrival Time  : " + arrivalTime1
	print "Flight #      : " + flightNum1
	print "Fare Type     : " + fareType1

	db = MySQLdb.connect("127.0.0.1","root","swfarereducer","SWFAREREDUCERDB")
	cursor = db.cursor()
	sql = "INSERT INTO SWFAREREDUCERDB.UPCOMING_FLIGHTS(CONFIRMATION_NUM,FIRST_NAME,LAST_NAME,DEPART_AIRPORT_CODE,ARRIVE_AIRPORT_CODE,DEPART_DATE,DEPART_TIME,ARRIVE_TIME,FLIGHT_NUM,FARE_TYPE) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (confirmationNum,firstName,lastName,departureCityCode1,arrivalCityCode1,departureDate1,departureTime1,arrivalTime1,flightNum1,fareType1)
	try:
		cursor.execute(sql)
		db.commit()
	except:
		db.rollback()
		print "ERROR: Unable to insert new flight info"
	db.close()

if departureCity2:
	# print ""
	temp = datetime.datetime.strptime(departureDate2, "%A, %B %d, %Y")
	departureDate2 = temp.strftime("%m/%d/%Y")
	# print "Departure Code: " + departureCityCode2
	# print "Departure City: " + departureCity2
	# print "Arrival Code  : " + arrivalCityCode2
	# print "Arrival City  : " + arrivalCity2
	# print "Departure Date: " + departureDate2
	# print "Departure Time: " + departureTime2
	# print "Arrival Time  : " + arrivalTime2
	# print "Flight #      : " + flightNum2
	# print "Fare Type     : " + fareType2

	db = MySQLdb.connect("127.0.0.1","root","swfarereducer","SWFAREREDUCERDB")
	cursor = db.cursor()
	sql = "INSERT INTO SWFAREREDUCERDB.UPCOMING_FLIGHTS(CONFIRMATION_NUM,FIRST_NAME,LAST_NAME,DEPART_AIRPORT_CODE,ARRIVE_AIRPORT_CODE,DEPART_DATE,DEPART_TIME,ARRIVE_TIME,FLIGHT_NUM,FARE_TYPE) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (confirmationNum,firstName,lastName,departureCityCode2,arrivalCityCode2,departureDate2,departureTime2,arrivalTime2,flightNum2,fareType2)
	try:
		cursor.execute(sql)
		db.commit()
	except:
		db.rollback()
		print "ERROR: Unable to insert new flight info"
	db.close()
# else:
# 	print existFlag