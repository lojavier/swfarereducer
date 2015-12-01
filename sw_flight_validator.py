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

class MyHTMLParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		global departDateFlag
		global departCityFlag
		global departTimeFlag
		global arriveCityFlag
		global arriveTimeFlag
		global strongFlag
		global tdFlag
		global fareTypeFlag
		if "span" in tag:
			for attr in attrs:
				if "class" in attr[0] and "summary-travel-date" in attr[1]:
					departDateFlag = True
				if "class" in attr[0] and "nowrap" in attr[1] and "nextDayContainer" not in attr[1]:
					departTimeFlag = True
				if "class" in attr[0] and "nextDayContainer" in attr[1]:
					arriveTimeFlag = True
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
		global departAirportCode1
		global departCity1
		global departDate1
		global departTime1
		global departAirportCode2
		global departCity2
		global departDate2
		global departTime2
		global departCityFlag
		global departDateFlag
		global departTimeFlag
		global arriveAirportCode1
		global arriveCity1
		global arriveTime1
		global arriveAirportCode2
		global arriveCity2
		global arriveTime2
		global arriveCityFlag
		global arriveTimeFlag
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
			# Departure of 1st flight (city)
			if departCityFlag and strongFlag and not roundTripFlag:
				pos1 = data.find("(")
				pos2 = data.find(")", pos1)
				departAirportCode1 = data[(pos1+1):(pos2)]
				departCity1 = data.replace("(","- ")
				departCity1 = departCity1.strip(')')
				departCityFlag = False
				print departAirportCode1
			# Departure of 1st flight (date)
			elif departDateFlag and tdFlag and not roundTripFlag:
				temp = datetime.datetime.strptime(data, "%A, %B %d, %Y")
				departDate1 = temp.strftime("%Y-%m-%d")
				departDateFlag = False
				print departDate1
			# Departure of 1st flight (time)
			elif departTimeFlag and strongFlag and not roundTripFlag:
				temp = datetime.datetime.strptime(data, "%I:%M %p")
				departTime1 = temp.strftime("%H:%M:%S")
				departTimeFlag = False
				print departTime1
			# Arrival of 1st flight (city)
			elif arriveCityFlag and strongFlag and not roundTripFlag:
				pos1 = data.find("(")
				pos2 = data.find(")", pos1)
				arriveAirportCode1 = data[(pos1+1):(pos2)]
				arriveCity1 = data.replace("(","- ")
				arriveCity1 = arriveCity1.strip(')')
				arriveCityFlag = False
				print arriveAirportCode1
			# Arrival of 1st flight (time)
			elif arriveTimeFlag and strongFlag and not roundTripFlag:
				temp = datetime.datetime.strptime(data, "%I:%M %p")
				arriveTime1 = temp.strftime("%H:%M:%S")
				arriveTimeFlag = False
				print arriveTime1
			# Flight number of 1st flight
			elif flightNumFlag and strongFlag and not roundTripFlag:
				flightNum1 = data.replace('#','')
				flightNumFlag = False
				print flightNum1
			# Departure of 2nd flight (city)
			elif departCityFlag and strongFlag and roundTripFlag:
				pos1 = data.find("(")
				pos2 = data.find(")", pos1)
				departAirportCode2 = data[(pos1+1):(pos2)]
				departCity2 = data.replace("(","- ")
				departCity2 = departCity2.strip(')')
				departCityFlag = False
				print departAirportCode2
			# Departure of 2nd flight (date)
			elif departDateFlag and tdFlag and roundTripFlag:
				temp = datetime.datetime.strptime(data, "%A, %B %d, %Y")
				departDate2 = temp.strftime("%Y-%m-%d")
				departDateFlag = False
				print departDate2
			# Departure of 2nd flight (date)
			elif departTimeFlag and strongFlag and roundTripFlag:
				temp = datetime.datetime.strptime(data, "%I:%M %p")
				departTime2 = temp.strftime("%H:%M:%S")
				departTimeFlag = False
				print departTime2
			# Arrival of 2nd flight (city)
			elif arriveCityFlag and strongFlag and roundTripFlag:
				pos1 = data.find("(")
				pos2 = data.find(")", pos1)
				arriveAirportCode2 = data[(pos1+1):(pos2)]
				arriveCity2 = data.replace("(","- ")
				arriveCity2 = arriveCity2.strip(')')
				arriveCityFlag = False
				print arriveAirportCode2
			# Arrival of 2nd flight (time)
			elif arriveTimeFlag and strongFlag and roundTripFlag:
				temp = datetime.datetime.strptime(data, "%I:%M %p")
				arriveTime2 = temp.strftime("%H:%M:%S")
				arriveTimeFlag = False
				print arriveTime2
			# Flight number of 2nd flight
			elif flightNumFlag and strongFlag and roundTripFlag:
				flightNum2 = data.replace('#','')
				flightNumFlag = False
				print flightNum2
			elif "Depart" in data:
				departCityFlag = True
			elif "Arrive in" in data:
				arriveCityFlag = True
			elif "Flight" in data:
				flightNumFlag = True
			elif fareTypeFlag and not roundTripFlag:
				fareType1 = data
				fareTypeFlag = False
				roundTripFlag = True
				print fareType1
				print ""
			elif fareTypeFlag and roundTripFlag:
				fareTypeFlag = False
				fareType2 = data
				print fareType2
				print ""
			elif "errors" in data:
				errorFlag = True
			else:
				departCityFlag = False
				departDateFlag = False
				departTimeFlag = False
				arriveCityFlag = False
				arriveTimeFlag = False
				flightNumFlag = False

#####################################################################
## Set user input variables
#####################################################################
confirmationNum = (sys.argv[1]).upper()
firstName = (sys.argv[2]).upper()
lastName = (sys.argv[3]).upper()

data = {}
departDate1 = ""
departCity1 = ""
departTime1 = ""
departDate2 = ""
departCity2 = ""
departTime2 = ""
arriveCity1 = ""
arriveTime1 = ""
arriveCity2 = ""
arriveTime2 = ""
flightNum1 = ""
flightNum2 = ""
fareType1 = ""
fareType2 = ""
currentDollarsPrice = ""
currentPointsPrice = ""
departAirportCode1 = ""
departAirportCode2 = ""
arriveAirportCode1 = ""
arriveAirportCode2 = ""
departDateFlag = False
departCityFlag = False
departTimeFlag = False
arriveCityFlag = False
arriveTimeFlag = False
flightNumFlag = False
strongFlag = False
tdFlag = False
fareTypeFlag = False
roundTripFlag = False
errorFlag = False

#####################################################################
## Set directory path and file name for response & results html file
#####################################################################
cwd = os.getcwd()
responseFile = cwd+"/logs/lookup-air-reservation.html"
resultsFile = cwd+"/logs/view-air-reservation.html"
logFile = cwd+"/logs/"+time.strftime("%Y_%m_%d")+"_sw_flight_validator.log"

def main():
	#####################################################################
	## Check if flight information exists in DB
	#####################################################################
	db = MySQLdb.connect("127.0.0.1","root","swfarereducer","SWFAREREDUCERDB")
	cursor = db.cursor()
	sql = "SELECT COUNT(*) FROM RESERVED_FLIGHTS WHERE CONFIRMATION_NUM='%s' AND FIRST_NAME='%s' AND LAST_NAME='%s'" % (confirmationNum,firstName,lastName)
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

	####################################################################
	# If flight information does not exist in DB, retrieve flight 
	# information
	####################################################################
	try:
		br = mechanize.Browser()
		br.set_handle_robots(False)
		br.set_handle_refresh(False)
		response = br.open("https://www.southwest.com/flight/lookup-air-reservation.html")
		responseContent = response.read()
		with open(responseFile, "w") as f:
		    f.write(responseContent)
		# br.select_form(predicate=lambda f: f.attrs.get('id', None) == 'pnrFriendlyLookup_check_form')
		formcount=0
		for form in br.forms():
			if str(form.attrs.get('id')) == "pnrFriendlyLookup_check_form":
				break
			formcount=formcount+1
		br.select_form(nr=formcount)
		br.find_control(id="pnrFriendlyLookup_option_confirmationNumber",name="searchType").value = ['ConfirmationNumber']
		br.find_control(name="confirmationNumberFirstName").value = firstName
		br.find_control(name="confirmationNumberLastName").value = lastName
		br.find_control(name="confirmationNumber").value = confirmationNum
		results = br.submit()
		resultsContent = results.read()
		with open(resultsFile, "w") as f:
			f.write(resultsContent)
	except:
		print "ERROR: Could not connect to browser\n"
		logF = open(logFile, "a")
		logMessage = "%s ERROR: Unable to lookup reservation [confirmationNum:%s|firstName:%s|lastName:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),confirmationNum,firstName,lastName)
		logF.write(logMessage)
		logF.close()
		db.close()
		sys.exit(1)

	parser = MyHTMLParser()
	parser.feed(resultsContent)

	if departCity1 and departCity2:
		# First flight
		sql = "SELECT UPCOMING_FLIGHT_ID FROM UPCOMING_FLIGHTS WHERE DEPART_AIRPORT_CODE='%s' AND ARRIVE_AIRPORT_CODE='%s' AND DEPART_DATE_TIME='%s %s' AND FLIGHT_NUM='%s'" % (departAirportCode1,arriveAirportCode1,departDate1,departTime1,flightNum1)
		try:
			cursor.execute(sql)
			upcomingFlightID = cursor.fetchone()[0]
		except:
			logF = open(logFile, "a")
			logMessage = "%s ERROR: Unable to check upcoming flights [depart:%s|arrive:%s|date/time:%s %s|flight:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),departAirportCode1,arriveAirportCode1,departDate1,departTime1,flightNum1)
			logF.write(logMessage)
			logF.close()
			db.close()
			sys.exit(1)

		sql = "INSERT INTO RESERVED_FLIGHTS (CONFIRMATION_NUM,FIRST_NAME,LAST_NAME,UPCOMING_FLIGHT_ID,FARE_TYPE) VALUES ('%s','%s','%s','%s','%s')" % (confirmationNum,firstName,lastName,upcomingFlightID,fareType1)
		try:
			cursor.execute(sql)
			db.commit()
		except:
			db.rollback()
			logF = open(logFile, "a")
			logMessage = "%s ERROR: Unable to insert reserved flight [confirmationNum:%s|firstName:%s|lastName:%s|upcomingFlightID:%s|fareType:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),confirmationNum,firstName,lastName,upcomingFlightID,fareType1)
			logF.write(logMessage)
			logF.close()
			db.close()
			sys.exit(1)

		# Second flight
		sql = "SELECT UPCOMING_FLIGHT_ID FROM UPCOMING_FLIGHTS WHERE DEPART_AIRPORT_CODE='%s' AND ARRIVE_AIRPORT_CODE='%s' AND DEPART_DATE_TIME='%s %s' AND FLIGHT_NUM='%s'" % (departAirportCode2,arriveAirportCode2,departDate2,departTime2,flightNum2)
		try:
			cursor.execute(sql)
			upcomingFlightID = cursor.fetchone()[0]
		except:
			logF = open(logFile, "a")
			logMessage = "%s ERROR: Unable to check upcoming flights [depart:%s|arrive:%s|date/time:%s %s|flight:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),departAirportCode2,arriveAirportCode2,departDate2,departTime2,flightNum2)
			logF.write(logMessage)
			logF.close()
			db.close()
			sys.exit(1)

		sql = "INSERT INTO RESERVED_FLIGHTS (CONFIRMATION_NUM,FIRST_NAME,LAST_NAME,UPCOMING_FLIGHT_ID,FARE_TYPE) VALUES ('%s','%s','%s','%s','%s')" % (confirmationNum,firstName,lastName,upcomingFlightID,fareType2)
		try:
			cursor.execute(sql)
			db.commit()
		except:
			db.rollback()
			logF = open(logFile, "a")
			logMessage = "%s ERROR: Unable to insert reserved flight [confirmationNum:%s|firstName:%s|lastName:%s|upcomingFlightID:%s|fareType:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),confirmationNum,firstName,lastName,upcomingFlightID,fareType2)
			logF.write(logMessage)
			logF.close()
			db.close()
			sys.exit(1)

	elif departCity1 and not departCity2:
		# First flight
		sql = "SELECT UPCOMING_FLIGHT_ID FROM UPCOMING_FLIGHTS WHERE DEPART_AIRPORT_CODE='%s' AND ARRIVE_AIRPORT_CODE='%s' AND DEPART_DATE_TIME='%s %s' AND FLIGHT_NUM='%s'" % (departAirportCode1,arriveAirportCode1,departDate1,departTime1,flightNum1)
		try:
			cursor.execute(sql)
			upcomingFlightID = cursor.fetchone()[0]
		except:
			logF = open(logFile, "a")
			logMessage = "%s ERROR: Unable to check upcoming flights [depart:%s|arrive:%s|date/time:%s %s|flight:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),departAirportCode1,arriveAirportCode1,departDate1,departTime1,flightNum1)
			logF.write(logMessage)
			logF.close()
			db.close()
			sys.exit(1)

		sql = "INSERT INTO RESERVED_FLIGHTS (CONFIRMATION_NUM,FIRST_NAME,LAST_NAME,UPCOMING_FLIGHT_ID,FARE_TYPE) VALUES ('%s','%s','%s','%s','%s')" % (confirmationNum,firstName,lastName,upcomingFlightID,fareType1)
		try:
			cursor.execute(sql)
			db.commit()
		except:
			db.rollback()
			logF = open(logFile, "a")
			logMessage = "%s ERROR: Unable to insert reserved flight [confirmationNum:%s|firstName:%s|lastName:%s|upcomingFlightID:%s|fareType:%s]\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),confirmationNum,firstName,lastName,upcomingFlightID,fareType1)
			logF.write(logMessage)
			logF.close()
			db.close()
			sys.exit(1)

	elif not departCity2 and not departCity1:
		print "No flight exists"

	db.close()

main()